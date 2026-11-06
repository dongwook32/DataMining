"""Phase 5.6 — 결정론적 Strict OOS 파이프라인 (v4).

v3와의 차이 (설계 변경은 모두 여기에 기록한다):
  1. 문서 순서: (month, article_id, keywords) 안정 정렬 후 article_id 중복 제거.
     입력 파일의 물리적 행 순서는 결과에 영향을 주지 않는다.
  2. 어휘 사전: DF 내림차순 → 토큰 사전순으로 동률을 고정하고 SHA-256을 저장한다.
  3. 수치 연산: BLAS/OpenMP 스레드를 1로 고정하고 버전·스레드 설정을 기록한다.
  4. 저장 아티팩트: 어휘+IDF, 학습 표본 문서 ID, NMF H 행렬, 월별 토픽 비중, 직렬화 모델.
  5. 토픽-국면 매핑: 토픽 번호에 의존하지 않는다. 고정된 8개 도메인 키워드 사전과
     학습 H 행렬·학습 어휘만으로 점수를 계산한다. 임계값은 기존 연구 상수를 그대로 쓴다.
  6. 감사 항목은 플래그가 아니라 저장 산출물에서 다시 계산한 값으로 판정한다.
  7. 보고서의 모든 수치는 계산 변수에서 동적으로 출력한다.

실행:
  python analysis/validate_strict_oos_forecast_v4.py --core-only --artifact-root <dir>   # 재현성 확인용
  python analysis/validate_strict_oos_forecast_v4.py --rerun-dir <core 재실행 디렉터리>   # 최종 실행
"""

from __future__ import annotations

import os

# 수치 연산의 비결정성을 줄이기 위해 numpy import 이전에 스레드를 고정한다.
for _var in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ[_var] = "1"

import argparse
import datetime as dt
import hashlib
import inspect
import json
import math
import platform
import re
import sys
import time
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import scipy
import sklearn
import statsmodels
import statsmodels.api as sm
from scipy import sparse
from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfTransformer

from api.datalab_keyword_sets import KEYWORD_SETS
from preprocess.mine_keywords import _tokens

SCRIPT_VERSION = "5.6.0-v4"
KST = dt.timezone(dt.timedelta(hours=9), "KST")

# ---------------------------------------------------------------- 연구 설계 상수
TRAIN_END = "2024-12"
EVAL_START = "2025-01"
EVAL_END = "2026-07"
STUDY_START = "2021-01"
MIN_DF = 200
MAX_DF_RATIO = 0.15
TOP_N_VOCAB = 30_000
N_TOPICS = 14
PER_MONTH_SAMPLE = 3000
SEED = 42
NMF_MAX_ITER = 400
NMF_INIT = "nndsvd"
NMF_SOLVER = "cd"
BATCH = 50_000
# 기존 연구(analysis/detect_regimes.py)의 상수를 그대로 쓴다. 결과를 보고 바꾸지 않는다.
MIN_MAP_SHARE = 0.01
MASS_TIE_RATIO = 0.90
TOP_TERMS = 25

EXPECTED_COUNTS = {"raw": 931_709, "train": 643_095, "eval": 288_614, "fit_sample": 144_000}

# 8개 국면 = 기존 키워드 사전(KEYWORD_SETS)의 고정 재구성. 학습 결과를 보고 바꾸지 않는다.
#   (key, group) 에서 group=None 이면 해당 key의 모든 그룹.
DOMAIN_SPEC: dict[str, dict[str, Any]] = {
    "macro": {"label": "금리·물가", "sources": [("물가", None), ("금리", None)]},
    "realestate": {"label": "부동산", "sources": [("부동산", None)]},
    "hhdebt": {"label": "가계대출", "sources": [("가계대출", None)]},
    "trade": {"label": "대외통상", "sources": [("대외통상", None)]},
    "aichip": {"label": "AI·반도체", "sources": [("AI반도체", None)]},
    "market": {"label": "시황", "sources": [("증시실적", "국내증시"), ("증시실적", "해외주식")]},
    "earnings": {"label": "기업실적", "sources": [("증시실적", "기업실적")]},
    "capital": {"label": "자본거래", "sources": [("증시실적", "공모주")]},
}
DOMAIN_ORDER = list(DOMAIN_SPEC)
# 회귀 특징은 토픽 번호가 아니라 경제 국면 이름으로 연결한다.
H1_DOMAIN = "hhdebt"
H2_DOMAIN = "macro"
# AI·반도체 키워드 사전에 전기차·배터리 그룹이 들어 있다. 이 그룹만으로 지지되면 별도 표기한다.
EV_GROUP = "전기차배터리"


