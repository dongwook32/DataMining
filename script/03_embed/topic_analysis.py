"""Final paper: topic_analysis. See core/description.md."""
from __future__ import annotations

import os
import json
import platform
import sys
import time
import warnings
from collections import Counter
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import scipy
import sklearn
import statsmodels
from scipy import sparse
from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfTransformer
from core.preprocessing.mine_keywords import _tokens
from config.research import BATCH, EVAL_START, MAX_DF_RATIO, MIN_DF, NMF_INIT, NMF_MAX_ITER, NMF_SOLVER, N_TOPICS, PER_MONTH_SAMPLE, SCRIPT_VERSION, SEED, TOP_N_VOCAB, TRAIN_END
from util.research import arr_hash, text_hash
from core.regime_analysis import dictionary_hash


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
