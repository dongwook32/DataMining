"""폴백 BERTopic. NMF 본분석은 바꾸지 않는다.

  python -m analysis.fallback_bertopic

같은 `doc_term.npz` 어휘로 문서를 만들고(등장 어휘를 공백으로 이음),
월별 무작위 층화표본에 BERTopic을 적합한다. 임베딩 전량 변환(93만)은
돌리지 않는다. 월별 비중은 그 표본에서만 집계한다. NMF/LDA가 전량
변환인 것과 다르므로 QC에 적는다.

토픽 수 상한은 NMF와 같은 14. 매핑 규칙은 키워드 질량과 같고 수동
덮어쓰기는 없다. 반응은 `data/processed/reactions_bertopic`에 다시 쓴다.

산출:
  data/processed/regimes_bertopic/
  data/processed/reactions_bertopic/
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd
from scipy import sparse

from analysis.detect_regimes import (
    CP_MIN_SIZE,
    detect_changepoints,
    drop_empty,
    fold_regimes,
    load_inputs,
    map_topics,
    monthly_topic_share,
    sha256_file,
    stratified_indices,
    topic_terms_table,
)
from analysis.measure_reactions import analyze, join_regime_panel
from config import load_config, project_root

ROOT = project_root()
MATRIX_PATH = ROOT / "data" / "processed" / "corpus" / "doc_term.npz"
OUT_DIR = ROOT / "data" / "processed" / "regimes_bertopic"
REACT_DIR = ROOT / "data" / "processed" / "reactions_bertopic"

H_PATH = OUT_DIR / "bertopic_H.npy"
TERMS_PATH = OUT_DIR / "topic_terms.csv"
TOPIC_SHARE_PATH = OUT_DIR / "topic_monthly_share.csv"
MAP_PATH = OUT_DIR / "topic_regime_map.csv"
REGIME_PATH = OUT_DIR / "regime_monthly.csv"
CP_PATH = OUT_DIR / "changepoints.csv"
QC_PATH = OUT_DIR / "regimes_qc.md"
META_PATH = OUT_DIR / "bertopic_meta.json"
ASSIGN_PATH = OUT_DIR / "sample_assignments.csv"

# NMF/LDA 적합 표본은 월 3,000. 임베딩은 그보다 비싸서 기본은 월 1,000.
# 월 격자(67)는 같고, 달은 무작위 층화라 앞부분 절단은 아니다.
DEFAULT_PER_MONTH = 1000
EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
MIN_TOPIC_SIZE = 40


def sparse_to_texts(X: sparse.csr_matrix, vocab: list[str]) -> list[str]:
    """행마다 등장 어휘를 공백으로 잇는다. 본문이 아니라 행렬과 같은 어휘다."""
    X = X.tocsr()
    indptr, indices = X.indptr, X.indices
    texts = []
    for i in range(X.shape[0]):
        js = indices[indptr[i] : indptr[i + 1]]
        texts.append(" ".join(vocab[j] for j in js))
    return texts


def h_from_bertopic(model, vocab: list[str], topic_ids: list[int]) -> np.ndarray:
    """c-TF-IDF 상위 어휘 점수를 어휘 열에 올려 NMF/LDA 와 같은 매핑에 쓴다."""
    pos = {t: j for j, t in enumerate(vocab)}
    H = np.zeros((len(topic_ids), len(vocab)), dtype=np.float64)
    for row, tid in enumerate(topic_ids):
        words = model.get_topic(tid)
        if not words:
            continue
        for term, score in words:
            j = pos.get(str(term))
            if j is not None and float(score) > 0:
                H[row, j] = float(score)
    return H


def assignment_shares(topics: np.ndarray, topic_ids: list[int]) -> tuple[np.ndarray, np.ndarray]:
    """하드 배정 원핫. -1(이상치)과 축소에서 빠진 id 는 행합 0."""
    id_to_col = {tid: k for k, tid in enumerate(topic_ids)}
    W = np.zeros((len(topics), len(topic_ids)), dtype=np.float64)
    for i, t in enumerate(topics):
        col = id_to_col.get(int(t))
        if col is not None:
            W[i, col] = 1.0
    ok = W.sum(axis=1) > 0
    return W, ok


def write_qc(
    *,
    mapping: pd.DataFrame,
    topic_share: pd.DataFrame,
    regimes: pd.DataFrame,
    cps: pd.DataFrame,
    n_sample: int,
    n_outlier: int,
    n_topics: int,
    fit_s: float,
    embed_s: float,
    matrix_hash: str,
    labels: list[str],
    per_month: int,
    random_state: int,
    embed_model: str,
    n_iter_note: str,
) -> None:
    lines: list[str] = []
    add = lines.append
    add("# 폴백 BERTopic 국면 점검")
    add("")
    add(f"생성: `analysis.fallback_bertopic` · {pd.Timestamp.now():%Y-%m-%d %H:%M}")
    add("")
    add("이 산출은 NMF 본분석을 대체하지 않는다. 월별 비중은 층화표본에서만")
    add("집계했다. NMF/LDA의 전량 변환과 다르다.")
    add("")
    add("## 1. 입력·적합")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 행렬 | `{MATRIX_PATH.relative_to(ROOT).as_posix()}` |")
    add(f"| 행렬 sha256 | `{matrix_hash}` |")
    add("| 문서 표현 | 행렬에 등장한 어휘를 공백으로 이은 문자열 (본문 아님) |")
    add(f"| 임베딩 | `{embed_model}` |")
    add(f"| 적합·시계열 표본 | {n_sample:,}건 (월당 최대 {per_month:,}, seed {random_state}) |")
    add(f"| 이상치(-1) | {n_outlier:,}건 ({n_outlier / n_sample:.3f}) |")
    add(f"| 토픽 수 (이상치 제외) | {n_topics} |")
    add(f"| 임베딩 시간 | {embed_s:.1f}s |")
    add(f"| 적합 합계 | {fit_s:.1f}s |")
    add(f"| 비고 | {n_iter_note} |")
    add("| 전량 변환 | 안 함 |")
    add("| 수동 덮어쓰기 | 없음 |")
    add("")
    add("## 2. 토픽 → 국면")
    add("")
    add("| 토픽 | 국면 | 질량 점유 | 차순위 | 상위 어휘 |")
    add("|------|------|-----------|--------|-----------|")
    for _, r in mapping.iterrows():
        add(f"| {int(r['topic'])} | {r['regime']} | {r['score_share']:.3f} | "
            f"{r['second_regime']} | {r['top_terms'][:80]} |")
    add("")
    missing = [r for r in labels if r not in set(mapping["regime"])]
    add("매핑에서 빠진 국면: " + (", ".join(missing) if missing else "없음"))
    add("")
    add("## 3. z-우세 개월 (표본 시계열)")
    add("")
    add("| 국면 | 개월 |")
    add("|------|------|")
    counts = regimes["dominant_regime"].value_counts()
    for r in labels:
        add(f"| {r} | {int(counts.get(r, 0))} |")
    add("")
    add("## 4. 변화점")
    add("")
    if cps.empty:
        add("전환 없음.")
    else:
        add("| 신호 | 전환월 | 이전 | 이후 |")
        add("|------|--------|------|------|")
        for _, r in cps.iterrows():
            add(f"| {r['signal']} | {r['cp_month']} | {r['from_label']} | {r['to_label']} |")
    add("")
    add(f"최소 구간 {CP_MIN_SIZE}개월. 페널티는 NMF와 같은 `dim × ln(n)`.")
    add("")
    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_bertopic(
    n_topics: int,
    random_state: int,
    per_month: int,
    embed_model_name: str,
    min_topic_size: int,
) -> dict:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer

    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("행렬 로드 (BERTopic)", flush=True)
    X, docs, vocab = load_inputs()
    X, docs, n_drop = drop_empty(X, docs)
    print(f"  빈 문서 {n_drop}건 제외 → {X.shape[0]:,}", flush=True)

    months_arr = docs["month"].to_numpy()
    fit_idx = stratified_indices(months_arr, per_month, random_state)
    print(f"  표본 {len(fit_idx):,}건 (월당 최대 {per_month:,}, seed {random_state})", flush=True)

    t0 = time.perf_counter()
    texts = sparse_to_texts(X[fit_idx], vocab)
    print(f"  텍스트 {len(texts):,}건 · {time.perf_counter() - t0:.1f}s", flush=True)

    t1 = time.perf_counter()
    embed_model = SentenceTransformer(embed_model_name)
    embeddings = embed_model.encode(
        texts,
        show_progress_bar=True,
        batch_size=64,
    )
    embed_s = time.perf_counter() - t1
    print(f"  임베딩 {embed_s:.1f}s · shape {getattr(embeddings, 'shape', None)}", flush=True)

    t2 = time.perf_counter()
    model = BERTopic(
        embedding_model=embed_model,
        nr_topics=n_topics,
        min_topic_size=min_topic_size,
        calculate_probabilities=False,
        verbose=True,
    )
    topics, _ = model.fit_transform(texts, embeddings=embeddings)
    topics = np.asarray(topics)
    fit_s = time.perf_counter() - t1
    print(f"  BERTopic.fit {time.perf_counter() - t2:.1f}s · 합계 {fit_s:.1f}s", flush=True)

    topic_ids = sorted(int(t) for t in set(topics.tolist()) if t != -1)
    n_outlier = int((topics == -1).sum())
    print(f"  토픽 {len(topic_ids)}개 · 이상치 {n_outlier:,}", flush=True)
    if not topic_ids:
        raise RuntimeError("BERTopic이 이상치만 남겼다. min_topic_size 를 낮춰야 한다.")

    H = h_from_bertopic(model, vocab, topic_ids)
    W, ok = assignment_shares(topics, topic_ids)
    sample_months = months_arr[fit_idx]
    topic_share = monthly_topic_share(W, sample_months, ok)
    n_docs = (
        pd.DataFrame({"month": sample_months})
        .groupby("month").size().rename("n_docs")
    )

    mapping = map_topics(H, vocab, labels, overrides={})
    # map_topics 는 행 번호 0..K-1 을 topic 으로 쓴다. BERTopic id 와 다를 수 있어 열을 남긴다.
    mapping = mapping.copy()
    mapping["bertopic_id"] = [topic_ids[int(t)] for t in mapping["topic"]]
    terms = topic_terms_table(H, vocab)
    regimes = fold_regimes(topic_share, mapping, n_docs, labels, slugs)

    months = [str(m) for m in topic_share.index]
    topic_cols = [c for c in topic_share.columns if c.startswith("topic_")]
    slug_order = [slugs[r] for r in labels]
    topic_names = [
        str(mapping.loc[mapping["topic"] == k, "regime"].iloc[0]) for k in range(len(topic_cols))
    ]
    cps_topics = detect_changepoints(
        topic_share[topic_cols].to_numpy(), months, topic_names, "topics",
    )
    cps_regimes = detect_changepoints(
        regimes[[f"share_{s}" for s in slug_order]].to_numpy(), months, labels, "regimes",
    )
    cps = pd.concat([cps_topics, cps_regimes], ignore_index=True)

    np.save(H_PATH, H)
    topic_share.index.name = "month"
    topic_share.to_csv(TOPIC_SHARE_PATH, encoding="utf-8-sig")
    terms.to_csv(TERMS_PATH, index=False, encoding="utf-8-sig")
    mapping.to_csv(MAP_PATH, index=False, encoding="utf-8-sig")
    regimes.to_csv(REGIME_PATH, index=False, encoding="utf-8-sig")
    cps.to_csv(CP_PATH, index=False, encoding="utf-8-sig")
    pd.DataFrame({
        "month": sample_months,
        "bertopic_id": topics,
    }).to_csv(ASSIGN_PATH, index=False, encoding="utf-8-sig")

    import bertopic as _bt
    import sentence_transformers as _st

    META_PATH.write_text(json.dumps({
        "method": "bertopic",
        "n_sample": int(len(fit_idx)),
        "n_outlier": n_outlier,
        "n_topics": len(topic_ids),
        "topic_ids": topic_ids,
        "fit_s": fit_s,
        "embed_s": embed_s,
        "per_month": per_month,
        "random_state": random_state,
        "embed_model": embed_model_name,
        "min_topic_size": min_topic_size,
        "nr_topics_request": n_topics,
        "full_transform": False,
        "bertopic": getattr(_bt, "__version__", ""),
        "sentence_transformers": getattr(_st, "__version__", ""),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    write_qc(
        mapping=mapping, topic_share=topic_share, regimes=regimes, cps=cps,
        n_sample=len(fit_idx), n_outlier=n_outlier, n_topics=len(topic_ids),
        fit_s=fit_s, embed_s=embed_s, matrix_hash=sha256_file(MATRIX_PATH),
        labels=labels, per_month=per_month, random_state=random_state,
        embed_model=embed_model_name,
        n_iter_note="시계열=층화표본 하드배정. 전량 변환 없음.",
    )

    print("\n=== BERTopic 국면 ===")
    print(regimes["dominant_regime"].value_counts().to_string())
    print(f"변화점 {len(cps)}건")
    print(f"월별 → {REGIME_PATH}")
    print(f"QC   → {QC_PATH}")
    return {"regimes": regimes, "cps": cps, "mapping": mapping}


def run_fallback_reactions() -> dict:
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    df = join_regime_panel(REGIME_PATH, labels)
    cps = pd.read_csv(CP_PATH, dtype={"cp_month": str})
    return analyze(
        df, cps, labels, slugs, REACT_DIR,
        qc_title="폴백 BERTopic 국면별 반응 분석 점검",
    )


def main() -> None:
    cfg = load_config()
    tm = cfg["topic_model"]
    p = argparse.ArgumentParser(description="폴백 BERTopic (본분석 NMF는 유지)")
    p.add_argument("--topics", type=int, default=int(tm["n_topics"]))
    p.add_argument("--seed", type=int, default=int(tm["random_state"]))
    p.add_argument("--per-month", type=int, default=DEFAULT_PER_MONTH)
    p.add_argument("--embed-model", default=EMBED_MODEL)
    p.add_argument("--min-topic-size", type=int, default=MIN_TOPIC_SIZE)
    p.add_argument("--skip-reactions", action="store_true")
    a = p.parse_args()

    run_bertopic(a.topics, a.seed, a.per_month, a.embed_model, a.min_topic_size)
    if not a.skip_reactions:
        run_fallback_reactions()


if __name__ == "__main__":
    main()