# ======================================================================= 유틸
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def arr_hash(a: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(str(a.dtype).encode())
    h.update(str(a.shape).encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest().upper()


def text_hash(lines: list[str]) -> str:
    return sha256_bytes("\n".join(lines).encode("utf-8"))


def safe_path(p: Path) -> Path:
    """이미 존재하는 파일은 덮어쓰지 않고 새 버전 이름을 쓴다."""
    if not p.exists():
        return p
    v = 2
    while True:
        cand = p.parent / f"{p.stem}_v{v}{p.suffix}"
        if not cand.exists():
            return cand
        v += 1


def is_nan(x: Any) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def fnum(x: Any, nd: int = 4) -> str:
    return "N/A" if is_nan(x) else f"{x:.{nd}f}"


def fpct(x: Any, nd: int = 2) -> str:
    return "N/A" if is_nan(x) else f"{x:+.{nd}f}%"


def fratio(num: int, den: int) -> str:
    return "정의 불가" if den == 0 else f"{100 * num / den:.1f}% ({num}/{den})"


def improvement(baseline: float, model: float) -> float:
    if is_nan(baseline) or is_nan(model) or baseline == 0:
        return float("nan")
    return 100.0 * (baseline - model) / baseline


def verdict_word(x: Any) -> str:
    if is_nan(x):
        return "N/A"
    return "오차 감소" if x > 0 else "오차 증가" if x < 0 else "동일"


# ======================================================================= 도메인 사전
def build_domain_pairs() -> list[tuple[str, str, str]]:
    """(keyword, domain_slug, group_name). 긴 키워드 우선, 동률은 도메인 순서→키워드 사전순."""
    pairs: list[tuple[str, str, str]] = []
    for slug in DOMAIN_ORDER:
        seen: set[str] = set()
        for key, group_name in DOMAIN_SPEC[slug]["sources"]:
            for group in KEYWORD_SETS[key]:
                if group_name is not None and group["groupName"] != group_name:
                    continue
                for kw in group["keywords"]:
                    if kw not in seen:
                        seen.add(kw)
                        pairs.append((kw, slug, group["groupName"]))
    pairs.sort(key=lambda x: (-len(x[0]), DOMAIN_ORDER.index(x[1]), x[0]))
    return pairs


def dictionary_hash() -> str:
    return text_hash([f"{kw}|{slug}|{grp}" for kw, slug, grp in build_domain_pairs()])


def claim_terms(vocab: list[str]) -> dict[int, tuple[str, str]]:
    """어휘 열 번호 → (도메인, 그룹). 긴 키워드가 먼저 점유하고, 정확 일치 후 부분 일치(길이≥2)."""
    term_pos = {t: i for i, t in enumerate(vocab)}
    claimed: dict[int, tuple[str, str]] = {}
    for kw, slug, grp in build_domain_pairs():
        if kw in term_pos and term_pos[kw] not in claimed:
            claimed[term_pos[kw]] = (slug, grp)
        if len(kw) >= 2:
            for j, term in enumerate(vocab):
                if j not in claimed and kw in term:
                    claimed[j] = (slug, grp)
    return claimed


def map_topics(H: np.ndarray, vocab: list[str]) -> pd.DataFrame:
    """학습 H 행렬과 학습 어휘, 고정 키워드 사전만으로 토픽→국면을 결정한다.

    토픽 번호는 어떤 규칙에도 쓰이지 않는다. 입력은 (H, vocab) 둘뿐이다.
    규칙: 최고 도메인 질량 점유율 < MIN_MAP_SHARE → residual,
          2위/1위 질량비 ≥ MASS_TIE_RATIO → ambiguous, 그 외 → assigned.
    """
    claimed = claim_terms(vocab)
    by_domain: dict[str, list[int]] = {s: [] for s in DOMAIN_ORDER}
    for j, (slug, _grp) in claimed.items():
        by_domain[slug].append(j)
    rows: list[dict[str, Any]] = []
    for k in range(H.shape[0]):
        total = float(H[k].sum()) or 1.0
        masses = {s: float(H[k, idx].sum()) if idx else 0.0 for s, idx in by_domain.items()}
        ranked = sorted(masses.items(), key=lambda x: (-x[1], DOMAIN_ORDER.index(x[0])))
        (best_s, best_m), (second_s, second_m) = ranked[0], ranked[1]
        share = best_m / total
        ratio = second_m / best_m if best_m > 0 else float("nan")
        if best_m <= 0 or share < MIN_MAP_SHARE:
            status, slug_out = "residual", ""
            reason = f"최고 도메인({best_s}) 질량 점유율 {share:.4f} < {MIN_MAP_SHARE}"
        elif ratio >= MASS_TIE_RATIO:
            status, slug_out = "ambiguous", ""
            reason = f"1위 {best_s}/2위 {second_s} 질량비 {ratio:.3f} >= {MASS_TIE_RATIO}"
        else:
            status, slug_out = "assigned", best_s
            reason = f"{best_s} 질량 점유율 {share:.4f}, 2위/1위 {ratio:.3f}"
        # 최고 도메인 내부의 그룹 질량 (전기차배터리 등 한정 근거 식별용)
        grp_mass: Counter[str] = Counter()
        for j in by_domain[best_s]:
            grp_mass[claimed[j][1]] += float(H[k, j])
        dom_group = sorted(grp_mass.items(), key=lambda x: (-x[1], x[0]))[0][0] if grp_mass else ""
        claimed_top = sorted(by_domain[best_s], key=lambda j: (-float(H[k, j]), j))[:6]
        top_idx = np.lexsort((np.arange(H.shape[1]), -H[k]))[:TOP_TERMS]
        row: dict[str, Any] = {
            "topic": k,
            "status": status,
            "assigned_slug": slug_out,
            "assigned_label": DOMAIN_SPEC[slug_out]["label"] if slug_out else "",
            "best_slug": best_s,
            "best_mass": best_m,
            "best_share": share,
            "second_slug": second_s,
            "second_mass": second_m,
            "mass_ratio": ratio,
            "confidence": (1.0 - ratio) if status == "assigned" else float("nan"),
            "dominant_group": dom_group,
            "top_terms": ", ".join(vocab[j] for j in top_idx),
            "claimed_top_terms": ", ".join(vocab[j] for j in claimed_top),
            "reason": reason,
        }
        for s in DOMAIN_ORDER:
            row[f"mass_{s}"] = masses[s]
            row[f"share_{s}"] = masses[s] / total
        rows.append(row)
    return pd.DataFrame(rows)


def mapping_hash(df_map: pd.DataFrame) -> str:
    cols = [c for c in df_map.columns if c not in ("run_id",)]
    return sha256_bytes(df_map[cols].to_csv(index=False, float_format="%.10g").encode("utf-8"))


def domain_topics(df_map: pd.DataFrame) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {s: [] for s in DOMAIN_ORDER}
    for _, r in df_map[df_map["status"] == "assigned"].iterrows():
        out[r["assigned_slug"]].append(int(r["topic"]))
    return out


def domain_support(df_map: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """지원 상태. 미지원 국면은 비중 0이 아니라 unrepresented 로 표기한다."""
    topics = domain_topics(df_map)
    out: dict[str, dict[str, Any]] = {}
    for s in DOMAIN_ORDER:
        ks = topics[s]
        if not ks:
            cand = df_map[(df_map["best_slug"] == s) & (df_map["status"] != "assigned")]["topic"].astype(int).tolist()
            out[s] = {
                "status": "unrepresented",
                "topics": [],
                "note": "학습 H에서 임계값·모호성 규칙을 통과한 토픽 없음"
                + (f" (최고 후보였으나 residual/ambiguous: {cand})" if cand else ""),
            }
            continue
        groups = {str(df_map.loc[df_map["topic"] == k, "dominant_group"].iloc[0]) for k in ks}
        if s == "aichip" and groups == {EV_GROUP}:
            out[s] = {"status": "supported_ev_battery_only", "topics": ks,
                      "note": "지지 근거가 사전의 전기차배터리 그룹뿐이며 AI·반도체 직접 근거는 아님"}
        else:
            out[s] = {"status": "supported", "topics": ks, "note": f"우세 키워드 그룹: {sorted(groups)}"}
    return out


# ======================================================================= 코어(학습) 단계
def run_core(corpus_path: Path, run_id: str, art_dir: Path, subsample: int = 1) -> dict[str, Any]:
    t_start = time.time()
    art_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[Core] run_id={run_id}  artifacts={art_dir}", flush=True)

    # ---- 1. 적재·정리·안정 정렬
    tbl = pq.read_table(corpus_path, columns=["article_id", "month", "keywords"]).to_pandas()
    n_raw = len(tbl)
    n_null_id = int(tbl["article_id"].isna().sum())
    n_null_month = int(tbl["month"].isna().sum())
    n_null_kw = int(tbl["keywords"].isna().sum())
    tbl = tbl[tbl["article_id"].notna() & tbl["month"].notna() & tbl["keywords"].notna()]
    blank = tbl["keywords"].str.strip() == ""
    n_blank_kw = int(blank.sum())
    tbl = tbl[~blank]
    tbl = tbl.sort_values(["month", "article_id", "keywords"], kind="mergesort").reset_index(drop=True)
    n_dup_id = int(tbl["article_id"].duplicated().sum())
    tbl = tbl.drop_duplicates(subset="article_id", keep="first").reset_index(drop=True)
    if subsample > 1:
        tbl = tbl.iloc[::subsample].reset_index(drop=True)
    months = tbl["month"].to_numpy()
    ids = tbl["article_id"].to_numpy()
    kws = tbl["keywords"].tolist()
    n_docs = len(tbl)
    n_train = int((months <= TRAIN_END).sum())
    n_eval = int((months >= EVAL_START).sum())
    assert n_train + n_eval == n_docs and bool((months[:n_train] <= TRAIN_END).all())
    assert n_train == 0 or n_train == n_docs or months[n_train] >= EVAL_START
    counts = {
        "raw_rows": n_raw, "null_article_id": n_null_id, "null_month": n_null_month,
        "null_keywords": n_null_kw, "blank_keywords": n_blank_kw, "duplicate_article_id_removed": n_dup_id,
        "after_cleaning": n_docs, "train_docs": n_train, "eval_docs": n_eval,
        "subsample_every_k": subsample,
    }
    print(f"  docs raw={n_raw:,} clean={n_docs:,} train={n_train:,} eval={n_eval:,}", flush=True)

    # ---- 2. 어휘: 학습 기간 DF만 사용
    counter: Counter[str] = Counter()
    for cell in kws[:n_train]:
        counter.update(_tokens(cell))
    df_doc_max_month = str(months[:n_train].max())
    ordered = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    kept = [(t, c) for t, c in ordered if c >= MIN_DF and c / n_train <= MAX_DF_RATIO][:TOP_N_VOCAB]
    vocab = [t for t, _ in kept]
    vocab_df = np.array([c for _, c in kept], dtype=np.int64)
    vocab_index = {t: i for i, t in enumerate(vocab)}
    V = len(vocab)
    print(f"  vocab={V:,} (unique tokens in train={len(counter):,})", flush=True)

    # ---- 3. 학습 표본: 학습 기간 월별 층화(안정 정렬 위치 기준)
    rng = np.random.default_rng(SEED)
    parts = []
    for m in np.unique(months[:n_train]):
        idx = np.flatnonzero(months[:n_train] == m)
        take = min(PER_MONTH_SAMPLE, int(idx.size))
        parts.append(np.sort(rng.choice(idx, size=take, replace=False)))
    sample_pos = np.concatenate(parts)
    assert int(sample_pos.max()) < n_train
    n_sample = int(sample_pos.size)
    sample_ids = [str(ids[p]) for p in sample_pos]
    sample_months = months[sample_pos]
    print(f"  fit sample={n_sample:,} docs", flush=True)

    # ---- 4. 전량 문서-어휘 행렬(이진)
    batches = []
    for s in range(0, n_docs, BATCH):
        cols: list[int] = []
        lens = np.empty(min(BATCH, n_docs - s), dtype=np.int32)
        for i, cell in enumerate(kws[s:s + BATCH]):
            hit = sorted({vocab_index[t] for t in _tokens(cell) if t in vocab_index})
            cols.extend(hit)
            lens[i] = len(hit)
        indptr = np.zeros(len(lens) + 1, dtype=np.int64)
        np.cumsum(lens, out=indptr[1:])
        batches.append(sparse.csr_matrix(
            (np.ones(len(cols), dtype=np.float32), np.array(cols, dtype=np.int32), indptr),
            shape=(len(lens), V)))
    X_all = sparse.vstack(batches, format="csr")
    X_sample = X_all[sample_pos]
    n_zero_term_docs = int((np.diff(X_all.indptr) == 0).sum())

    # ---- 5. TF-IDF·NMF: 학습 표본만으로 적합
    tfidf = TfidfTransformer(norm="l2", use_idf=True, smooth_idf=True, sublinear_tf=False)
    Xt_sample = tfidf.fit_transform(X_sample)
    sample_df = np.bincount(X_sample.indices, minlength=V)
    idf_expected = np.log((1.0 + X_sample.shape[0]) / (1.0 + sample_df)) + 1.0
    idf_indep_maxdiff = float(np.max(np.abs(idf_expected - tfidf.idf_)))

    nmf = NMF(n_components=N_TOPICS, init=NMF_INIT, solver=NMF_SOLVER, beta_loss="frobenius",
              max_iter=NMF_MAX_ITER, random_state=SEED, verbose=0)
    with warnings.catch_warnings(record=True) as wlist:
        warnings.simplefilter("always")
        nmf.fit(Xt_sample)
    converge_warn = any(issubclass(w.category, ConvergenceWarning) for w in wlist)
    H = nmf.components_.copy()
    idf_hash = arr_hash(tfidf.idf_)
    H_hash_fit = arr_hash(H)
    print(f"  NMF fit: n_iter={nmf.n_iter_} converged={not converge_warn}", flush=True)

    # ---- 6. 고정 모델 transform → 월별 토픽 비중
    uniq_months = sorted(set(months.tolist()))
    sums = {m: np.zeros(N_TOPICS, dtype=np.float64) for m in uniq_months}
    n_docs_m: Counter[str] = Counter()
    n_valid_m: Counter[str] = Counter()
    for s in range(0, n_docs, BATCH):
        W = nmf.transform(tfidf.transform(X_all[s:s + BATCH]))
        tot = W.sum(axis=1)
        ok = tot > 0
        sh = np.zeros(W.shape, dtype=np.float64)
        sh[ok] = (W[ok] / tot[ok, None]).astype(np.float64)
        mb = months[s:s + BATCH]
        for m in np.unique(mb):
            mask = mb == m
            okm = mask & ok
            n_docs_m[m] += int(mask.sum())
            n_valid_m[m] += int(okm.sum())
            sums[m] += sh[okm].sum(axis=0)
    H_hash_after = arr_hash(nmf.components_)
    idf_hash_after = arr_hash(tfidf.idf_)
    rows = []
    for m in uniq_months:
        v = n_valid_m[m]
        mean_s = sums[m] / v if v > 0 else np.full(N_TOPICS, np.nan)
        if v > 0:
            mean_s = mean_s / mean_s.sum()
        r: dict[str, Any] = {"month": m, "n_docs": n_docs_m[m], "n_valid": v}
        for k in range(N_TOPICS):
            r[f"topic_{k}"] = float(mean_s[k])
        rows.append(r)
    df_topic = pd.DataFrame(rows)

    # ---- 7. 아티팩트 저장
    vocab_csv = art_dir / "vocab_idf.csv"
    pd.DataFrame({"index": range(V), "term": vocab, "df_train": vocab_df, "idf": tfidf.idf_}).to_csv(
        vocab_csv, index=False, encoding="utf-8-sig")
    np.save(art_dir / "nmf_H.npy", H)
    pd.DataFrame({"order": range(n_sample), "article_id": sample_ids, "month": sample_months}).to_csv(
        art_dir / "fit_sample_ids.csv", index=False, encoding="utf-8")
    df_topic.to_csv(art_dir / "monthly_topic_share.csv", index=False, encoding="utf-8")
    joblib.dump({"tfidf": tfidf, "nmf": nmf, "vocab": vocab}, art_dir / "models.joblib")

    try:
        from threadpoolctl import threadpool_info
        tp_info = threadpool_info()
    except Exception:  # pragma: no cover
        tp_info = []
    core_meta = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "counts": counts,
        "vocab_size": V,
        "vocab_sha256": text_hash(vocab),
        "idf_sha256": idf_hash,
        "idf_sha256_after_transform": idf_hash_after,
        "idf_independent_recompute_maxdiff": idf_indep_maxdiff,
        "H_sha256": H_hash_fit,
        "H_sha256_after_transform": H_hash_after,
        "sample_ids_sha256": text_hash(sample_ids),
        "n_fit_sample": n_sample,
        "fit_sample_month_range": [str(sample_months.min()), str(sample_months.max())],
        "df_docs_max_month": df_doc_max_month,
        "n_df_docs": n_train,
        "n_zero_in_vocab_term_docs": n_zero_term_docs,
        "nmf_params": {k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v))
                       for k, v in nmf.get_params().items()},
        "nmf_n_iter": int(nmf.n_iter_),
        "nmf_converged_no_warning": (not converge_warn),
        "nmf_reconstruction_err": float(nmf.reconstruction_err_),
        "tfidf_params": {k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v))
                         for k, v in tfidf.get_params().items()},
        "environment": {
            "python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__, "pandas": pd.__version__, "statsmodels": statsmodels.__version__,
            "platform": platform.platform(), "thread_env": {v: os.environ.get(v) for v in (
                "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")},
            "threadpool_info": [{k: v for k, v in d.items() if k in ("internal_api", "num_threads", "version")}
                                for d in tp_info],
        },
        "dictionary_sha256": dictionary_hash(),
        "elapsed_sec": round(time.time() - t_start, 1),
    }
    (art_dir / "core_meta.json").write_text(json.dumps(core_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  core done in {core_meta['elapsed_sec']}s", flush=True)
    return {"meta": core_meta, "vocab": vocab, "vocab_df": vocab_df, "H": H, "df_topic": df_topic,
            "sample_months": sample_months, "tfidf": tfidf, "nmf": nmf, "art_dir": art_dir}


# ======================================================================= 월별 국면 특징
def build_regime_monthly(df_topic: pd.DataFrame, df_map: pd.DataFrame, run_id: str) -> pd.DataFrame:
    """share_d(m)=Σ_{k∈K_d} topic_k(m);  residual(m)=Σ_{k∈K_res} topic_k(m);  Σ_d share_d + residual = 1.
    미지원 국면은 NaN(비중 0이 아님). K_res = 미배정(residual/ambiguous) 토픽. Z는 학습 48개월 mean/std(ddof=1)."""
    topics = domain_topics(df_map)
    support = domain_support(df_map)
    res_topics = df_map[df_map["status"] != "assigned"]["topic"].astype(int).tolist()
    out = pd.DataFrame({"run_id": run_id, "month": df_topic["month"], "n_docs": df_topic["n_docs"],
                        "n_valid": df_topic["n_valid"]})
    out["period"] = np.where(out["month"] <= TRAIN_END, "train", "eval")
    for s in DOMAIN_ORDER:
        out[f"status_{s}"] = support[s]["status"]
    for s in DOMAIN_ORDER:
        ks = topics[s]
        out[f"share_{s}"] = df_topic[[f"topic_{k}" for k in ks]].sum(axis=1).to_numpy() if ks else np.nan
    out["residual_share"] = (df_topic[[f"topic_{k}" for k in res_topics]].sum(axis=1).to_numpy()
                             if res_topics else 0.0)
    comp = [f"share_{s}" for s in DOMAIN_ORDER if topics[s]] + ["residual_share"]
    assert np.allclose(out[comp].sum(axis=1), 1.0, atol=1e-9), "월별 비중 합이 1이 아님"
    tr = out["month"] <= TRAIN_END
    assert int(tr.sum()) == 48
    for s in DOMAIN_ORDER:
        if topics[s]:
            mu = float(out.loc[tr, f"share_{s}"].mean())
            sd = float(out.loc[tr, f"share_{s}"].std(ddof=1))
            out[f"z_{s}"] = (out[f"share_{s}"] - mu) / sd
        else:
            out[f"z_{s}"] = np.nan
    return out


# ======================================================================= 예측
def _design(df: pd.DataFrame, ycol: str, xcol: str, ny: int, nx: int, end: int, news: bool) -> tuple[pd.DataFrame, pd.Series]:
    start = max(ny, nx)
    rows = []
    for i in range(start, end):
        r = {"y": df[ycol].iloc[i]}
        for L in range(1, ny + 1):
            r[f"y_lag{L}"] = df[ycol].iloc[i - L]
        if news:
            for L in range(1, nx + 1):
                r[f"x_lag{L}"] = df[xcol].iloc[i - L]
        rows.append(r)
    d = pd.DataFrame(rows)
    return sm.add_constant(d.drop(columns="y"), has_constant="add"), d["y"]


def _predict(df: pd.DataFrame, t: int, ycol: str, xcol: str, ny: int, nx: int, news: bool, end: int) -> float:
    """end=학습에 쓰는 마지막 행의 다음 위치(확장창은 end=t, 고정창은 end=평가 시작 위치)."""
    X, y = _design(df, ycol, xcol, ny, nx, end, news)
    res = sm.OLS(y, X).fit()
    val = float(res.params["const"])
    for L in range(1, ny + 1):
        val += float(res.params[f"y_lag{L}"]) * float(df[ycol].iloc[t - L])
    if news:
        for L in range(1, nx + 1):
            val += float(res.params[f"x_lag{L}"]) * float(df[xcol].iloc[t - L])
    return val


def run_forecasts(df_regime: pd.DataFrame, panel_path: Path, run_id: str, h1_col: str, h2_col: str,
                  ok_h1: bool, ok_h2: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(panel_path, dtype={"month": str})
    df = df_regime.merge(panel[["month", "kospi_ret", "base_rate_diff"]], on="month", how="inner")
    df = df[(df["month"] >= STUDY_START) & (df["month"] <= EVAL_END)].sort_values("month").reset_index(drop=True)
    ev = df[(df["month"] >= EVAL_START) & (df["month"] <= EVAL_END)]["month"].tolist()
    assert len(ev) == 19, f"평가월 {len(ev)}개"
    i0 = int(df.index[df["month"] == EVAL_START][0])
    recs = []
    for m in ev:
        t = int(df.index[df["month"] == m][0])
        a1, a2 = float(df["kospi_ret"].iloc[t]), float(df["base_rate_diff"].iloc[t])
        nan = float("nan")
        p = {
            "h1_ar2_exp": _predict(df, t, "kospi_ret", h1_col, 2, 2, False, t),
            "h1_news_exp": _predict(df, t, "kospi_ret", h1_col, 2, 2, True, t) if ok_h1 else nan,
            "h1_ar2_fix": _predict(df, t, "kospi_ret", h1_col, 2, 2, False, i0),
            "h1_news_fix": _predict(df, t, "kospi_ret", h1_col, 2, 2, True, i0) if ok_h1 else nan,
            "h2_ar1_exp": _predict(df, t, "base_rate_diff", h2_col, 1, 1, False, t),
            "h2_news_exp": _predict(df, t, "base_rate_diff", h2_col, 1, 1, True, t) if ok_h2 else nan,
            "h2_ar1_fix": _predict(df, t, "base_rate_diff", h2_col, 1, 1, False, i0),
            "h2_news_fix": _predict(df, t, "base_rate_diff", h2_col, 1, 1, True, i0) if ok_h2 else nan,
        }
        rec: dict[str, Any] = {
            "run_id": run_id, "forecast_month": m, "last_available_obs_month": df["month"].iloc[t - 1],
            "actual_kospi_ret": a1, "h1_zero_pred": 0.0,
            "h1_ar2_exp_pred": p["h1_ar2_exp"], "h1_news_exp_pred": p["h1_news_exp"],
            "h1_ar2_fix_pred": p["h1_ar2_fix"], "h1_news_fix_pred": p["h1_news_fix"],
            "actual_base_rate_diff": a2, "h2_zero_pred": 0.0,
            "h2_ar1_exp_pred": p["h2_ar1_exp"], "h2_news_exp_pred": p["h2_news_exp"],
            "h2_ar1_fix_pred": p["h2_ar1_fix"], "h2_news_fix_pred": p["h2_news_fix"],
        }
        recs.append(rec)
    out = pd.DataFrame(recs)
    for tag, act in (("h1", "actual_kospi_ret"), ("h2", "actual_base_rate_diff")):
        for name in ("zero", "ar2_exp" if tag == "h1" else "ar1_exp", "news_exp",
                     "ar2_fix" if tag == "h1" else "ar1_fix", "news_fix"):
            out[f"{tag}_{name}_error"] = out[f"{tag}_{name}_pred"] - out[act]
    return out, df


MODEL_SPECS = {
    "h1": [("zero", "Zero 기준선"), ("ar2_exp", "[확장창] AR(2)"), ("news_exp", "[확장창] AR(2)+News"),
           ("ar2_fix", "[고정창] AR(2)"), ("news_fix", "[고정창] AR(2)+News")],
    "h2": [("zero", "Zero-change 기준선"), ("ar1_exp", "[확장창] AR(1)"), ("news_exp", "[확장창] AR(1)+News"),
           ("ar1_fix", "[고정창] AR(1)"), ("news_fix", "[고정창] AR(1)+News")],
}
ACTUAL_COL = {"h1": "actual_kospi_ret", "h2": "actual_base_rate_diff"}


def cont_metrics(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    if np.isnan(pred).any():
        return {"rmse": float("nan"), "mae": float("nan"), "bias": float("nan")}
    e = pred - actual
    return {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))), "bias": float(np.mean(e))}


def class_metrics(pred: np.ndarray, actual: np.ndarray) -> dict[str, Any] | None:
    if np.isnan(pred).any():
        return None
    pos, neg = actual < 0, actual >= 0
    pp, pn = pred < 0, pred >= 0
    tp, fp = int((pos & pp).sum()), int((neg & pp).sum())
    fn, tn = int((pos & pn).sum()), int((neg & pn).sum())
    n, n_pos, n_neg = len(actual), int(pos.sum()), int(neg.sum())
    ids = (tp + fn == n_pos, tn + fp == n_neg, tp + tn == int((pos & pp).sum() + (neg & pn).sum()),
           tp + tn + fp + fn == n)
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    bal = (rec + spec) / 2 if not (is_nan(rec) or is_nan(spec)) else float("nan")
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn, "hits": tp + tn, "n": n, "n_pos": n_pos, "n_neg": n_neg,
            "recall": rec, "precision": prec, "specificity": spec, "balanced": bal, "identities_ok": all(ids)}


