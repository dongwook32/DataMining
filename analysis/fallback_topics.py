"""폴백 토픽 모형: 본분석 반응 차이가 약할 때만 LDA (선택 BERTopic).

  python -m analysis.fallback_topics
  python -m analysis.fallback_topics --method lda

NMF 본분석은 바꾸지 않는다. 이 모듈은 같은 `doc_term.npz`에 LDA를 적합하고,
같은 키워드 질량 매핑·z-우세 라벨·PELT를 적용해 국면 시계열을 하나 더 만든다.
반응표는 `measure_reactions.analyze`가 `data/processed/reactions_lda`에 다시 쓴다.

BERTopic은 임베딩 스택이 필요하다. 설치되어 있지 않으면 건너뛰고 이유를 기록한다.
본분석 경로에 BERTopic을 끼워 넣지 않는다.

산출 (LDA):
  data/processed/regimes_lda/  (NMF regimes/ 와 같은 스키마)
  data/processed/reactions_lda/ (반응 재추정)
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import LatentDirichletAllocation

from analysis.detect_regimes import (
    CP_MIN_SIZE,
    FIT_PER_MONTH,
    detect_changepoints,
    drop_empty,
    fold_regimes,
    load_inputs,
    map_topics,
    monthly_topic_share,
    row_shares,
    sha256_file,
    stratified_indices,
    topic_terms_table,
)
from analysis.measure_reactions import analyze, join_regime_panel
from config import load_config, project_root

ROOT = project_root()
MATRIX_PATH = ROOT / "data" / "processed" / "corpus" / "doc_term.npz"
OUT_DIR = ROOT / "data" / "processed" / "regimes_lda"
REACT_DIR = ROOT / "data" / "processed" / "reactions_lda"

H_PATH = OUT_DIR / "lda_H.npy"
TERMS_PATH = OUT_DIR / "topic_terms.csv"
TOPIC_SHARE_PATH = OUT_DIR / "topic_monthly_share.csv"
MAP_PATH = OUT_DIR / "topic_regime_map.csv"
REGIME_PATH = OUT_DIR / "regime_monthly.csv"
CP_PATH = OUT_DIR / "changepoints.csv"
QC_PATH = OUT_DIR / "regimes_qc.md"
META_PATH = OUT_DIR / "lda_meta.json"


def fit_lda(
    X: sparse.csr_matrix,
    months: np.ndarray,
    n_topics: int,
    random_state: int,
    max_iter: int,
    per_month: int,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray, LatentDirichletAllocation, float, int]:
    """카운트 행렬(이진)에 online LDA. 적합은 층화표본, 변환은 전량."""
    fit_idx = stratified_indices(months, per_month, random_state)
    print(f"  적합 표본 {len(fit_idx):,}건 (월당 최대 {per_month:,}, seed {random_state})", flush=True)

    t1 = time.perf_counter()
    model = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method="online",
        learning_offset=50.0,
        batch_size=batch_size,
        max_iter=max_iter,
        random_state=random_state,
        evaluate_every=-1,
        n_jobs=1,
    )
    model.fit(X[fit_idx])
    print(f"  LDA.fit {time.perf_counter() - t1:.1f}s · iter {model.n_iter_}", flush=True)

    t2 = time.perf_counter()
    W = model.transform(X)
    elapsed = time.perf_counter() - t1
    print(f"  LDA.transform 전량 {time.perf_counter() - t2:.1f}s · 합계 {elapsed:.1f}s", flush=True)
    return W, model.components_.copy(), model, elapsed, int(len(fit_idx))


def write_lda_qc(
    *,
    mapping: pd.DataFrame,
    topic_share: pd.DataFrame,
    regimes: pd.DataFrame,
    cps: pd.DataFrame,
    n_docs_total: int,
    n_drop: int,
    n_topics: int,
    n_iter: int,
    fit_s: float,
    matrix_hash: str,
    sklearn_ver: str,
    slugs: dict[str, str],
    labels: list[str],
    random_state: int,
    n_fit: int,
) -> None:
    lines: list[str] = []
    add = lines.append
    add("# 폴백 LDA 국면 점검")
    add("")
    add(f"생성: `analysis.fallback_topics` · {pd.Timestamp.now():%Y-%m-%d %H:%M}")
    add("")
    add("이 산출은 NMF 본분석을 대체하지 않는다. 주 종속변수 그룹 차이가 약할 때")
    add("같은 행렬·같은 매핑 규칙으로 토픽 모형만 바꾼 비교용이다.")
    add("")
    add("## 1. 입력·적합")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 행렬 | `{MATRIX_PATH.relative_to(ROOT).as_posix()}` |")
    add(f"| 행렬 sha256 | `{matrix_hash}` |")
    add(f"| 문서 | {n_docs_total:,}건 (n_terms=0 제외 {n_drop}건) |")
    add(f"| 월 | {len(topic_share)}개 ({topic_share.index[0]} ~ {topic_share.index[-1]}) |")
    add(f"| 모형 | LDA(online) · 토픽 {n_topics} · seed {random_state} |")
    add(f"| 적합 표본 | {n_fit:,}건 · iter {n_iter} · {fit_s:.1f}s |")
    add(f"| sklearn | {sklearn_ver} |")
    add("| 수동 덮어쓰기 | 없음 (NMF topic 3 덮어쓰기는 토픽 번호가 달라 적용하지 않음) |")
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
    add("## 3. z-우세 개월")
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


def run_lda(n_topics: int, random_state: int, max_iter: int, per_month: int, batch_size: int) -> dict:
    import sklearn

    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("행렬 로드 (LDA)", flush=True)
    X, docs, vocab = load_inputs()
    n_total = X.shape[0]
    X, docs, n_drop = drop_empty(X, docs)
    print(f"  {n_total:,} → {X.shape[0]:,} (빈 문서 {n_drop}건 제외)", flush=True)

    months_arr = docs["month"].to_numpy()
    W, H, model, fit_s, n_fit = fit_lda(
        X, months_arr, n_topics, random_state, max_iter, per_month, batch_size,
    )
    doc_share, ok = row_shares(W)
    topic_share = monthly_topic_share(doc_share, months_arr, ok)
    n_docs = (
        pd.DataFrame({"month": months_arr[ok]})
        .groupby("month").size().rename("n_docs")
    )

    # NMF 수동 덮어쓰기(토픽 3=완성차)는 LDA 토픽 번호에 적용하지 않는다.
    mapping = map_topics(H, vocab, labels, overrides={})
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
    META_PATH.write_text(json.dumps({
        "method": "lda",
        "n_fit": n_fit,
        "n_iter": int(model.n_iter_),
        "fit_s": fit_s,
        "sklearn": sklearn.__version__,
        "random_state": random_state,
        "n_topics": n_topics,
        "max_iter": max_iter,
        "per_month": per_month,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    write_lda_qc(
        mapping=mapping, topic_share=topic_share, regimes=regimes, cps=cps,
        n_docs_total=X.shape[0], n_drop=n_drop, n_topics=n_topics,
        n_iter=int(model.n_iter_), fit_s=fit_s,
        matrix_hash=sha256_file(MATRIX_PATH),
        sklearn_ver=sklearn.__version__, slugs=slugs, labels=labels,
        random_state=random_state, n_fit=n_fit,
    )

    print(f"\n=== LDA 국면 ===")
    print(regimes["dominant_regime"].value_counts().to_string())
    print(f"변화점 {len(cps)}건")
    print(f"월별 → {REGIME_PATH}")
    print(f"QC   → {QC_PATH}")
    return {"regimes": regimes, "cps": cps, "mapping": mapping}


def try_bertopic() -> dict:
    """BERTopic이 설치되어 있으면 알리고, 없으면 건너뛴다. 본분석에 넣지 않는다."""
    try:
        import bertopic  # noqa: F401
    except ImportError:
        note = "bertopic 미설치 — 폴백 2순위 건너뜀. LDA만 실행."
        print(note)
        return {"ran": False, "reason": note}
    return {
        "ran": False,
        "reason": "bertopic 은 설치되어 있으나 임베딩 전량 적합은 이번 범위에서 돌리지 않음. LDA가 폴백 1순위.",
    }


def run_fallback_reactions() -> dict:
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    df = join_regime_panel(REGIME_PATH, labels)
    cps = pd.read_csv(CP_PATH, dtype={"cp_month": str})
    return analyze(
        df, cps, labels, slugs, REACT_DIR,
        qc_title="폴백 LDA 국면별 반응 분석 점검",
    )


def main() -> None:
    cfg = load_config()
    tm = cfg["topic_model"]
    p = argparse.ArgumentParser(description="폴백 LDA 국면 (본분석 NMF는 유지)")
    p.add_argument("--method", choices=["lda"], default="lda")
    p.add_argument("--topics", type=int, default=int(tm["n_topics"]))
    p.add_argument("--seed", type=int, default=int(tm["random_state"]))
    p.add_argument("--max-iter", type=int, default=15)
    p.add_argument("--per-month", type=int, default=FIT_PER_MONTH)
    p.add_argument("--batch-size", type=int, default=2048)
    p.add_argument("--skip-reactions", action="store_true")
    a = p.parse_args()

    run_lda(a.topics, a.seed, a.max_iter, a.per_month, a.batch_size)
    bt = try_bertopic()
    print(f"BERTopic: {bt['reason']}")
    if not a.skip_reactions:
        run_fallback_reactions()


if __name__ == "__main__":
    main()
