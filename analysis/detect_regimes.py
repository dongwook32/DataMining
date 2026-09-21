"""코퍼스 전량 문서-어휘 행렬 → 월별 국면 시계열.

  python -m analysis.detect_regimes
  python -m analysis.detect_regimes --remap-only   # 저장해 둔 H·월별 비중만으로 매핑·변화점 재계산

`doc_term.npz`에 TF-IDF를 얹고 NMF(14토픽)를 적합한다. 적합은 월별 무작위 3,000건
층화표본(탐색과 같은 규모, 앞부분 절단이 아님)에 하고, 추정된 H로 전량 문서를
변환한다. 시계열은 전량 변환에서 나온다. 토픽을 데이터랩 키워드 세트와의 겹침으로
국면 7개에 접고, 그달 라벨은 국면 비중의 표본 내 z점수가 가장 큰 축이다
(원비중 argmax는 상시 큰 토픽이 매달 이긴다). 토픽 비중 벡터에 PELT(L2, BIC)를
걸어 전환을 찾는다.

MiniBatchNMF 전량 적합은 버렸다. max_no_improvement=10 때문에 3 epoch 만에 멈추고
성분이 일반 어휘로 남았다. 탐색 단계와 같은 `sklearn.decomposition.NMF`를 쓴다.

산출:
  data/processed/regimes/topic_terms.csv
  data/processed/regimes/topic_monthly_share.csv
  data/processed/regimes/topic_regime_map.csv
  data/processed/regimes/regime_monthly.csv
  data/processed/regimes/changepoints.csv
  data/processed/regimes/nmf_H.npy
  data/processed/regimes/regimes_qc.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfTransformer

from api.datalab_keyword_sets import KEYWORD_SETS
from config import load_config, project_root

ROOT = project_root()
CORPUS_DIR = ROOT / "data" / "processed" / "corpus"
OUT_DIR = ROOT / "data" / "processed" / "regimes"

MATRIX_PATH = CORPUS_DIR / "doc_term.npz"
VOCAB_PATH = CORPUS_DIR / "doc_term_vocab.csv"
DOCS_PATH = CORPUS_DIR / "doc_term_docs.parquet"
EXPLORATORY_SHARE = CORPUS_DIR / "topic_monthly_share.csv"

H_PATH = OUT_DIR / "nmf_H.npy"
TERMS_PATH = OUT_DIR / "topic_terms.csv"
TOPIC_SHARE_PATH = OUT_DIR / "topic_monthly_share.csv"
MAP_PATH = OUT_DIR / "topic_regime_map.csv"
REGIME_PATH = OUT_DIR / "regime_monthly.csv"
CP_PATH = OUT_DIR / "changepoints.csv"
QC_PATH = OUT_DIR / "regimes_qc.md"
META_PATH = OUT_DIR / "nmf_meta.json"

TOP_TERMS = 25
# 변화점: 한 달이 단독 구간이 되지 않게. 국면이 한 달 만에 바뀌었다가 돌아오는
# 잡음을 전환으로 세지 않기 위해서다.
CP_MIN_SIZE = 3
# 키워드 질량이 이보다 작으면 그 토픽은 국면에 접지 않는다 (기타).
MIN_MAP_SHARE = 0.01
# 적합 표본: 월마다 이 건수를 무작위로. 탐색은 같은 수였으나 파일 앞부분만 취했다.
FIT_PER_MONTH = 3000

# 자동 매핑이 상위 어휘와 명백히 어긋날 때만 채운다. 키는 토픽 번호, 값은 국면 라벨
# 또는 "기타". 근거는 적합 후 상위 어휘를 QC에 남긴다.
MANUAL_OVERRIDE: dict[int, str] = {
    # 자동 매핑은 검색어 세트에 '전기차'가 있어 AI반도체로 붙인다.
    # 상위 어휘는 현대차·기아·SUV라 완성차 기사이지 반도체 축이 아니다.
    3: "기타",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_inputs() -> tuple[sparse.csr_matrix, pd.DataFrame, list[str]]:
    if not MATRIX_PATH.exists():
        raise FileNotFoundError(f"행렬이 없다: {MATRIX_PATH}")
    X = sparse.load_npz(MATRIX_PATH).tocsr()
    docs = pd.read_parquet(DOCS_PATH, columns=["article_id", "month", "n_terms"])
    vocab = list(pd.read_csv(VOCAB_PATH)["term"].astype(str))
    if X.shape[0] != len(docs):
        raise ValueError(f"행 수 불일치: 행렬 {X.shape[0]:,} vs docs {len(docs):,}")
    if X.shape[1] != len(vocab):
        raise ValueError(f"열 수 불일치: 행렬 {X.shape[1]:,} vs vocab {len(vocab):,}")
    return X, docs, vocab


def drop_empty(X: sparse.csr_matrix, docs: pd.DataFrame) -> tuple[sparse.csr_matrix, pd.DataFrame, int]:
    keep = docs["n_terms"].to_numpy() > 0
    n_drop = int((~keep).sum())
    return X[keep], docs.loc[keep].reset_index(drop=True), n_drop


def stratified_indices(months: np.ndarray, per_month: int, seed: int) -> np.ndarray:
    """월마다 per_month건을 무작위로. 탐색의 '앞에서 자르기'를 쓰지 않기 위해서다."""
    rng = np.random.default_rng(seed)
    parts = []
    for month in np.unique(months):
        idx = np.flatnonzero(months == month)
        take = min(per_month, int(idx.size))
        parts.append(rng.choice(idx, size=take, replace=False))
    return np.sort(np.concatenate(parts))


def fit_nmf(
    X: sparse.csr_matrix,
    months: np.ndarray,
    n_topics: int,
    random_state: int,
    max_iter: int,
    per_month: int,
) -> tuple[np.ndarray, np.ndarray, NMF, float, int]:
    """IDF는 전량, NMF 적합은 층화표본, W는 전량 변환."""
    t0 = time.perf_counter()
    tfidf = TfidfTransformer(norm="l2", use_idf=True, smooth_idf=True, sublinear_tf=False)
    Xt = tfidf.fit_transform(X)
    print(f"  TF-IDF {Xt.shape[0]:,} × {Xt.shape[1]:,} · {time.perf_counter() - t0:.1f}s", flush=True)

    fit_idx = stratified_indices(months, per_month, random_state)
    print(f"  적합 표본 {len(fit_idx):,}건 (월당 최대 {per_month:,}, seed {random_state})", flush=True)

    t1 = time.perf_counter()
    model = NMF(
        n_components=n_topics,
        init="nndsvd",
        solver="cd",
        beta_loss="frobenius",
        max_iter=max_iter,
        random_state=random_state,
        verbose=0,
    )
    model.fit(Xt[fit_idx])
    print(f"  NMF.fit {time.perf_counter() - t1:.1f}s · iter {model.n_iter_}", flush=True)

    t2 = time.perf_counter()
    W = model.transform(Xt)
    elapsed = time.perf_counter() - t1
    print(f"  NMF.transform 전량 {time.perf_counter() - t2:.1f}s · 합계 {elapsed:.1f}s", flush=True)
    return W, model.components_.copy(), model, elapsed, int(len(fit_idx))


def row_shares(W: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """문서별 토픽 비중. 행 합이 0이면 정의되지 않으므로 마스크로 돌려준다."""
    totals = W.sum(axis=1, keepdims=True)
    ok = totals.ravel() > 0
    shares = np.zeros_like(W)
    shares[ok] = W[ok] / totals[ok]
    return shares, ok


def monthly_topic_share(doc_share: np.ndarray, months: np.ndarray, ok: np.ndarray) -> pd.DataFrame:
    cols = [f"topic_{k}" for k in range(doc_share.shape[1])]
    df = pd.DataFrame(doc_share[ok], columns=cols)
    df["month"] = months[ok]
    monthly = df.groupby("month", sort=True).mean()
    monthly = monthly.div(monthly.sum(axis=1), axis=0)
    return monthly


def keyword_index(vocab: list[str]) -> dict[str, list[int]]:
    """국면 → 어휘 열 번호. 더 긴 키워드가 이긴다(대출금리 → 가계대출, 금리 아님)."""
    term_pos = {t: i for i, t in enumerate(vocab)}
    pairs: list[tuple[str, str]] = []
    for regime, groups in KEYWORD_SETS.items():
        seen: set[str] = set()
        for group in groups:
            for kw in group["keywords"]:
                if kw not in seen:
                    seen.add(kw)
                    pairs.append((kw, regime))
    pairs.sort(key=lambda x: len(x[0]), reverse=True)

    claimed: dict[int, str] = {}
    for kw, regime in pairs:
        if kw in term_pos:
            j = term_pos[kw]
            if j not in claimed:
                claimed[j] = regime
        for j, term in enumerate(vocab):
            if j in claimed:
                continue
            if len(kw) >= 2 and kw in term:
                claimed[j] = regime

    by_regime: dict[str, list[int]] = {r: [] for r in KEYWORD_SETS}
    for j, regime in claimed.items():
        by_regime[regime].append(j)
    return by_regime


def map_topics(
    H: np.ndarray,
    vocab: list[str],
    labels: list[str],
    overrides: dict[int, str] | None = None,
) -> pd.DataFrame:
    """토픽 k의 H 질량이 어느 국면 키워드에 실렸는지로 배정한다.

    여러 토픽이 한 국면에 붙을 수 있다(탐색에서 증시실적이 그랬다).
    키워드 질량이 전부 0이면 기타. overrides 가 None 이면 NMF 용 MANUAL_OVERRIDE.
    LDA 폴백은 빈 dict 를 넘겨 토픽 번호가 다른 수동 덮어쓰기를 쓰지 않는다.
    """
    by_regime = keyword_index(vocab)
    ov = MANUAL_OVERRIDE if overrides is None else overrides
    rows = []
    for k in range(H.shape[0]):
        scores = {r: float(H[k, idx].sum()) if idx else 0.0 for r, idx in by_regime.items()}
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_r, best_s = ranked[0]
        second_r, second_s = ranked[1]
        h_sum = float(H[k].sum()) or 1.0
        if best_s <= 0 or (best_s / h_sum) < MIN_MAP_SHARE:
            regime = "기타"
        else:
            regime = best_r
        source = "auto"
        if k in ov:
            regime = ov[k]
            source = "manual"
        top_idx = np.argsort(H[k])[::-1][:TOP_TERMS]
        top_terms = ", ".join(vocab[j] for j in top_idx)
        rows.append({
            "topic": k,
            "regime": regime,
            "source": source,
            "score": best_s,
            "score_share": best_s / h_sum,
            "second_regime": second_r,
            "second_score": second_s,
            "top_terms": top_terms,
        })
    out = pd.DataFrame(rows)
    missing = [r for r in labels if r not in set(out["regime"])]
    if missing:
        print(f"  경고: 매핑에서 빠진 국면 {missing}", flush=True)
    return out


def topic_terms_table(H: np.ndarray, vocab: list[str]) -> pd.DataFrame:
    rows = []
    for k in range(H.shape[0]):
        order = np.argsort(H[k])[::-1][:TOP_TERMS]
        for rank, j in enumerate(order, start=1):
            rows.append({"topic": k, "rank": rank, "term": vocab[j], "weight": float(H[k, j])})
    return pd.DataFrame(rows)


def fold_regimes(
    topic_share: pd.DataFrame,
    mapping: pd.DataFrame,
    n_docs: pd.Series,
    labels: list[str],
    slugs: dict[str, str],
) -> pd.DataFrame:
    """14토픽 비중 → 7국면 비중. 라벨은 원비중 argmax가 아니라 표본 내 z점수 argmax.

    경제지 코퍼스에서 증시·AI 기사는 매달 많다. 원비중 최댓값은 상시 큰 축이 이긴다.
    z점수는 '평소보다 얼마나 올랐는지'를 보므로 국면 라벨의 질문에 맞다.
    """
    assigned = {r: [] for r in labels}
    other: list[int] = []
    for _, row in mapping.iterrows():
        k = int(row["topic"])
        if row["regime"] in assigned:
            assigned[row["regime"]].append(k)
        else:
            other.append(k)

    out = pd.DataFrame({"month": topic_share.index.astype(str)})
    out["n_docs"] = out["month"].map(n_docs).astype(int)
    share_cols = []
    for label in labels:
        slug = slugs[label]
        cols = [f"topic_{k}" for k in assigned[label]]
        out[f"share_{slug}"] = topic_share[cols].sum(axis=1).to_numpy() if cols else 0.0
        share_cols.append(f"share_{slug}")
    out["residual_share"] = (
        topic_share[[f"topic_{k}" for k in other]].sum(axis=1).to_numpy() if other else 0.0
    )

    shares = out[share_cols].to_numpy(dtype=float)
    raw_top = shares.argmax(axis=1)
    out["dominant_raw"] = [labels[i] for i in raw_top]
    out["dominant_raw_share"] = shares[np.arange(len(out)), raw_top]

    std = shares.std(axis=0, ddof=1)
    std = np.where(std < 1e-12, np.nan, std)
    z = (shares - shares.mean(axis=0)) / std
    z = np.where(np.isnan(z), -np.inf, z)
    z_top = z.argmax(axis=1)
    z_runner = np.argpartition(-z, 1, axis=1)[:, 1]
    out["dominant_regime"] = [labels[i] for i in z_top]
    out["dominant_share"] = shares[np.arange(len(out)), z_top]
    out["dominant_z"] = z[np.arange(len(out)), z_top]
    out["runner_up"] = [labels[i] for i in z_runner]
    out["runner_up_share"] = shares[np.arange(len(out)), z_runner]
    out["runner_up_z"] = z[np.arange(len(out)), z_runner]
    return out


def bic_penalty(n: int, dim: int) -> float:
    """L2 평균 변화 PELT의 BIC 페널티. 미리 정해 두고 결과에 맞추지 않는다."""
    return dim * float(np.log(n))


def standardize_cols(x: np.ndarray) -> np.ndarray:
    """열별 z점수. 원비중이 [0,1]이면 BIC 페널티가 손실보다 커 전환이 0건이 된다."""
    sd = x.std(axis=0, ddof=1)
    sd = np.where(sd < 1e-12, 1.0, sd)
    return (x - x.mean(axis=0)) / sd


def detect_changepoints(
    signal: np.ndarray,
    months: list[str],
    regime_labels: list[str],
    signal_name: str,
) -> pd.DataFrame:
    import ruptures as rpt

    n, dim = signal.shape
    pen = bic_penalty(n, dim)
    z = standardize_cols(signal)
    algo = rpt.Pelt(model="l2", min_size=CP_MIN_SIZE, jump=1).fit(z)
    bkps = algo.predict(pen=pen)
    # ruptures는 구간 끝(배타) 인덱스를 주고 마지막은 항상 n이다.
    bounds = [0] + list(bkps)
    rows = []
    for i in range(len(bounds) - 2):
        a, b, c = bounds[i], bounds[i + 1], bounds[i + 2]
        prev = z[a:b].mean(axis=0)
        nxt = z[b:c].mean(axis=0)
        from_i = int(prev.argmax())
        to_i = int(nxt.argmax())
        rows.append({
            "signal": signal_name,
            "model": "l2_z",
            "penalty": pen,
            "cp_month": months[b],
            "from_label": regime_labels[from_i] if from_i < len(regime_labels) else str(from_i),
            "to_label": regime_labels[to_i] if to_i < len(regime_labels) else str(to_i),
            "segment_start": months[a],
            "segment_end": months[b - 1],
        })
    return pd.DataFrame(rows)


def write_qc(
    *,
    mapping: pd.DataFrame,
    topic_share: pd.DataFrame,
    regimes: pd.DataFrame,
    cps: pd.DataFrame,
    n_docs_total: int,
    n_drop: int,
    n_zero_w: int,
    n_topics: int,
    n_iter: int,
    fit_s: float,
    recon: float | None,
    matrix_hash: str,
    sklearn_ver: str,
    slugs: dict[str, str],
    labels: list[str],
    random_state: int,
    n_fit: int,
) -> None:
    lines: list[str] = []
    add = lines.append
    add("# 국면 탐지 품질 점검")
    add("")
    add(f"생성: `analysis.detect_regimes` · {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    add("")
    add("## 1. 입력·적합")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 행렬 | `{MATRIX_PATH.relative_to(ROOT).as_posix()}` |")
    add(f"| 행렬 sha256 | `{matrix_hash}` |")
    add(f"| 문서 | {n_docs_total:,}건 (n_terms=0 제외 {n_drop}건) |")
    add(f"| W 행합 0 | {n_zero_w}건 (월평균에서 제외) |")
    add(f"| 월 | {len(topic_share)}개 ({topic_share.index[0]} ~ {topic_share.index[-1]}) |")
    add(f"| 모형 | NMF(CD) · 토픽 {n_topics} · init nndsvd · seed {random_state} |")
    fit_note = (
        f"{n_fit:,}건 (월당 최대 {FIT_PER_MONTH:,}, 무작위 층화) · iter {n_iter} · {fit_s:.1f}s"
        if n_fit >= 0
        else "remap-only (기존 H)"
    )
    add(f"| 적합 표본 | {fit_note} |")
    add(f"| sklearn | {sklearn_ver} |")
    if recon is not None:
        add(f"| 재구성 오차 | {recon:.6f} |")
    add("")
    add("IDF는 전량 행렬에서 계산하고, NMF는 월별 무작위 층화표본에만 적합한다.")
    add("시계열은 그 H로 전량 문서를 변환해 만든다. MiniBatchNMF 전량 적합은")
    add("early-stop 때문에 성분이 갈리지 않아 버렸다.")
    add("")
    add("## 2. 토픽 → 국면 매핑")
    add("")
    add("배정은 데이터랩 키워드 세트(`api/datalab_keyword_sets.py`)와 H 질량의 겹침이다.")
    add(f"질량 점유가 {MIN_MAP_SHARE} 미만이면 기타. 더 긴 키워드가 이긴다.")
    add("여러 토픽이 한 국면에 붙을 수 있다.")
    add("")
    add("| 토픽 | 국면 | 출처 | 질량 점유 | 차순위 | 상위 어휘 |")
    add("|------|------|------|-----------|--------|-----------|")
    for _, r in mapping.iterrows():
        add(
            f"| {int(r['topic'])} | {r['regime']} | {r['source']} | "
            f"{r['score_share']:.3f} | {r['second_regime']} | {r['top_terms']} |"
        )
    add("")
    by = mapping.groupby("regime")["topic"].apply(lambda s: ", ".join(str(x) for x in s))
    add("국면별 토픽: " + " · ".join(f"{k} [{v}]" for k, v in by.items()) + ".")
    add("")
    uncovered = [r for r in labels if r not in set(mapping["regime"])]
    if uncovered:
        add(f"**매핑에서 빠진 국면:** {', '.join(uncovered)}.")
        if "물가" in uncovered:
            add("토픽 9 상위 어휘는 물가·인플레이션과 금리·연준이 같이 나온다. "
                "금리 질량과 물가 질량이 거의 같아 전량 NMF는 둘을 한 거시 축으로 붙인다. "
                "검색 대분류의 물가는 뉴스 토픽에서 독립 축이 아니다. 라벨은 질량 1위(금리)를 쓴다.")
        add("")

    add("## 3. 월별 우세 국면")
    add("")
    add("라벨은 국면 비중의 **표본 내 z점수** argmax다. 원비중 argmax(`dominant_raw`)는")
    add("상시 큰 축(증시·AI)이 매달 이기므로 참고열로만 둔다.")
    add("")
    add("| 국면 | z-우세 개월 | 원비중 우세 | 평균 비중 | 피크 월 | 피크 비중 |")
    add("|------|------------|------------|-----------|---------|-----------|")
    for label in labels:
        slug = slugs[label]
        s = regimes[f"share_{slug}"]
        n_z = int((regimes["dominant_regime"] == label).sum())
        n_raw = int((regimes["dominant_raw"] == label).sum())
        peak_month = regimes.loc[s.idxmax(), "month"]
        add(f"| {label} | {n_z} | {n_raw} | {s.mean():.3f} | {peak_month} | {s.max():.3f} |")
    add("")
    add("z-우세 시계열 (월 순):")
    add("")
    seq = " → ".join(f"{m[-2:]}:{r}" for m, r in zip(regimes["month"], regimes["dominant_regime"]))
    add(seq)
    add("")
    add(f"z>1 월: {int((regimes['dominant_z'] > 1).sum())} / {len(regimes)}. "
        f"원비중 우세와 z-우세가 다른 월: "
        f"{int((regimes['dominant_regime'] != regimes['dominant_raw']).sum())}.")
    add("단일 라벨은 그달의 상대 상승 축일 뿐이고, 비중 벡터가 공존 이슈를 담는다.")
    add("")

    add("## 4. 변화점 (PELT L2, 열별 z점수 + BIC 페널티)")
    add("")
    add("신호는 열별 z점수로 표준화한 뒤 PELT를 건다. 원비중 [0,1]에 `dim × ln(n)`을")
    add("그대로 씌우면 페널티가 손실보다 커 전환이 항상 0건이었다. 표준화 후 같은")
    add("페널티 식은 분산 1인 가우시안 평균 변화에 대한 BIC에 가깝다. 페널티 값은")
    add("결과에 맞춰 바꾸지 않는다.")
    add("")
    add(f"n={len(topic_share)}, "
        f"토픽 신호 dim={n_topics} → {bic_penalty(len(topic_share), n_topics):.4f}, "
        f"국면 신호 dim={len(labels)} → {bic_penalty(len(topic_share), len(labels)):.4f}.")
    add(f"최소 구간 {CP_MIN_SIZE}개월. 2026-03·2026-07이 잡히면 타당성 확인이지 발견이 아니다.")
    add("")
    if cps.empty:
        add("변화점 없음 (페널티 하에서 전 구간이 한 덩어리).")
        add("")
    else:
        add("| 신호 | 전환월 | 이전 | 이후 | 이전 구간 |")
        add("|------|--------|------|------|-----------|")
        for _, r in cps.iterrows():
            add(
                f"| {r['signal']} | {r['cp_month']} | {r['from_label']} | "
                f"{r['to_label']} | {r['segment_start']}~{r['segment_end']} |"
            )
        add("")
        for signal_name in cps["signal"].unique():
            months_hit = set(cps.loc[cps["signal"] == signal_name, "cp_month"])
            for mark in ("2026-03", "2026-07"):
                hit = mark in months_hit
                add(f"- `{signal_name}` 에 {mark}: {'잡힘 (타당성 확인)' if hit else '안 잡힘'}")
        add("")
    import ruptures as rpt
    topic_cols = [c for c in topic_share.columns if c.startswith("topic_")]
    share_cols = [f"share_{slugs[r]}" for r in labels]
    add("페널티 배율에 따른 전환 수 (본결과는 ×1, 신호는 열별 z점수). 배율을 골라 2026년을 맞추지는 않는다.")
    add("")
    add("| 신호 | ×0.25 | ×0.5 | ×1 (BIC) | ×2 |")
    add("|------|-------|------|----------|-----|")
    for name, arr, dim in (
        ("topics", topic_share[topic_cols].to_numpy(), n_topics),
        ("regimes", regimes[share_cols].to_numpy(), len(labels)),
    ):
        base = bic_penalty(arr.shape[0], dim)
        fitted = rpt.Pelt(model="l2", min_size=CP_MIN_SIZE, jump=1).fit(standardize_cols(arr))
        counts = []
        for mult in (0.25, 0.5, 1.0, 2.0):
            bkps = fitted.predict(pen=base * mult)
            counts.append(str(max(len(bkps) - 1, 0)))
        add(f"| {name} | " + " | ".join(counts) + " |")
    add("")

    add("## 5. 정합 검사")
    add("")
    topic_sum = topic_share.sum(axis=1)
    share_cols = [f"share_{slugs[r]}" for r in labels]
    regime_sum = regimes[share_cols].sum(axis=1) + regimes["residual_share"]
    add(f"- 토픽 비중 행합: 최소 {topic_sum.min():.12f} · 최대 {topic_sum.max():.12f} (1이어야 함)")
    add(f"- 국면+잔차 행합: 최소 {regime_sum.min():.12f} · 최대 {regime_sum.max():.12f} (1이어야 함)")
    add(f"- 월 수 67 여부: {len(regimes) == 67} (실제 {len(regimes)})")
    add(f"- 결측: 토픽 {int(topic_share.isna().sum().sum())} · 국면 {int(regimes.isna().sum().sum())}")
    add("")

    if EXPLORATORY_SHARE.exists():
        add("## 6. 탐색 표본(월별 앞 3,000건)과의 상관")
        add("")
        add("토픽 번호는 적합마다 바뀌므로, 전량 토픽 각각에 대해 탐색 토픽 중")
        add("월별 비중 상관이 가장 큰 짝을 본다. 축이 되살아났는지의 점검이다.")
        add("")
        old = pd.read_csv(EXPLORATORY_SHARE)
        old["month"] = old["month"].astype(str)
        old = old.set_index("month")
        old_cols = [c for c in old.columns if c != "month"]
        new = topic_share.copy()
        new.index = new.index.astype(str)
        common = new.index.intersection(old.index)
        add("| 전량 토픽 | 국면 | 탐색 토픽 | 상관 |")
        add("|-----------|------|-----------|------|")
        for k in range(n_topics):
            cors = {c: float(new.loc[common, f"topic_{k}"].corr(old.loc[common, c])) for c in old_cols}
            best = max(cors, key=lambda c: abs(cors[c]))
            regime = mapping.loc[mapping["topic"] == k, "regime"].iloc[0]
            add(f"| {k} | {regime} | {best} | {cors[best]:+.3f} |")
        add("")
        add("탐색 파일은 표본이라 숫자가 달라도 방향만 같으면 된다. 국면 시계열은 전량 쪽을 쓴다.")
        add("")

    add("## 7. 주장 범위")
    add("")
    add("코퍼스는 매일경제·서울경제·한국경제 3개 경제지다. 종합지를 추가하지 않기로 했으므로")
    add("이후 결과는 **경제지 기준 이슈 국면**으로 읽는다. 매체 편향을 통제하지는 못했다.")
    add("")
    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_fit(n_topics: int, random_state: int, max_iter: int, per_month: int) -> None:
    import sklearn

    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])

    print("행렬 로드", flush=True)
    X, docs, vocab = load_inputs()
    n_total = X.shape[0]
    X, docs, n_drop = drop_empty(X, docs)
    print(f"  {n_total:,} → {X.shape[0]:,} (빈 문서 {n_drop}건 제외)", flush=True)

    months_arr = docs["month"].to_numpy()
    W, H, model, fit_s, n_fit = fit_nmf(
        X, months_arr, n_topics, random_state, max_iter, per_month,
    )
    doc_share, ok = row_shares(W)
    n_zero_w = int((~ok).sum())
    topic_share = monthly_topic_share(doc_share, months_arr, ok)
    n_docs = (
        pd.DataFrame({"month": months_arr[ok]})
        .groupby("month")
        .size()
        .rename("n_docs")
    )

    np.save(H_PATH, H)
    topic_share.index.name = "month"
    topic_share.to_csv(TOPIC_SHARE_PATH, encoding="utf-8-sig")
    recon = float(model.reconstruction_err_) if hasattr(model, "reconstruction_err_") else None
    META_PATH.write_text(json.dumps({
        "n_fit": n_fit,
        "n_iter": int(model.n_iter_),
        "fit_s": fit_s,
        "recon": recon,
        "n_zero_w": n_zero_w,
        "sklearn": sklearn.__version__,
        "random_state": random_state,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  H → {H_PATH}")
    print(f"  월별 토픽 비중 → {TOPIC_SHARE_PATH}")

    finish_from_share(
        H=H,
        vocab=vocab,
        topic_share=topic_share,
        n_docs=n_docs,
        labels=labels,
        slugs=slugs,
        n_docs_total=X.shape[0],
        n_drop=n_drop,
        n_zero_w=n_zero_w,
        n_iter=int(model.n_iter_),
        fit_s=fit_s,
        recon=recon,
        sklearn_ver=sklearn.__version__,
        random_state=random_state,
        n_fit=n_fit,
    )


def run_remap() -> None:
    import sklearn

    if not H_PATH.exists() or not TOPIC_SHARE_PATH.exists():
        raise FileNotFoundError("--remap-only 는 nmf_H.npy 와 topic_monthly_share.csv 가 있어야 한다")
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    vocab = list(pd.read_csv(VOCAB_PATH)["term"].astype(str))
    H = np.load(H_PATH)
    topic_share = pd.read_csv(TOPIC_SHARE_PATH, index_col="month")
    docs = pd.read_parquet(DOCS_PATH, columns=["month", "n_terms"])
    n_docs = docs.loc[docs["n_terms"] > 0].groupby("month").size().rename("n_docs")
    n_drop = int((docs["n_terms"] == 0).sum())
    meta = json.loads(META_PATH.read_text(encoding="utf-8")) if META_PATH.exists() else {}
    finish_from_share(
        H=H,
        vocab=vocab,
        topic_share=topic_share,
        n_docs=n_docs,
        labels=labels,
        slugs=slugs,
        n_docs_total=int((docs["n_terms"] > 0).sum()),
        n_drop=n_drop,
        n_zero_w=int(meta.get("n_zero_w", 0)),
        n_iter=int(meta.get("n_iter", -1)),
        fit_s=float(meta.get("fit_s", 0.0)),
        recon=meta.get("recon"),
        sklearn_ver=str(meta.get("sklearn", sklearn.__version__)),
        random_state=int(cfg["topic_model"]["random_state"]),
        n_fit=int(meta.get("n_fit", -1)),
    )


def finish_from_share(
    *,
    H: np.ndarray,
    vocab: list[str],
    topic_share: pd.DataFrame,
    n_docs: pd.Series,
    labels: list[str],
    slugs: dict[str, str],
    n_docs_total: int,
    n_drop: int,
    n_zero_w: int,
    n_iter: int,
    fit_s: float,
    recon: float | None,
    sklearn_ver: str,
    random_state: int,
    n_fit: int,
) -> None:
    mapping = map_topics(H, vocab, labels)
    terms = topic_terms_table(H, vocab)
    regimes = fold_regimes(topic_share, mapping, n_docs, labels, slugs)

    print("\n=== 토픽 ===", flush=True)
    for _, r in mapping.iterrows():
        print(
            f"  [{int(r['topic']):>2}] {r['regime']:<6} 질량 {r['score_share']:.3f}  "
            f"{r['top_terms'][:80]}",
            flush=True,
        )

    months = [str(m) for m in topic_share.index]
    topic_cols = [c for c in topic_share.columns if c.startswith("topic_")]
    slug_order = [slugs[r] for r in labels]
    topic_names = [str(mapping.loc[mapping["topic"] == k, "regime"].iloc[0]) for k in range(len(topic_cols))]
    cps_topics = detect_changepoints(
        topic_share[topic_cols].to_numpy(),
        months,
        topic_names,
        "topics",
    )
    cps_regimes = detect_changepoints(
        regimes[[f"share_{s}" for s in slug_order]].to_numpy(),
        months,
        labels,
        "regimes",
    )
    cps = pd.concat([cps_topics, cps_regimes], ignore_index=True)

    terms.to_csv(TERMS_PATH, index=False, encoding="utf-8-sig")
    mapping.to_csv(MAP_PATH, index=False, encoding="utf-8-sig")
    regimes.to_csv(REGIME_PATH, index=False, encoding="utf-8-sig")
    cps.to_csv(CP_PATH, index=False, encoding="utf-8-sig")

    write_qc(
        mapping=mapping,
        topic_share=topic_share,
        regimes=regimes,
        cps=cps,
        n_docs_total=n_docs_total,
        n_drop=n_drop,
        n_zero_w=n_zero_w,
        n_topics=H.shape[0],
        n_iter=n_iter,
        fit_s=fit_s,
        recon=recon,
        matrix_hash=sha256_file(MATRIX_PATH),
        sklearn_ver=sklearn_ver,
        slugs=slugs,
        labels=labels,
        random_state=random_state,
        n_fit=n_fit,
    )

    print(f"\n=== 국면 ===")
    print(regimes["dominant_regime"].value_counts().to_string())
    print(f"변화점 {len(cps)}건 (토픽 신호 {len(cps_topics)} · 국면 신호 {len(cps_regimes)})")
    print(f"\n용어 → {TERMS_PATH}")
    print(f"매핑 → {MAP_PATH}")
    print(f"월별 → {REGIME_PATH}")
    print(f"전환 → {CP_PATH}")
    print(f"QC   → {QC_PATH}")


def main() -> None:
    cfg = load_config()
    tm = cfg["topic_model"]
    p = argparse.ArgumentParser(description="전량 행렬 → 월별 국면 시계열")
    p.add_argument("--remap-only", action="store_true", help="저장본 H·월별 비중만으로 매핑·변화점 재계산")
    p.add_argument("--topics", type=int, default=int(tm["n_topics"]))
    p.add_argument("--seed", type=int, default=int(tm["random_state"]))
    p.add_argument("--max-iter", type=int, default=400)
    p.add_argument("--per-month", type=int, default=FIT_PER_MONTH)
    a = p.parse_args()

    if tm["method"] != "nmf":
        raise ValueError(f"config topic_model.method={tm['method']!r} — 이 스크립트는 nmf만 돌린다")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if a.remap_only:
        run_remap()
    else:
        run_fit(a.topics, a.seed, a.max_iter, a.per_month)


if __name__ == "__main__":
    main()