def compute_all_metrics(df_f: pd.DataFrame) -> dict[str, Any]:
    m: dict[str, Any] = {"n": len(df_f)}
    for tag in ("h1", "h2"):
        act = df_f[ACTUAL_COL[tag]].to_numpy()
        for key, _ in MODEL_SPECS[tag]:
            m[f"{tag}_{key}"] = cont_metrics(df_f[f"{tag}_{key}_pred"].to_numpy(), act)
    act1 = df_f["actual_kospi_ret"].to_numpy()
    n = len(df_f)
    m["class"] = {
        "always_pos": class_metrics(np.ones(n), act1), "always_neg": class_metrics(-np.ones(n), act1),
        "exp_base": class_metrics(df_f["h1_ar2_exp_pred"].to_numpy(), act1),
        "exp_news": class_metrics(df_f["h1_news_exp_pred"].to_numpy(), act1),
        "fix_base": class_metrics(df_f["h1_ar2_fix_pred"].to_numpy(), act1),
        "fix_news": class_metrics(df_f["h1_news_fix_pred"].to_numpy(), act1),
    }
    return m


# ======================================================================= 보고서
def _rel_table(m: dict[str, Any], tag: str, base_exp: str, base_fix: str) -> list[str]:
    spec = MODEL_SPECS[tag]
    z, be = m[f"{tag}_zero"], m[f"{tag}_{base_exp}"]
    same = {"news_exp": base_exp, "news_fix": base_fix}
    lines = []
    for key, name in spec:
        c = m[f"{tag}_{key}"]
        def cell(base: dict[str, float] | None, self_ref: bool) -> tuple[str, str]:
            if self_ref:
                return "기준", "기준"
            if base is None or is_nan(c["rmse"]) or is_nan(base["rmse"]):
                return "N/A", "N/A"
            r, a = improvement(base["rmse"], c["rmse"]), improvement(base["mae"], c["mae"])
            return f"{fpct(r)} ({verdict_word(r)})", f"{fpct(a)} ({verdict_word(a)})"
        vz = cell(z, key == "zero")
        ve = cell(be, key == base_exp)
        if key in same:
            vs = cell(m[f"{tag}_{same[key]}"], False)
        elif key in (base_exp, base_fix):
            vs = ("기준", "기준")
        else:
            vs = ("해당 없음", "해당 없음")
        lines.append(f"| {name} <!--id:{tag}_{key}--> | {fnum(c['rmse'])} | {fnum(c['mae'])} | {fnum(c['bias'])} "
                     f"| {vz[0]} | {vz[1]} | {ve[0]} | {ve[1]} | {vs[0]} | {vs[1]} |")
    return lines


def cross_run_rows(root: Path) -> list[str]:
    reac = root / "data" / "processed" / "reactions"
    files = [("Phase 5 (원본)", "phase5_strict_oos_forecast.csv"), ("Phase 5 (v2)", "phase5_strict_oos_forecast_v2.csv"),
             ("Phase 5.2", "phase5_2_strict_oos_forecast.csv")]
    rows = []
    for label, fn in files:
        p = reac / fn
        if not p.exists():
            rows.append(f"| {label} | 파일 없음 | | | | | |")
            continue
        d = pd.read_csv(p)
        vals = []
        for tag, key in (("h1", "news_exp"), ("h1", "news_fix"), ("h2", "news_exp"), ("h2", "news_fix")):
            col = f"{tag}_{key}_pred"
            vals.append(cont_metrics(d[col].to_numpy(), d[ACTUAL_COL[tag]].to_numpy())["rmse"])
        rows.append(f"| {label} | {fnum(vals[0])} | {fnum(vals[1])} | {fnum(vals[2], 5)} | {fnum(vals[3], 5)} |")
    return rows


def render_markdown(ctx: dict[str, Any]) -> str:
    meta, m, df_map, support = ctx["meta"], ctx["metrics"], ctx["df_map"], ctx["support"]
    L: list[str] = []
    A = L.append
    A(f"# Phase 5.6 — 결정론적 Strict OOS 최종 실험 결과")
    A("")
    A(f"- 실행 ID: `{ctx['run_id']}`")
    A(f"- 스크립트: `analysis/validate_strict_oos_forecast_v4.py` (버전 `{SCRIPT_VERSION}`)")
    A(f"- 실행 시각: {ctx['started_kst']} (KST) / {ctx['started_utc']} (UTC)")
    A(f"- 학습 기간(텍스트 파이프라인·표준화·고정창 회귀): {STUDY_START} ~ {TRAIN_END} (48개월)")
    A(f"- 평가 기간: {EVAL_START} ~ {EVAL_END} ({m['n']}개월)")
    A("")
    A("## 1. 데이터 계보와 표본 수")
    c = meta["counts"]
    A("")
    A(f"- 입력: `{ctx['corpus_rel']}` (SHA-256 `{ctx['corpus_sha']}`)")
    A(f"- 입력: `{ctx['panel_rel']}` (SHA-256 `{ctx['panel_sha']}`)")
    A("")
    A("| 단계 | 건수 |")
    A("| :--- | ---: |")
    A(f"| 원본 행 수 | {c['raw_rows']:,} |")
    A(f"| article_id·month·keywords 결측 / 공백 keywords 제거 | {c['null_article_id'] + c['null_month'] + c['null_keywords'] + c['blank_keywords']:,} |")
    A(f"| article_id 중복 제거(정렬 후 첫 행 유지) | {c['duplicate_article_id_removed']:,} |")
    A(f"| 정리 후 분석 기사 | {c['after_cleaning']:,} |")
    A(f"| 학습 기사 (month ≤ {TRAIN_END}) | {c['train_docs']:,} |")
    A(f"| 평가 기사 (month ≥ {EVAL_START}) | {c['eval_docs']:,} |")
    A(f"| NMF·IDF 적합 표본 (월별 최대 {PER_MONTH_SAMPLE:,}건, seed={SEED}) | {meta['n_fit_sample']:,} |")
    A(f"| 어휘에 해당 토큰이 하나도 없는 기사(월별 비중 분모에서 제외) | {meta['n_zero_in_vocab_term_docs']:,} |")
    A("")
    A("처리 규칙: 정리는 결측·공백 제거와 article_id 중복 제거만 수행한다(본문 중복·매체·길이 필터링 없음). "
      "정렬 키는 (month, article_id, keywords), 안정 정렬(mergesort). 월별 표본은 정렬된 위치에서 "
      "`numpy.random.default_rng(seed)`로 비복원 추출하고 위치 오름차순으로 저장한다. "
      "표본 문서 ID 목록은 아티팩트 `fit_sample_ids.csv`에 있다.")
    ec = EXPECTED_COUNTS
    A("")
    A(f"기대 표본 수와의 대조: 원본 {c['raw_rows']:,}/{ec['raw']:,}, 학습 {c['train_docs']:,}/{ec['train']:,}, "
      f"평가 {c['eval_docs']:,}/{ec['eval']:,}, 적합 표본 {meta['n_fit_sample']:,}/{ec['fit_sample']:,}.")
    A("")
    A("## 2. 텍스트 파이프라인 설정과 아티팩트")
    A("")
    A("| 항목 | 값 |")
    A("| :--- | :--- |")
    A(f"| 어휘 | DF ≥ {MIN_DF}, DF/N ≤ {MAX_DF_RATIO}, 상한 {TOP_N_VOCAB:,}, 정렬 (−DF, 토큰) → {meta['vocab_size']:,}개 |")
    A(f"| 어휘 해시 | `{meta['vocab_sha256']}` |")
    A(f"| IDF 해시 | `{meta['idf_sha256']}` |")
    A(f"| 학습 표본 ID 해시 | `{meta['sample_ids_sha256']}` |")
    A(f"| NMF | n_components={N_TOPICS}, init=`{NMF_INIT}`, solver=`{NMF_SOLVER}`, max_iter={NMF_MAX_ITER}, random_state={SEED} |")
    A(f"| NMF 실제 반복 / 경고 없는 종료 | {meta['nmf_n_iter']} / {meta['nmf_converged_no_warning']} |")
    A(f"| H 행렬 해시 | `{meta['H_sha256']}` |")
    A(f"| 매핑 해시 | `{ctx['map_sha']}` |")
    A(f"| 키워드 사전 해시 | `{meta['dictionary_sha256']}` |")
    env = meta["environment"]
    A(f"| 환경 | Python {env['python']}, NumPy {env['numpy']}, SciPy {env['scipy']}, scikit-learn {env['scikit_learn']}, "
      f"statsmodels {env['statsmodels']}, 스레드 환경변수 {env['thread_env']} |")
    A(f"| 아티팩트 디렉터리 | `{ctx['art_rel']}` |")
    A("")
    A("## 3. 토픽-국면 매핑 (토픽 번호 비의존)")
    A("")
    A(f"규칙: 고정 키워드 사전으로 어휘를 도메인에 배정 → 토픽별 도메인 질량 계산 → 최고 도메인 점유율 < {MIN_MAP_SHARE}이면 "
      f"`residual`, 2위/1위 질량비 ≥ {MASS_TIE_RATIO}이면 `ambiguous`, 그 외 `assigned`. 신뢰도 = 1 − (2위/1위).")
    A("")
    A("| 토픽 | 상위 단어(12) | 판정 | 배정 국면 | 1위 도메인 (점유율) | 2위 도메인 | 2위/1위 | 신뢰도 | 우세 그룹 | 사유 |")
    A("| ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | :--- | :--- |")
    for _, r in df_map.iterrows():
        tt = ", ".join(str(r["top_terms"]).split(", ")[:12])
        A(f"| {int(r['topic'])} | {tt} | {r['status']} | {r['assigned_label'] or '—'} | "
          f"{r['best_slug']} ({r['best_share']:.4f}) | {r['second_slug']} | {fnum(r['mass_ratio'], 3)} | "
          f"{fnum(r['confidence'], 3)} | {r['dominant_group']} | {r['reason']} |")
    A("")
    A("### 8개 국면 지원 상태")
    A("")
    A("| 국면 | 코드 | 상태 | 연결 토픽 | 비고 |")
    A("| :--- | :--- | :--- | :--- | :--- |")
    for s in DOMAIN_ORDER:
        sp = support[s]
        A(f"| {DOMAIN_SPEC[s]['label']} | `{s}` | {sp['status']} | {sp['topics'] or '—'} | {sp['note']} |")
    A("")
    A("미지원(`unrepresented`) 국면의 월별 비중은 CSV에서 0이 아니라 빈 값(NaN)이다. 그 토픽 질량은 `residual_share`에 포함된다.")
    A("월별 비중 정의: 문서별 토픽 비중 w_k/Σw를 만들고(Σw=0 문서 제외) 월 평균 topic_k(m)을 구한 뒤, "
      "share_d(m)=Σ_{k∈d} topic_k(m), residual_share(m)=Σ_{k 미배정} topic_k(m). 합은 1이다.")
    A("")
    A("### 회귀 특징 연결")
    A("")
    A(f"- H1 뉴스 특징: 국면 `{H1_DOMAIN}` → 토픽 {support[H1_DOMAIN]['topics']} → 열 `share_{H1_DOMAIN}` (시차 1, 2)")
    A(f"- H2 뉴스 특징: 국면 `{H2_DOMAIN}` → 토픽 {support[H2_DOMAIN]['topics']} → 열 `share_{H2_DOMAIN}` (시차 1)")
    A("")
    A("## 4. H1 — 코스피 월간 수익률 예측")
    A("")
    A("개선율 = 100 × (기준 오차 − 모형 오차) / 기준 오차. 양수는 오차 감소, 음수는 오차 증가. "
      "‘동일창 AR 대비’는 확장창 모형은 확장창 AR(2), 고정창 모형은 고정창 AR(2)를 분모로 쓴다.")
    A("")
    A("| 모형 | RMSE | MAE | Bias | Zero 대비 RMSE | Zero 대비 MAE | 확장창 AR(2) 대비 RMSE | 확장창 AR(2) 대비 MAE | 동일창 AR(2) 대비 RMSE | 동일창 AR(2) 대비 MAE |")
    A("| :--- | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- |")
    L.extend(_rel_table(m, "h1", "ar2_exp", "ar2_fix"))
    A("")
    cl = m["class"]
    n_pos = (cl["always_pos"] or cl["always_neg"])["n_pos"]
    n_neg = (cl["always_pos"] or cl["always_neg"])["n_neg"]
    A(f"### H1 방향 분류 (양성=하락월: 실제 < 0, 평가 {m['n']}개월 중 하락월 {n_pos}, 비하락월 {n_neg})")
    A("")
    A("| 모형 | TP | TN | FP | FN | 방향 적중 | 하락 재현율 | 하락 정밀도 | 특이도 | 균형 정확도 |")
    A("| :--- | ---: | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- |")
    for key, name in (("always_pos", "Always Positive"), ("always_neg", "Always Negative"),
                      ("exp_base", "[확장창] AR(2)"), ("exp_news", "[확장창] AR(2)+News"),
                      ("fix_base", "[고정창] AR(2)"), ("fix_news", "[고정창] AR(2)+News")):
        r = cl[key]
        if r is None:
            A(f"| {name} <!--cls:{key}--> | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        A(f"| {name} <!--cls:{key}--> | {r['tp']} | {r['tn']} | {r['fp']} | {r['fn']} | {fratio(r['hits'], r['n'])} | "
          f"{fratio(r['tp'], r['tp'] + r['fn'])} | {fratio(r['tp'], r['tp'] + r['fp'])} | "
          f"{fratio(r['tn'], r['tn'] + r['fp'])} | {'정의 불가' if is_nan(r['balanced']) else f'{100 * r['balanced']:.1f}%'} |")
    A("")
    A("## 5. H2 — 한국은행 기준금리 변화 예측")
    A("")
    A("| 모형 | RMSE | MAE | Bias | Zero-change 대비 RMSE | Zero-change 대비 MAE | 확장창 AR(1) 대비 RMSE | 확장창 AR(1) 대비 MAE | 동일창 AR(1) 대비 RMSE | 동일창 AR(1) 대비 MAE |")
    A("| :--- | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- |")
    L.extend(_rel_table(m, "h2", "ar1_exp", "ar1_fix"))
    A("")
    A("## 6. 관찰 요약 (표본 내 관찰이며 통계 검정은 수행하지 않음)")
    A("")
    e_r = improvement(m["h1_ar2_exp"]["rmse"], m["h1_news_exp"]["rmse"])
    f_r = improvement(m["h1_ar2_fix"]["rmse"], m["h1_news_fix"]["rmse"])
    A(f"- H1 확장창: 가계대출 뉴스 추가 시 동일창 AR(2) 대비 RMSE {fpct(e_r)} ({verdict_word(e_r)}).")
    A(f"- H1 고정창: 동일창 AR(2) 대비 RMSE {fpct(f_r)} ({verdict_word(f_r)}).")
    he_r = improvement(m["h2_ar1_exp"]["rmse"], m["h2_news_exp"]["rmse"])
    hf_r = improvement(m["h2_ar1_fix"]["rmse"], m["h2_news_fix"]["rmse"])
    A(f"- H2 확장창: 금리·물가 뉴스 추가 시 동일창 AR(1) 대비 RMSE {fpct(he_r)} ({verdict_word(he_r)}).")
    A(f"- H2 고정창: 동일창 AR(1) 대비 RMSE {fpct(hf_r)} ({verdict_word(hf_r)}).")
    zr = {k: improvement(m["h2_zero"]["rmse"], m[f"h2_{k}"]["rmse"]) for k in ("ar1_exp", "news_exp", "ar1_fix", "news_fix")}
    A("- H2 Zero-change 대비 RMSE: " + ", ".join(f"{k} {fpct(v)}" for k, v in zr.items()) + ".")
    ce = cl["exp_news"]
    if ce:
        A(f"- H1 확장창 News 방향 적중 {ce['hits']}/{ce['n']}, 하락 정밀도 {fratio(ce['tp'], ce['tp'] + ce['fp'])}, "
          f"단순 상승 기준선 적중 {cl['always_pos']['hits']}/{ce['n']}.")
    A("")
    A("## 7. 이전 실행과의 비교 (뉴스 모형 RMSE, 각 CSV에서 재계산)")
    A("")
    A("| 실행 | H1 확장창 News | H1 고정창 News | H2 확장창 News | H2 고정창 News |")
    A("| :--- | ---: | ---: | ---: | ---: |")
    L.extend(ctx["cross_rows"])
    A(f"| **Phase 5.6 (본 실행)** | {fnum(m['h1_news_exp']['rmse'])} | {fnum(m['h1_news_fix']['rmse'])} | "
      f"{fnum(m['h2_news_exp']['rmse'], 5)} | {fnum(m['h2_news_fix']['rmse'], 5)} |")
    A("")
    A("## 8. 자동 감사 요약")
    A("")
    A("| 번호 | 항목 | 판정 | 근거 |")
    A("| :--- | :--- | :--- | :--- |")
    for name, ch in ctx["checks"].items():
        A(f"| {name.split('_', 1)[0]} | {name.split('_', 1)[1]} | {ch['status']} | {ch['detail']} |")
    A("")
    A("보고서 지표와 CSV의 일치, 산출물 간 실행 ID 일치, 최종 파일 해시는 이 파일이 작성된 뒤 JSON 감사에서 추가로 확인한다.")
    A("")
    A("## 9. 한계")
    A("")
    A(f"- 평가 표본은 {m['n']}개월이고 하락월은 {n_pos}개월이다. 통계적 유의성 검정은 수행하지 않았으므로 "
      "위 차이를 유의한 개선 또는 일반화 가능한 예측력으로 해석하지 않는다.")
    A("- 키워드 사전 기반 국면 매핑은 사전의 어휘 범위에 의존한다. 사전의 해석 적합성은 상위 단어로 사람이 확인해야 하며 "
      "자동 감사는 규칙 재현성만 검증한다.")
    A("- 같은 코드·입력의 반복 실행 일치는 이 환경(스레드 1개)에서 확인한 것이며 다른 환경에서의 일치는 확인하지 않았다.")
    return "\n".join(L) + "\n"


# ======================================================================= 감사
def _chk(status: bool | None, detail: str, **ev: Any) -> dict[str, Any]:
    return {"status": "PASS" if status is True else "FAIL" if status is False else "INSUFFICIENT EVIDENCE",
            "detail": detail, "evidence": ev}


def independent_mapping(H: np.ndarray, vocab: list[str]) -> list[tuple[str, str, float]]:
    """map_topics 와 다른 구현(어휘 중심 점유)으로 (status, slug, best_mass)를 다시 계산한다."""
    pairs = build_domain_pairs()
    owner: list[str | None] = []
    for term in vocab:
        hit = None
        for kw, slug, _g in pairs:
            if kw == term or (len(kw) >= 2 and kw in term):
                hit = slug
                break
        owner.append(hit)
    own = np.array([o if o else "" for o in owner])
    res = []
    for k in range(H.shape[0]):
        total = H[k].sum()
        masses = [(float(H[k][own == s].sum()), i, s) for i, s in enumerate(DOMAIN_ORDER)]
        masses.sort(key=lambda x: (-x[0], x[1]))
        (bm, _, bs), (sm_, _, _s2) = masses[0], masses[1]
        if bm <= 0 or bm / total < MIN_MAP_SHARE:
            res.append(("residual", "", bm))
        elif sm_ / bm >= MASS_TIE_RATIO:
            res.append(("ambiguous", "", bm))
        else:
            res.append(("assigned", bs, bm))
    return res


def pre_md_checks(ctx: dict[str, Any]) -> dict[str, Any]:
    meta, H, vocab = ctx["meta"], ctx["H"], ctx["vocab"]
    art = ctx["art_dir"]
    checks: dict[str, Any] = {}
    c = meta["counts"]

    ec = EXPECTED_COUNTS
    ok = (c["raw_rows"], c["train_docs"], c["eval_docs"], meta["n_fit_sample"]) == (ec["raw"], ec["train"], ec["eval"], ec["fit_sample"])
    checks["01_데이터 표본 수"] = _chk(ok, f"원본 {c['raw_rows']:,}, 학습 {c['train_docs']:,}, 평가 {c['eval_docs']:,}, 적합 표본 {meta['n_fit_sample']:,} "
                                    f"(기대 {ec['raw']:,}/{ec['train']:,}/{ec['eval']:,}/{ec['fit_sample']:,})", counts=c)

    vdf = pd.read_csv(art / "vocab_idf.csv", encoding="utf-8-sig")
    terms = vdf["term"].astype(str).tolist()
    ordered = all((vdf["df_train"].iloc[i], terms[i]) is not None for i in range(1)) and \
        all((-int(vdf["df_train"].iloc[i]), terms[i]) <= (-int(vdf["df_train"].iloc[i + 1]), terms[i + 1]) for i in range(len(vdf) - 1))
    rules = bool((vdf["df_train"] >= MIN_DF).all() and (vdf["df_train"] / c["train_docs"] <= MAX_DF_RATIO).all()
                 and len(vdf) <= TOP_N_VOCAB)
    ok = ordered and rules and meta["df_docs_max_month"] <= TRAIN_END and meta["n_df_docs"] == c["train_docs"] \
        and text_hash(terms) == meta["vocab_sha256"] and terms == vocab
    checks["02_어휘·DF 학습기간 한정과 정렬 규칙"] = _chk(ok, f"DF 계산 기사 {meta['n_df_docs']:,}건, 최대 월 {meta['df_docs_max_month']}, "
                                                    f"저장된 어휘표에서 DF 규칙 {rules}, (−DF,토큰) 정렬 {ordered}, 해시 일치", vocab_size=len(terms))

    sid = pd.read_csv(art / "fit_sample_ids.csv", dtype=str)
    ok = bool((sid["month"] <= TRAIN_END).all()) and len(sid) == meta["n_fit_sample"] and sid["article_id"].is_unique \
        and text_hash(sid["article_id"].tolist()) == meta["sample_ids_sha256"] and meta["idf_independent_recompute_maxdiff"] < 1e-5
    checks["03_IDF 적합 표본(학습기간) 및 IDF 독립 재계산"] = _chk(
        ok, f"표본 {len(sid):,}건 월 범위 {sid['month'].min()}~{sid['month'].max()}, 표본 DF로 재계산한 IDF 최대 차 {meta['idf_independent_recompute_maxdiff']:.2e}")

    ok = H.shape == (N_TOPICS, len(vocab)) and bool((H >= 0).all()) and meta["nmf_params"].get("max_iter") == NMF_MAX_ITER \
        and meta["nmf_params"].get("init") == NMF_INIT and meta["nmf_params"].get("random_state") == SEED \
        and meta["nmf_params"].get("n_components") == N_TOPICS and meta["n_fit_sample"] == len(sid)
    conv = meta["nmf_converged_no_warning"]
    checks["04_NMF 적합 입력과 설정"] = _chk(ok, f"H {H.shape}, 비음수, 파라미터 {meta['nmf_params']}, 반복 {meta['nmf_n_iter']}, 수렴 경고 없음={conv}",
                                          converged=conv)

    ok = meta["H_sha256"] == meta["H_sha256_after_transform"] and meta["idf_sha256"] == meta["idf_sha256_after_transform"]
    checks["05_평가기간 기사는 transform만 적용(H·IDF 불변)"] = _chk(ok, "전량 transform 전후 H·IDF 해시 동일")

    H_disk = np.load(art / "nmf_H.npy")
    ok_h = arr_hash(H_disk) == meta["H_sha256"]
    df_map = ctx["df_map"]
    ind = independent_mapping(H_disk, terms)
    same = all(ind[k][0] == df_map.loc[df_map["topic"] == k, "status"].iloc[0]
               and ind[k][1] == ("" if pd.isna(df_map.loc[df_map["topic"] == k, "assigned_slug"].iloc[0])
                                else str(df_map.loc[df_map["topic"] == k, "assigned_slug"].iloc[0]))
               and abs(ind[k][2] - float(df_map.loc[df_map["topic"] == k, "best_mass"].iloc[0])) < 1e-6 * max(1.0, abs(ind[k][2]))
               for k in range(N_TOPICS))
    params = list(inspect.signature(map_topics).parameters)
    ok = ok_h and same and params == ["H", "vocab"]
    checks["06_매핑이 학습 H·학습 어휘·고정 사전만 사용하고 독립 구현과 일치"] = _chk(
        ok, f"저장된 H(해시 일치 {ok_h})와 저장된 어휘로 다른 구현이 14개 토픽 판정·질량을 재현 {same}; map_topics 인자 {params}")

    sig = {k: (df_map.loc[df_map["topic"] == k, "status"].iloc[0], df_map.loc[df_map["topic"] == k, "assigned_slug"].iloc[0])
           for k in range(N_TOPICS)}
    perm_ok = True
    for sd in range(5):
        perm = np.random.default_rng(sd).permutation(N_TOPICS)
        m2 = map_topics(H_disk[perm], terms)
        for i in range(N_TOPICS):
            if (m2.loc[m2["topic"] == i, "status"].iloc[0], m2.loc[m2["topic"] == i, "assigned_slug"].iloc[0]) != sig[int(perm[i])]:
                perm_ok = False
    checks["07_토픽 번호 재정렬 불변성(무작위 순열 5회)"] = _chk(perm_ok, "H 행을 무작위로 재정렬해도 각 토픽의 판정이 상위 단어를 따라 이동")

    reg = pd.read_csv(ctx["regime_path"])
    tr = reg["month"] <= TRAIN_END
    zok = True
    for s in DOMAIN_ORDER:
        if reg[f"share_{s}"].notna().all():
            z = (reg[f"share_{s}"] - reg.loc[tr, f"share_{s}"].mean()) / reg.loc[tr, f"share_{s}"].std(ddof=1)
            zok &= bool(np.allclose(z, reg[f"z_{s}"], atol=1e-10)) and int(tr.sum()) == 48
        else:
            zok &= bool(reg[f"z_{s}"].isna().all())
    checks["08_Z-score 모수 학습 48개월 한정"] = _chk(zok, f"저장된 월별 CSV에서 {STUDY_START}~{TRAIN_END} {int(tr.sum())}개월 평균·표준편차(ddof=1)로 z를 재계산해 일치")

    topics = domain_topics(df_map)
    dtp = pd.read_csv(art / "monthly_topic_share.csv")
    link_ok = True
    has_unrep = False
    link_detail: list[str] = []
    for dom, col in ((H1_DOMAIN, f"share_{H1_DOMAIN}"), (H2_DOMAIN, f"share_{H2_DOMAIN}")):
        ks = topics[dom]
        if not ks:
            has_unrep = True
            link_detail.append(f"{dom}: unrepresented (학습 H에서 독립 국면 미형성)")
            continue
        rec = dtp[[f"topic_{k}" for k in ks]].sum(axis=1).to_numpy()
        match = bool(np.allclose(rec, reg[col].to_numpy(), atol=1e-12))
        link_ok &= match
        link_detail.append(f"{dom}→토픽{ks}→{col}(일치={match})")
    fc = pd.read_csv(ctx["forecast_path"])
    mon = reg.set_index("month")
    lag_ok = True
    for _, r in fc.iterrows():
        prev = mon.index[mon.index.get_loc(r["forecast_month"]) - 1]
        lag_ok &= (r["last_available_obs_month"] == prev) and (r["last_available_obs_month"] < r["forecast_month"])
    status_09 = False if not link_ok else (None if has_unrep else True)
    checks["09_H1·H2 특징 연결 재현"] = _chk(status_09, "; ".join(link_detail) + " — 월별 토픽 아티팩트와 매핑으로 특징 열 정합성 확인")
    checks["10_시차 정합(대상월 t는 직전월까지의 정보)"] = _chk(bool(lag_ok), "19개월 전수 last_available_obs_month = 대상월의 직전월")

    df = ctx["df_study"]
    perturb_ok = True
    maxdiff = 0.0
    for m in fc["forecast_month"]:
        t = int(df.index[df["month"] == m][0])
        bad = df.copy()
        bad.loc[bad.index >= t, ["kospi_ret", "base_rate_diff", f"share_{H1_DOMAIN}", f"share_{H2_DOMAIN}"]] = 1.0e6
        row = fc[fc["forecast_month"] == m].iloc[0]
        for tag, y, x, ny, nx, col in (("h1", "kospi_ret", f"share_{H1_DOMAIN}", 2, 2, "h1_ar2_exp_pred"),
                                       ("h1", "kospi_ret", f"share_{H1_DOMAIN}", 2, 2, "h1_news_exp_pred"),
                                       ("h2", "base_rate_diff", f"share_{H2_DOMAIN}", 1, 1, "h2_ar1_exp_pred"),
                                       ("h2", "base_rate_diff", f"share_{H2_DOMAIN}", 1, 1, "h2_news_exp_pred")):
            if is_nan(row[col]):
                continue
            p = _predict_with_future(bad, t, y, x, ny, nx, "news" in col)
            maxdiff = max(maxdiff, abs(p - float(row[col])))
    perturb_ok = maxdiff < 1e-8
    checks["11_확장창 회귀가 대상월 이후 종속변수·특징을 쓰지 않음(교란 시험)"] = _chk(
        perturb_ok, f"대상월 이후 값을 1e6으로 교란해도 19개월×4모형 예측 최대 변화 {maxdiff:.2e}")

    ind_max = 0.0
    for _, row in fc.iterrows():
        t = int(df.index[df["month"] == row["forecast_month"]].tolist()[0])
        for tag, y, x, ny, nx in (("h1", "kospi_ret", f"share_{H1_DOMAIN}", 2, 2), ("h2", "base_rate_diff", f"share_{H2_DOMAIN}", 1, 1)):
            for news in (False, True):
                for win in ("exp", "fix"):
                    col = f"{tag}_{'news' if news else ('ar2' if tag == 'h1' else 'ar1')}_{win}_pred"
                    if is_nan(row[col]):
                        continue
                    end = t if win == "exp" else int(df.index[df["month"] == EVAL_START][0])
                    p = _numpy_predict(df, t, y, x, ny, nx, news, end)
                    ind_max = max(ind_max, abs(p - float(row[col])))
    checks["12_예측 독립 재현(numpy lstsq, 저장 CSV 기준)"] = _chk(ind_max < 1e-8, f"statsmodels 예측과 numpy 최소제곱 재구현의 최대 차 {ind_max:.2e}")

    cls_valid = [r for r in ctx["metrics"]["class"].values() if r is not None]
    m_ids = len(cls_valid) > 0 and all(r["identities_ok"] for r in cls_valid)
    checks["13_혼동행렬 항등식 4종"] = _chk(m_ids, f"TP+FN=하락월, TN+FP=비하락월, TP+TN=적중, 합=N 을 {len(cls_valid)}개 지원 모형에서 확인")

    if ctx["rerun_dir"] is None or not (Path(ctx["rerun_dir"]) / "core_meta.json").exists():
        checks["14_동일 입력·설정 재실행 일치"] = _chk(None, "재실행 아티팩트가 없어 비교하지 못함")
    else:
        rd = Path(ctx["rerun_dir"])
        rm = json.loads((rd / "core_meta.json").read_text(encoding="utf-8"))
        same_hash = {k: rm[k] == meta[k] for k in ("vocab_sha256", "idf_sha256", "sample_ids_sha256", "H_sha256")}
        r_topic = pd.read_csv(rd / "monthly_topic_share.csv")
        f_topic = pd.read_csv(art / "monthly_topic_share.csv")
        cols = [f"topic_{k}" for k in range(N_TOPICS)]
        md = float(np.nanmax(np.abs(r_topic[cols].to_numpy() - f_topic[cols].to_numpy())))
        r_map = map_topics(np.load(rd / "nmf_H.npy"), pd.read_csv(rd / "vocab_idf.csv", encoding="utf-8-sig")["term"].astype(str).tolist())
        same_map = mapping_hash(r_map) == ctx["map_sha"]
        ok = all(same_hash.values()) and md == 0.0 and same_map and r_topic["n_docs"].tolist() == f_topic["n_docs"].tolist()
        checks["14_동일 입력·설정 재실행 일치"] = _chk(
            ok, f"별도 프로세스 재실행({rm['run_id']})과 해시 일치 {same_hash}, 월별 토픽 비중 최대 차 {md:.2e}, 매핑 해시 일치 {same_map}")

    checks["15_평가기간 정보가 특징 선택·적합에 쓰이지 않음"] = _chk(
        meta["fit_sample_month_range"][1] <= TRAIN_END and meta["df_docs_max_month"] <= TRAIN_END
        and params == ["H", "vocab"] and ctx["panel_loaded_after_mapping"],
        f"적합 표본 월 ≤ {meta['fit_sample_month_range'][1]}, DF 기사 월 ≤ {meta['df_docs_max_month']}, "
        f"매핑 함수 입력은 H·vocab 뿐이며 패널(수익률·금리)은 매핑 확정 이후에 읽음")
    return checks


def _predict_with_future(df: pd.DataFrame, t: int, y: str, x: str, ny: int, nx: int, news: bool) -> float:
    return _predict(df, t, y, x, ny, nx, news, t)


def _numpy_predict(df: pd.DataFrame, t: int, y: str, x: str, ny: int, nx: int, news: bool, end: int) -> float:
    start = max(ny, nx)
    yv, xv = df[y].to_numpy(), df[x].to_numpy()
    rows, tgt = [], []
    for i in range(start, end):
        r = [1.0] + [yv[i - L] for L in range(1, ny + 1)]
        if news:
            r += [xv[i - L] for L in range(1, nx + 1)]
        rows.append(r)
        tgt.append(yv[i])
    beta = np.linalg.lstsq(np.array(rows), np.array(tgt), rcond=None)[0]
    q = [1.0] + [yv[t - L] for L in range(1, ny + 1)]
    if news:
        q += [xv[t - L] for L in range(1, nx + 1)]
    return float(np.dot(beta, np.array(q)))


def post_md_checks(ctx: dict[str, Any], md_path: Path, files: dict[str, Path]) -> dict[str, Any]:
    """MD 작성 후: CSV에서 다시 계산한 지표가 MD 표의 모든 셀과 일치하는지, 실행 ID 일치를 확인."""
    checks: dict[str, Any] = {}
    md = md_path.read_text(encoding="utf-8")
    fc = pd.read_csv(files["forecast"])
    mism: list[str] = []
    n_cells = 0

    def cells(tag: str) -> list[str] | None:
        for line in md.splitlines():
            if f"<!--{tag}-->" in line:
                return [c.strip() for c in line.strip().strip("|").split("|")]
        return None

    num = re.compile(r"[+-]?\d+\.\d+")
    ind: dict[str, dict[str, float]] = {}
    for tag in ("h1", "h2"):
        act = fc[ACTUAL_COL[tag]].to_numpy()
        for key, _n in MODEL_SPECS[tag]:
            pr = fc[f"{tag}_{key}_pred"].to_numpy()
            if np.isnan(pr).any():
                ind[f"{tag}_{key}"] = {"rmse": float("nan"), "mae": float("nan"), "bias": float("nan")}
            else:
                e = pr - act
                ind[f"{tag}_{key}"] = {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))), "bias": float(np.mean(e))}
    for tag, base_exp, base_fix in (("h1", "ar2_exp", "ar2_fix"), ("h2", "ar1_exp", "ar1_fix")):
        nd = 4 if tag == "h1" else 5
        for key, _n in MODEL_SPECS[tag]:
            row = cells(f"id:{tag}_{key}")
            if row is None:
                mism.append(f"{tag}_{key}: 행 없음")
                continue
            c = ind[f"{tag}_{key}"]
            if np.isnan(c["rmse"]):
                exp_vals = ["N/A", "N/A", "N/A"]
            else:
                exp_vals = [f"{c['rmse']:.4f}", f"{c['mae']:.4f}", f"{c['bias']:.4f}"]
            for j, ev in enumerate(exp_vals, start=1):
                n_cells += 1
                if row[j] != ev:
                    mism.append(f"{tag}_{key} col{j}: MD {row[j]} vs CSV {ev}")
            z, be = ind[f"{tag}_zero"], ind[f"{tag}_{base_exp}"]
            same = {"news_exp": base_exp, "news_fix": base_fix}
            refs = [(4, z, key == "zero"), (6, be, key == base_exp)]
            if key in same:
                refs.append((8, ind[f"{tag}_{same[key]}"], False))
            for j0, base, selfref in refs:
                if selfref:
                    continue
                for off, met in ((0, "rmse"), (1, "mae")):
                    n_cells += 1
                    if np.isnan(c[met]) or np.isnan(base[met]):
                        if not row[j0 + off].startswith("N/A"):
                            mism.append(f"{tag}_{key} improvement col{j0 + off}: MD {row[j0 + off]} vs CSV N/A")
                    else:
                        val = 100.0 * (base[met] - c[met]) / base[met]
                        got = num.findall(row[j0 + off])
                        if not got or f"{val:+.2f}" != got[0]:
                            mism.append(f"{tag}_{key} improvement col{j0 + off}: MD {row[j0 + off]} vs CSV {val:+.2f}")
    # 분류표
    act1 = fc["actual_kospi_ret"].to_numpy()
    nrow = len(fc)
    cls_pred = {"always_pos": np.ones(nrow), "always_neg": -np.ones(nrow), "exp_base": fc["h1_ar2_exp_pred"].to_numpy(),
                "exp_news": fc["h1_news_exp_pred"].to_numpy(), "fix_base": fc["h1_ar2_fix_pred"].to_numpy(),
                "fix_news": fc["h1_news_fix_pred"].to_numpy()}
    for key, pr in cls_pred.items():
        row = cells(f"cls:{key}")
        if row is None:
            mism.append(f"cls_{key}: 행 없음")
            continue
        if np.isnan(pr).any():
            n_cells += 1
            if row[1] != "N/A":
                mism.append(f"cls_{key} N/A row: MD {row[1]}")
            continue
        pos, neg = act1 < 0, act1 >= 0
        pp = pr < 0
        tp, fp = int((pos & pp).sum()), int((neg & pp).sum())
        fn, tn = int((pos & ~pp).sum()), int((neg & ~pp).sum())
        for j, v in zip((1, 2, 3, 4), (tp, tn, fp, fn)):
            n_cells += 1
            if row[j] != str(v):
                mism.append(f"cls_{key} col{j}: MD {row[j]} vs CSV {v}")
        n_cells += 1
        if not row[5].startswith(f"{100 * (tp + tn) / nrow:.1f}% ({tp + tn}/{nrow})"):
            mism.append(f"cls_{key} hits: MD {row[5]}")
    checks["16_MD의 모든 지표 셀이 CSV 재계산값과 일치"] = _chk(len(mism) == 0, f"비교 셀 {n_cells}개, 불일치 {len(mism)}개" + (f": {mism[:5]}" if mism else ""))

    run_id = ctx["run_id"]
    rid_ok = {}
    for name, p in files.items():
        txt = p.read_text(encoding="utf-8-sig") if p.suffix != ".json" else p.read_text(encoding="utf-8")
        rid_ok[name] = run_id in txt
    rid_ok["artifact_meta"] = json.loads((ctx["art_dir"] / "core_meta.json").read_text(encoding="utf-8"))["run_id"] == run_id
    checks["17_산출물 실행 ID 일치"] = _chk(all(rid_ok.values()), f"실행 ID {run_id} 포함 여부: {rid_ok}")

    reg_cols_ok = all(c in pd.read_csv(files["regime"], nrows=1).columns for c in ("run_id", "month", "n_docs", "residual_share"))
    map_df = pd.read_csv(files["mapping"], encoding="utf-8-sig")
    once = sorted(map_df["topic"].tolist()) == list(range(N_TOPICS)) and map_df["topic"].is_unique
    checks["18_14개 토픽 각 1회 명시·중복 배정 없음"] = _chk(once and reg_cols_ok, f"토픽 {sorted(map_df['topic'].tolist())}, 각 토픽은 한 행(한 판정)")
    return checks


def overall_verdict(checks: dict[str, Any]) -> str:
    st = [c["status"] for c in checks.values()]
    if "FAIL" in st:
        return "REMAINS INCOMPLETE"
    if "INSUFFICIENT EVIDENCE" in st:
        return "PARTIALLY VERIFIED"
    return "TECHNICAL VALIDATION COMPLETE"


# ======================================================================= main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core-only", action="store_true")
    ap.add_argument("--artifact-root", default=str(ROOT / "data" / "processed" / "phase5_6_artifacts"))
    ap.add_argument("--deliver-dir", default=str(ROOT / "data" / "processed" / "reactions"))
    ap.add_argument("--rerun-dir", default=None)
    ap.add_argument("--subsample", type=int, default=1, help="개발용: N번째 문서마다 사용(최종 실행은 1)")
    args = ap.parse_args()

    now = dt.datetime.now(KST)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    corpus_path = ROOT / "data" / "processed" / "corpus" / "news_corpus.parquet"
    panel_path = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
    art_root = Path(args.artifact_root)

    if args.core_only:
        run_id = f"RUN_PHASE5_6_CORE_{stamp}"
        run_core(corpus_path, run_id, art_root / run_id, args.subsample)
        print(f"\ncore-only 완료: {art_root / run_id}")
        return

    run_id = f"RUN_PHASE5_6_{stamp}"
    deliver = Path(args.deliver_dir)
    deliver.mkdir(parents=True, exist_ok=True)
    art_dir = art_root / run_id
    corpus_sha, panel_sha = sha256_file(corpus_path), sha256_file(panel_path)
    print(f"corpus sha={corpus_sha}\npanel  sha={panel_sha}", flush=True)

    core = run_core(corpus_path, run_id, art_dir, args.subsample)
    meta, H, vocab = core["meta"], core["H"], core["vocab"]

    df_map = map_topics(H, vocab)
    map_sha = mapping_hash(df_map)
    support = domain_support(df_map)
    df_map.insert(0, "run_id", run_id)
    paths = {k: safe_path(deliver / f"phase5_6_{v}") for k, v in {
        "forecast": "strict_oos_forecast.csv", "regime": "train_only_regime_monthly.csv",
        "mapping": "topic_regime_mapping.csv", "audit": "pipeline_audit.json", "md": "strict_oos_forecast.md"}.items()}
    df_map.to_csv(paths["mapping"], index=False, encoding="utf-8-sig")
    print(df_map[["topic", "status", "assigned_slug", "best_slug", "best_share", "mass_ratio"]].to_string(), flush=True)

    df_regime = build_regime_monthly(core["df_topic"], df_map, run_id)
    df_regime.to_csv(paths["regime"], index=False, encoding="utf-8-sig")
    panel_loaded_after_mapping = True  # 패널은 아래에서 처음 읽는다(run_forecasts 내부)

    ok_h1, ok_h2 = support[H1_DOMAIN]["status"].startswith("supported"), support[H2_DOMAIN]["status"].startswith("supported")
    df_f, df_study = run_forecasts(df_regime, panel_path, run_id, f"share_{H1_DOMAIN}", f"share_{H2_DOMAIN}", ok_h1, ok_h2)
    df_f.to_csv(paths["forecast"], index=False, encoding="utf-8-sig")
    metrics = compute_all_metrics(df_f)

    ctx: dict[str, Any] = {
        "run_id": run_id, "meta": meta, "H": H, "vocab": vocab, "df_map": df_map, "support": support, "map_sha": map_sha,
        "metrics": metrics, "art_dir": art_dir, "regime_path": paths["regime"], "forecast_path": paths["forecast"],
        "df_study": df_study, "rerun_dir": args.rerun_dir, "panel_loaded_after_mapping": panel_loaded_after_mapping,
        "started_kst": now.strftime("%Y-%m-%d %H:%M:%S"), "started_utc": now.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "corpus_rel": str(corpus_path.relative_to(ROOT)).replace("\\", "/"), "corpus_sha": corpus_sha,
        "panel_rel": str(panel_path.relative_to(ROOT)).replace("\\", "/"), "panel_sha": panel_sha,
        "art_rel": str(art_dir.relative_to(ROOT)).replace("\\", "/") if art_dir.is_relative_to(ROOT) else str(art_dir),
        "cross_rows": cross_run_rows(ROOT),
    }
    pre = pre_md_checks(ctx)
    ctx["checks"] = pre
    paths["md"].write_text(render_markdown(ctx), encoding="utf-8")
    post = post_md_checks(ctx, paths["md"], {k: paths[k] for k in ("forecast", "regime", "mapping", "md")})
    checks = {**pre, **post}
    verdict = overall_verdict(checks)

    audit = {
        "run_id": run_id, "script_version": SCRIPT_VERSION,
        "started_kst": ctx["started_kst"], "started_utc": ctx["started_utc"],
        "inputs": {"news_corpus": {"path": ctx["corpus_rel"], "sha256": corpus_sha},
                   "monthly_panel": {"path": ctx["panel_rel"], "sha256": panel_sha}},
        "design": {"train": [STUDY_START, TRAIN_END], "eval": [EVAL_START, EVAL_END], "seed": SEED,
                   "min_df": MIN_DF, "max_df_ratio": MAX_DF_RATIO, "top_n_vocab": TOP_N_VOCAB, "n_topics": N_TOPICS,
                   "per_month_sample": PER_MONTH_SAMPLE, "nmf_max_iter": NMF_MAX_ITER, "nmf_init": NMF_INIT,
                   "min_map_share": MIN_MAP_SHARE, "mass_tie_ratio": MASS_TIE_RATIO},
        "core": meta,
        "mapping": {"sha256": map_sha, "domain_support": support,
                    "feature_links": {"H1": {"domain": H1_DOMAIN, "topics": support[H1_DOMAIN]["topics"], "column": f"share_{H1_DOMAIN}", "lags": [1, 2]},
                                      "H2": {"domain": H2_DOMAIN, "topics": support[H2_DOMAIN]["topics"], "column": f"share_{H2_DOMAIN}", "lags": [1]}}},
        "artifacts": {p.name: sha256_file(p) for p in sorted(art_dir.iterdir())},
        "deliverables": {k: {"path": str(paths[k].name), "sha256": sha256_file(paths[k])} for k in ("forecast", "regime", "mapping", "md")},
        "checks": checks,
        "overall_verdict": verdict,
        "notes": ["MD 작성 이후 항목(16~18)은 MD 파일 생성 뒤 실행됨", "이 JSON 자신의 해시는 포함되지 않음"],
    }
    paths["audit"].write_text(json.dumps(audit, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("\n=== AUDIT ===")
    for k, v in checks.items():
        print(f"{v['status']:<22} {k}  :: {v['detail'][:140]}")
    print(f"\nOVERALL: {verdict}\nrun_id={run_id}")
    for k, p in paths.items():
        print(f"{k}: {p}")


if __name__ == "__main__":
    main()
