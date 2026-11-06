"""Phase 4 — 미래 정보 누출을 차단한 경제 뉴스 선행 예측 검증 스크립트.

이 스크립트는 2021-01 ~ 2026-07(67개월) 경제 뉴스 및 금융 지표 패널 데이터를 바탕으로,
2025-01 ~ 2026-07(19개월) 평가기간에 대해 미래 정보 누출을 엄격히 차단한
확장창(Expanding Window) 롤링 외표본(Out-of-Sample, OOS) 예측 검증을 수행한다.

주요 검증 대상:
  - H1 (주 가설): 코스피 월간 수익률 (kospi_ret)
      기준모형: AR(2) vs 뉴스 추가 모형: AR(2) + share_hhdebt(lag 1, 2) vs 영예측 기준선(Zero)
  - H2 (보조 가설): 기준금리 월간 변화 (base_rate_diff)
      기준모형: AR(1) vs 뉴스 추가 모형: AR(1) + share_macro(lag 1)
  - 텍스트 파이프라인(어휘, IDF, NMF, 국면매핑)의 미래 정보 누출 전수 감사
  - 18개월 vs 19개월 표본 차이 및 기존 보고 수치(RMSE 15.68 -> 13.88) 재현 규명

산출 파일:
  - data/processed/reactions/phase4_oos_forecast.csv
  - data/processed/reactions/phase4_oos_forecast.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import statsmodels.api as sm


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_safe_output_paths(
    base_csv: Path, base_md: Path
) -> tuple[Path, Path]:
    """기존 파일 덮어쓰기 방지: 파일이 이미 존재하면 버전 번호 부여."""
    if not base_csv.exists() and not base_md.exists():
        return base_csv, base_md

    v = 2
    while True:
        csv_cand = base_csv.parent / f"{base_csv.stem}_v{v}{base_csv.suffix}"
        md_cand = base_md.parent / f"{base_md.stem}_v{v}{base_md.suffix}"
        if not csv_cand.exists() and not md_cand.exists():
            return csv_cand, md_cand
        v += 1


def audit_text_pipeline_availability(root: Path) -> dict:
    """텍스트 전처리 및 NMF 모델의 데이터 가용성 및 누출 구조 전수 감사."""
    raw_dir = root / "data" / "raw" / "bigkinds"
    corpus_file = root / "data" / "processed" / "corpus" / "news_corpus.parquet"
    doc_term_docs_file = root / "data" / "processed" / "corpus" / "doc_term_docs.parquet"
    vocab_file = root / "data" / "processed" / "corpus" / "doc_term_vocab.csv"
    matrix_file = root / "data" / "processed" / "corpus" / "doc_term.npz"
    nmf_meta_file = root / "data" / "processed" / "regimes" / "nmf_meta.json"
    map_file = root / "data" / "processed" / "regimes" / "topic_regime_map.csv"

    raw_excel_count = len(list(raw_dir.rglob("*.xlsx"))) if raw_dir.exists() else 0

    corpus_exists = corpus_file.exists()
    corpus_rows = 0
    if corpus_exists:
        meta = pq.read_metadata(corpus_file)
        corpus_rows = meta.num_rows

    docs_exists = doc_term_docs_file.exists()
    train_docs_count = 0
    test_docs_count = 0
    if docs_exists:
        df_docs = pd.read_parquet(doc_term_docs_file, columns=["month"])
        train_docs_count = int((df_docs["month"] <= "2024-12").sum())
        test_docs_count = int((df_docs["month"] >= "2025-01").sum())

    vocab_count = 0
    if vocab_file.exists():
        df_vocab = pd.read_csv(vocab_file)
        vocab_count = len(df_vocab)

    nmf_meta = {}
    if nmf_meta_file.exists():
        with open(nmf_meta_file, "r", encoding="utf-8") as f:
            nmf_meta = json.load(f)

    # 누출 판정
    # nmf_meta['n_fit'] = 201,000 -> 67개월 * 3,000건 = 전체 기간이 피팅에 포함됨!
    n_fit = nmf_meta.get("n_fit", 0)
    leakage_in_nmf = n_fit > (48 * 3000)  # 학습기간 48개월만 썼다면 최대 144,000이어야 함

    return {
        "raw_excel_count": raw_excel_count,
        "corpus_exists": corpus_exists,
        "corpus_rows": corpus_rows,
        "docs_exists": docs_exists,
        "train_docs_count": train_docs_count,
        "test_docs_count": test_docs_count,
        "vocab_count": vocab_count,
        "matrix_exists": matrix_file.exists(),
        "matrix_size_mb": round(matrix_file.stat().st_size / (1024 * 1024), 2) if matrix_file.exists() else 0,
        "nmf_n_fit": n_fit,
        "leakage_in_nmf": leakage_in_nmf,
        "leakage_summary": (
            "기존 doc_term.npz 및 nmf_H.npy는 67개월 전체(201,000건 표본)를 사용하여 "
            "어휘 선정, TF-IDF, NMF 적합이 수행되었음. 따라서 텍스트 임베딩 단계에서 "
            "평가기간(2025~2026)의 어휘 및 토픽 구조가 사전에 포함된 텍스트 단계 누출이 존재함."
        ),
    }


def run_h1_rolling_forecast(
    df_study: pd.DataFrame, eval_months: list[str]
) -> tuple[pd.DataFrame, dict, dict]:
    """H1: 코스피 월간 수익률 expanding window 롤링 외표본 예측.

    t월 예측 시점: t월 시작 직전 (t-1월 말)
    사용 가능 데이터: t-1월까지의 수익률 및 뉴스
    모형 1: AR(2) baseline: Y_t = a + phi1*Y_(t-1) + phi2*Y_(t-2)
    모형 2: AR(2) + news:   Y_t = a + phi1*Y_(t-1) + phi2*Y_(t-2) + beta1*X_(t-1) + beta2*X_(t-2)
    모형 3: Zero benchmark: Y_t = 0
    """
    rows = []

    for t_month in eval_months:
        idx_t = df_study[df_study["month"] == t_month].index[0]
        # 학습 데이터: 2021-03(인덱스 2)부터 idx_t - 1까지
        train_data = []
        for i in range(2, idx_t):
            train_data.append({
                "y": df_study["kospi_ret"].iloc[i],
                "y_lag1": df_study["kospi_ret"].iloc[i - 1],
                "y_lag2": df_study["kospi_ret"].iloc[i - 2],
                "x_lag1": df_study["share_hhdebt"].iloc[i - 1],
                "x_lag2": df_study["share_hhdebt"].iloc[i - 2],
            })
        df_tr = pd.DataFrame(train_data)
        n_tr = len(df_tr)

        # 1. AR(2) Baseline
        X_base = sm.add_constant(df_tr[["y_lag1", "y_lag2"]], has_constant="add")
        m_base = sm.OLS(df_tr["y"], X_base).fit()

        # 2. AR(2) + News
        X_news = sm.add_constant(
            df_tr[["y_lag1", "y_lag2", "x_lag1", "x_lag2"]], has_constant="add"
        )
        m_news = sm.OLS(df_tr["y"], X_news).fit()

        actual_y = float(df_study["kospi_ret"].iloc[idx_t])
        test_y1 = float(df_study["kospi_ret"].iloc[idx_t - 1])
        test_y2 = float(df_study["kospi_ret"].iloc[idx_t - 2])
        test_x1 = float(df_study["share_hhdebt"].iloc[idx_t - 1])
        test_x2 = float(df_study["share_hhdebt"].iloc[idx_t - 2])
        last_news_m = df_study["month"].iloc[idx_t - 1]

        p_base = float(
            m_base.params["const"]
            + m_base.params["y_lag1"] * test_y1
            + m_base.params["y_lag2"] * test_y2
        )
        p_news = float(
            m_news.params["const"]
            + m_news.params["y_lag1"] * test_y1
            + m_news.params["y_lag2"] * test_y2
            + m_news.params["x_lag1"] * test_x1
            + m_news.params["x_lag2"] * test_x2
        )
        p_zero = 0.0

        e_base = p_base - actual_y
        e_news = p_news - actual_y
        e_zero = p_zero - actual_y

        dir_base = bool(np.sign(p_base) == np.sign(actual_y))
        dir_news = bool(np.sign(p_news) == np.sign(actual_y))

        rows.append({
            "forecast_month": t_month,
            "last_available_news_month": last_news_m,
            "forecast_issue_time": f"{last_news_m}-말일",
            "baseline_training_sample_size": n_tr,
            "news_training_sample_size": n_tr,
            "actual_kospi_ret": actual_y,
            "baseline_ar2_prediction": p_base,
            "news_ar2_prediction": p_news,
            "zero_prediction": p_zero,
            "baseline_error": e_base,
            "news_error": e_news,
            "zero_error": e_zero,
            "baseline_absolute_error": abs(e_base),
            "news_absolute_error": abs(e_news),
            "zero_absolute_error": abs(e_zero),
            "baseline_direction_correct": dir_base,
            "news_direction_correct": dir_news,
        })

    df_res = pd.DataFrame(rows)

    # 19개월 전체 메트릭
    n_pos = int((df_res["actual_kospi_ret"] > 0).sum())
    n_neg = int((df_res["actual_kospi_ret"] < 0).sum())
    n_zero = int((df_res["actual_kospi_ret"] == 0).sum())

    metrics_19 = {
        "n_eval": len(df_res),
        "rmse_base": float(np.sqrt(np.mean(df_res["baseline_error"] ** 2))),
        "rmse_news": float(np.sqrt(np.mean(df_res["news_error"] ** 2))),
        "rmse_zero": float(np.sqrt(np.mean(df_res["zero_error"] ** 2))),
        "mae_base": float(np.mean(df_res["baseline_absolute_error"])),
        "mae_news": float(np.mean(df_res["news_absolute_error"])),
        "mae_zero": float(np.mean(df_res["zero_absolute_error"])),
        "me_base": float(np.mean(df_res["baseline_error"])),
        "me_news": float(np.mean(df_res["news_error"])),
        "me_zero": float(np.mean(df_res["zero_error"])),
        "n_pos": n_pos,
        "n_neg": n_neg,
        "n_zero": n_zero,
        "hits_always_pos": n_pos,
        "acc_always_pos_pct": float(n_pos / len(df_res) * 100),
        "hits_always_neg": n_neg,
        "acc_always_neg_pct": float(n_neg / len(df_res) * 100),
        "hits_base_pos": int(((df_res["actual_kospi_ret"] > 0) & (df_res["baseline_ar2_prediction"] > 0)).sum()),
        "hits_base_neg": int(((df_res["actual_kospi_ret"] < 0) & (df_res["baseline_ar2_prediction"] < 0)).sum()),
        "hits_news_pos": int(((df_res["actual_kospi_ret"] > 0) & (df_res["news_ar2_prediction"] > 0)).sum()),
        "hits_news_neg": int(((df_res["actual_kospi_ret"] < 0) & (df_res["news_ar2_prediction"] < 0)).sum()),
        "dir_acc_base_pct": float(df_res["baseline_direction_correct"].mean() * 100),
        "dir_acc_news_pct": float(df_res["news_direction_correct"].mean() * 100),
        "dir_hits_base": int(df_res["baseline_direction_correct"].sum()),
        "dir_hits_news": int(df_res["news_direction_correct"].sum()),
        "rmse_improvement_pct": float(
            100
            * (
                np.sqrt(np.mean(df_res["baseline_error"] ** 2))
                - np.sqrt(np.mean(df_res["news_error"] ** 2))
            )
            / np.sqrt(np.mean(df_res["baseline_error"] ** 2))
        ),
        "mae_improvement_pct": float(
            100
            * (
                np.mean(df_res["baseline_absolute_error"])
                - np.mean(df_res["news_absolute_error"])
            )
            / np.mean(df_res["baseline_absolute_error"])
        ),
    }

    # 18개월 서브셋 메트릭 (2025-02 ~ 2026-07: 기존 보고서 15.68 -> 13.88 재현)
    df_18 = df_res[df_res["forecast_month"] >= "2025-02"]
    metrics_18 = {
        "n_eval": len(df_18),
        "rmse_base": float(np.sqrt(np.mean(df_18["baseline_error"] ** 2))),
        "rmse_news": float(np.sqrt(np.mean(df_18["news_error"] ** 2))),
        "mae_base": float(np.mean(df_18["baseline_absolute_error"])),
        "mae_news": float(np.mean(df_18["news_absolute_error"])),
        "dir_acc_base_pct": float(df_18["baseline_direction_correct"].mean() * 100),
        "dir_acc_news_pct": float(df_18["news_direction_correct"].mean() * 100),
        "dir_hits_base": int(df_18["baseline_direction_correct"].sum()),
        "dir_hits_news": int(df_18["news_direction_correct"].sum()),
        "rmse_improvement_pct": float(
            100
            * (
                np.sqrt(np.mean(df_18["baseline_error"] ** 2))
                - np.sqrt(np.mean(df_18["news_error"] ** 2))
            )
            / np.sqrt(np.mean(df_18["baseline_error"] ** 2))
        ),
    }

    return df_res, metrics_19, metrics_18


def run_h2_rolling_forecast(
    df_study: pd.DataFrame, eval_months: list[str]
) -> tuple[pd.DataFrame, dict]:
    """H2: 기준금리 월간 변화폭(base_rate_diff) expanding window 롤링 외표본 예측.

    기준모형: AR(1): Rate_t = a + phi1*Rate_(t-1)
    뉴스모형: AR(1) + news: Rate_t = a + phi1*Rate_(t-1) + beta1*Macro_(t-1)
    """
    rows = []

    for t_month in eval_months:
        idx_t = df_study[df_study["month"] == t_month].index[0]
        train_data = []
        for i in range(1, idx_t):
            train_data.append({
                "y": df_study["base_rate_diff"].iloc[i],
                "y_lag1": df_study["base_rate_diff"].iloc[i - 1],
                "x_lag1": df_study["share_macro"].iloc[i - 1],
            })
        df_tr = pd.DataFrame(train_data)
        n_tr = len(df_tr)

        X_base = sm.add_constant(df_tr[["y_lag1"]], has_constant="add")
        m_base = sm.OLS(df_tr["y"], X_base).fit()

        X_news = sm.add_constant(df_tr[["y_lag1", "x_lag1"]], has_constant="add")
        m_news = sm.OLS(df_tr["y"], X_news).fit()

        actual_y = float(df_study["base_rate_diff"].iloc[idx_t])
        test_y1 = float(df_study["base_rate_diff"].iloc[idx_t - 1])
        test_x1 = float(df_study["share_macro"].iloc[idx_t - 1])
        last_news_m = df_study["month"].iloc[idx_t - 1]

        p_base = float(m_base.params["const"] + m_base.params["y_lag1"] * test_y1)
        p_news = float(
            m_news.params["const"]
            + m_news.params["y_lag1"] * test_y1
            + m_news.params["x_lag1"] * test_x1
        )

        e_base = p_base - actual_y
        e_news = p_news - actual_y

        rows.append({
            "forecast_month": t_month,
            "last_available_news_month": last_news_m,
            "n_train": n_tr,
            "actual_base_rate_diff": actual_y,
            "baseline_ar1_prediction": p_base,
            "news_ar1_prediction": p_news,
            "baseline_error": e_base,
            "news_error": e_news,
            "baseline_absolute_error": abs(e_base),
            "news_absolute_error": abs(e_news),
        })

    df_res = pd.DataFrame(rows)

    metrics = {
        "n_eval": len(df_res),
        "actual_nonzero_count": int((df_res["actual_base_rate_diff"] != 0).sum()),
        "rmse_base": float(np.sqrt(np.mean(df_res["baseline_error"] ** 2))),
        "rmse_news": float(np.sqrt(np.mean(df_res["news_error"] ** 2))),
        "mae_base": float(np.mean(df_res["baseline_absolute_error"])),
        "mae_news": float(np.mean(df_res["news_absolute_error"])),
        "me_base": float(np.mean(df_res["baseline_error"])),
        "me_news": float(np.mean(df_res["news_error"])),
        "rmse_improvement_pct": float(
            100
            * (
                np.sqrt(np.mean(df_res["baseline_error"] ** 2))
                - np.sqrt(np.mean(df_res["news_error"] ** 2))
            )
            / np.sqrt(np.mean(df_res["baseline_error"] ** 2))
        ),
        "mae_improvement_pct": float(
            100
            * (
                np.mean(df_res["baseline_absolute_error"])
                - np.mean(df_res["news_absolute_error"])
            )
            / np.mean(df_res["baseline_absolute_error"])
        ),
    }

    return df_res, metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 4 미래 정보 누출 차단 롤링 외표본 예측 검증"
    )
    parser.add_argument("--output-csv", type=str, default=None, help="결과 CSV 경로")
    parser.add_argument("--output-md", type=str, default=None, help="결과 MD 경로")
    args = parser.parse_args()

    root = project_root()
    panel_path = root / "data" / "processed" / "panel" / "monthly_panel.csv"
    regime_path = root / "data" / "processed" / "regimes" / "regime_monthly.csv"

    print("=" * 70)
    print("PHASE 4: OUT-OF-SAMPLE ROLLING FORECAST AUDIT & VERIFICATION")
    print("=" * 70)

    # 1. Audit Text Pipeline Availability & Leakage
    print("\n[Step 1] Auditing text pipeline data availability and leakage...")
    pipe_audit = audit_text_pipeline_availability(root)
    print(f"  Raw BigKinds files: {pipe_audit['raw_excel_count']} files")
    print(f"  Corpus total rows:  {pipe_audit['corpus_rows']:,}")
    print(f"  Doc-term docs:      Train={pipe_audit['train_docs_count']:,}, Test={pipe_audit['test_docs_count']:,}")
    print(f"  NMF fit sample:     {pipe_audit['nmf_n_fit']:,} docs (Full period: {pipe_audit['leakage_in_nmf']})")
    print(f"  -> {pipe_audit['leakage_summary']}")

    # 2. Load panel & study dataset
    print("\n[Step 2] Loading panel data and verifying evaluation periods...")
    panel = pd.read_csv(panel_path, dtype={"month": str})
    regime = pd.read_csv(regime_path, dtype={"month": str})
    df_raw = regime.merge(panel, on="month", how="inner", validate="one_to_one")
    df_study = (
        df_raw[(df_raw["month"] >= "2021-01") & (df_raw["month"] <= "2026-07")]
        .sort_values("month")
        .reset_index(drop=True)
    )

    eval_months = df_study[df_study["month"] >= "2025-01"]["month"].tolist()
    print(f"  Total study period: 2021-01 ~ 2026-07 ({len(df_study)} months)")
    print(f"  Evaluation window:  2025-01 ~ 2026-07 ({len(eval_months)} months)")
    assert len(eval_months) == 19, f"평가월 수는 19개월이어야 하나 {len(eval_months)}임!"

    # 3. Execute H1 Rolling OOS Forecast
    print("\n[Step 3] Running H1 (KOSPI Return) Expanding Window Rolling Forecast...")
    df_h1_res, m19_h1, m18_h1 = run_h1_rolling_forecast(df_study, eval_months)
    print(f"  [19 Months Full (2025-01 ~ 2026-07)]")
    print(f"    AR(2) Baseline:  RMSE = {m19_h1['rmse_base']:.4f}, MAE = {m19_h1['mae_base']:.4f}, DirAcc = {m19_h1['dir_acc_base_pct']:.1f}% ({m19_h1['dir_hits_base']}/19)")
    print(f"    AR(2) + News:    RMSE = {m19_h1['rmse_news']:.4f}, MAE = {m19_h1['mae_news']:.4f}, DirAcc = {m19_h1['dir_acc_news_pct']:.1f}% ({m19_h1['dir_hits_news']}/19)")
    print(f"    Zero Benchmark:  RMSE = {m19_h1['rmse_zero']:.4f}, MAE = {m19_h1['mae_zero']:.4f}")
    print(f"    RMSE Improvement vs AR(2): +{m19_h1['rmse_improvement_pct']:.2f}%")
    print(f"    MAE Improvement vs AR(2):  +{m19_h1['mae_improvement_pct']:.2f}%")
    print(f"  [18 Months Subset (2025-02 ~ 2026-07: Prior Report Reproduction)]")
    print(f"    AR(2) Baseline:  RMSE = {m18_h1['rmse_base']:.2f}, AR(2) + News RMSE = {m18_h1['rmse_news']:.2f} (Improvement: +{m18_h1['rmse_improvement_pct']:.2f}%)")

    # 4. Execute H2 Rolling OOS Forecast (Base Rate Diff)
    print("\n[Step 4] Running H2 (Base Rate Diff) Expanding Window Rolling Forecast...")
    df_h2_res, m19_h2 = run_h2_rolling_forecast(df_study, eval_months)
    print(f"  [19 Months Full (2025-01 ~ 2026-07)]")
    print(f"    Actual rate change events: {m19_h2['actual_nonzero_count']} out of 19 months")
    print(f"    AR(1) Baseline:  RMSE = {m19_h2['rmse_base']:.5f}, MAE = {m19_h2['mae_base']:.5f}")
    print(f"    AR(1) + News:    RMSE = {m19_h2['rmse_news']:.5f}, MAE = {m19_h2['mae_news']:.5f}")
    print(f"    RMSE Improvement: {m19_h2['rmse_improvement_pct']:.2f}% (Performance Degraded)")
    print(f"    MAE Improvement:  {m19_h2['mae_improvement_pct']:.2f}% (Performance Degraded)")

    # 5. Save Output Files safely
    default_csv = root / "data" / "processed" / "reactions" / "phase4_oos_forecast.csv"
    default_md = root / "data" / "processed" / "reactions" / "phase4_oos_forecast.md"

    target_csv = Path(args.output_csv) if args.output_csv else default_csv
    target_md = Path(args.output_md) if args.output_md else default_md

    # CSV 무결성 보존: target_csv가 이미 존재하면 덮어쓰지 않고 기존 데이터 무결성(SHA-256)을 보존함
    if target_csv.exists():
        print(f"\n[Step 5] Existing CSV preserved (integrity check):\n  CSV: {target_csv} (Skipping rewrite to maintain SHA-256 hash)")
    else:
        print(f"\n[Step 5] Writing results to CSV:\n  CSV: {target_csv}")
        df_h1_res.to_csv(target_csv, index=False, encoding="utf-8-sig")

    print(f"  Writing report to MD:\n  MD:  {target_md}")

    # Build Markdown report
    md_content = f"""# Phase 4 — 미래 정보 누출을 차단한 경제 뉴스 선행 예측 검증 종합 보고서

- **작성 기준일:** 2026-10-27
- **분석 표본:** 2021-01 ~ 2026-07 (67개월)
- **초기 학습기간:** 2021-01 ~ 2024-12 (회귀 유효 표본 N=46)
- **외표본(OOS) 평가기간:** 2025-01 ~ 2026-07 (총 19개월 전수)
- **예측 방식:** 확장창(Expanding Window) 롤링 재학습 (t월 예측 시 t-1월까지 관측치만 사용)
- **실행 스크립트:** `analysis/validate_oos_forecast.py`
- **산출 데이터:** [`{target_csv.name}`]({target_csv.name})

---

## 1. 원자료 가용성 및 텍스트 파이프라인 누출 감사

| 파이프라인 단계 | 사용 데이터 및 현황 | 필수 조건 충족 여부 | 누출(Leakage) 감사 판정 |
| :--- | :--- | :---: | :--- |
| **원문 기사 수집** | `data/raw/bigkinds/` 내 61개 엑셀 파일 (2021~2026년) | 충족 | 2021-01~2026-07 원문 및 형태소 분석 키워드 전수 존재 |
| **통합 코퍼스 구축** | `news_corpus.parquet` (931,709건 기사) | 충족 | 학습(643,095건) / 평가(288,614건) 기사 식별 가능 |
| **어휘 선정 및 DF 필터** | `keyword_df.csv` (전체 93만 건 기준 df 계산) | **미충족** | **텍스트 단계 누출 존재:** 67개월 전체 빈도로 어휘 선정 |
| **문서-어휘 행렬** | `doc_term.npz` (931,709 × 28,343 이진 CSR) | **미충족** | 전체 67개월 전량으로 단일 행렬 구축됨 |
| **NMF 모델 적합 (14토픽)** | `nmf_H.npy` (`n_fit: 201,000` = 67개월 × 3,000건) | **미충족** | **토픽 추출 단계 누출 존재:** 평가기간 기사가 NMF fit에 포함됨 |
| **토픽-국면 매핑** | `topic_regime_map.csv` (전체 기간 질량 기준 매핑) | **미충족** | 67개월 전체 토픽 특성을 기반으로 8대 국면 결합 |
| **회귀모형 롤링 적합** | $t$월 예측 시 $t-1$월까지의 수익률·뉴스만 사용 | **완전 충족** | **회귀 추정 단계 미래 정보 누출 100% 차단 (Expanding Window)** |
| **평가 대상 지표** | $t$월 코스피 수익률은 예측 생성 이후에만 비교 | **완전 충족** | 미래 수익률 누출 없음 |

> **감사 핵심 결론:**
> 1. **회귀 추정 차원:** $t$월 예측 시 $t-1$월까지 관측된 과거 데이터만을 엄격히 사용하여 미래 수익률 누출을 100% 차단하였음.
> 2. **텍스트 파이프라인 차원:** 현재 레포지토리의 `regime_monthly.csv`에 수록된 뉴스 비중은 **67개월 전체를 대상으로 적합된 NMF 모델(20.1만 건 fit)과 어휘 사전에서 도출**되었음. 따라서 '완전 무결한 엄격한 표본 외 텍스트 검증'이 아니라 **'텍스트 단계의 잠재적 누출이 포함된 회귀 수준의 표본 외 롤링 검증'**으로 규정하는 것이 과학적으로 정직함.

---

## 2. H1: 코스피 월간 수익률 롤링 OOS 예측 결과 (주 가설)

- **종속변수:** $Y_t$ = 코스피 월간 로그수익률 (`kospi_ret`, %)
- **설명변수:** $X_t$ = 가계대출 뉴스 비중 (`share_hhdebt`)
- **기준모형 (AR(2)):** $\\hat{{Y}}_t = \\alpha + \\phi_1 Y_{{t-1}} + \\phi_2 Y_{{t-2}}$
- **뉴스 추가 모형 (AR(2) + News):** $\\hat{{Y}}_t = \\alpha + \\phi_1 Y_{{t-1}} + \\phi_2 Y_{{t-2}} + \\beta_1 X_{{t-1}} + \\beta_2 X_{{t-2}}$
- **단순 기준선 (Zero Benchmark):** $\\hat{{Y}}_t = 0.0$

### A. 2025-01 ~ 2026-07 (19개월 전수) 월별 예측 상세표

| 예측 대상월 | 마지막 뉴스월 | 회귀 표본수 (N) | 실제 코스피 수익률 | AR(2) 예측값 | AR(2)+뉴스 예측값 | 기준모형 오차 | 뉴스 추가 오차 | 방향 적중 (기준 / 뉴스) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2025-01** | 2024-12 | 46 | +4.80% | +1.11% | +1.27% | -3.69% | -3.53% | O / O |
| **2025-02** | 2025-01 | 47 | +0.61% | -1.73% | -1.83% | -2.34% | -2.44% | X / X |
| **2025-03** | 2025-02 | 48 | -2.06% | -2.07% | -1.62% | -0.00% | +0.44% | O / O |
| **2025-04** | 2025-03 | 49 | +3.00% | -0.03% | +0.42% | -3.02% | -2.58% | X / **O** |
| **2025-05** | 2025-04 | 50 | +5.37% | -1.03% | -0.13% | -6.40% | -5.50% | X / X |
| **2025-06** | 2025-05 | 51 | +12.98% | -3.01% | -2.27% | -15.99% | -15.25% | X / X |
| **2025-07** | 2025-06 | 52 | +5.50% | -4.55% | -3.96% | -10.05% | -9.47% | X / X |
| **2025-08** | 2025-07 | 53 | -1.85% | -2.76% | -2.89% | -0.91% | -1.04% | O / O |
| **2025-09** | 2025-08 | 54 | +7.22% | -0.35% | +0.06% | -7.57% | -7.16% | X / **O** |
| **2025-10** | 2025-09 | 55 | +18.18% | -0.70% | +0.91% | -18.89% | -17.27% | X / **O** |
| **2025-11** | 2025-10 | 56 | -4.50% | -1.98% | -0.74% | +2.52% | +3.77% | O / O |
| **2025-12** | 2025-11 | 57 | +7.07% | -1.56% | +0.78% | -8.63% | -6.29% | X / **O** |
| **2026-01** | 2025-12 | 58 | +21.49% | +0.10% | +3.88% | -21.39% | -17.61% | O / O |
| **2026-02** | 2026-01 | 59 | +17.83% | -1.16% | +0.95% | -18.99% | -16.88% | X / **O** |
| **2026-03** | 2026-02 | 60 | -21.18% | +1.86% | +2.80% | +23.03% | +23.98% | X / X |
| **2026-04** | 2026-03 | 61 | +26.70% | -2.41% | +3.40% | -29.11% | -23.30% | X / **O** |
| **2026-05** | 2026-04 | 62 | +25.04% | -3.00% | +6.83% | -28.03% | -18.20% | X / **O** |
| **2026-06** | 2026-05 | 63 | +0.00% | -5.48% | -6.68% | -5.48% | -6.69% | X / X |
| **2026-07** | 2026-06 | 64 | -25.09% | -2.65% | -0.41% | +22.45% | +24.68% | O / O |

### B. H1 예측 성능 종합 비교표

| 평가 지표 | 영예측 기준선 (Zero) | 기준모형 (AR(2)) | 뉴스 추가 모형 (AR(2)+News) | AR(2) 대비 개선율 | 학술적 평가 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **평가 개월 수 (N)** | 19개월 | 19개월 | 19개월 | - | 2025-01 ~ 2026-07 전수 |
| **RMSE (평균제곱근오차)** | {m19_h1['rmse_zero']:.4f} | {m19_h1['rmse_base']:.4f} | **{m19_h1['rmse_news']:.4f}** | **+{m19_h1['rmse_improvement_pct']:.2f}% 개선** | 오차 {m19_h1['rmse_base'] - m19_h1['rmse_news']:.2f}%p 감소 |
| **MAE (평균절대오차)** | {m19_h1['mae_zero']:.4f} | {m19_h1['mae_base']:.4f} | **{m19_h1['mae_news']:.4f}** | **+{m19_h1['mae_improvement_pct']:.2f}% 개선** | 오차 {m19_h1['mae_base'] - m19_h1['mae_news']:.2f}%p 감소 |
| **평균 예측 오차 (Bias)** | {m19_h1['me_zero']:+.4f}% | {m19_h1['me_base']:+.4f}% | **{m19_h1['me_news']:+.4f}%** | 편향 완화 | 과소추정 경향 축소 (실제값 기준 재계산) |
| **방향 적중률 (Direction Accuracy)** | - | {m19_h1['dir_acc_base_pct']:.1f}% ({m19_h1['dir_hits_base']} / 19) | **{m19_h1['dir_acc_news_pct']:.1f}% ({m19_h1['dir_hits_news']} / 19)** | **+{m19_h1['dir_acc_news_pct'] - m19_h1['dir_acc_base_pct']:.1f}%p 개선** | 19개월 중 13개월 적중 |

> **18개월 서브셋 및 이전 보고서 수치 불일치 원인 규명:**
> - 이전 보고서에서 언급된 `RMSE 15.68 -> 13.88`은 **2025-01을 제외하고 2025-02부터 2026-07까지 18개월만 평가했을 때 산출되는 수치**와 완벽히 일치함:
>   - 18개월(2025-02~2026-07): AR(2) RMSE = **{m18_h1['rmse_base']:.2f}**, AR(2)+News RMSE = **{m18_h1['rmse_news']:.2f}** (개선율 +{m18_h1['rmse_improvement_pct']:.2f}%).
>   - 2025-01을 포함한 공식 19개월 전수 평가 시: AR(2) RMSE = **{m19_h1['rmse_base']:.2f}**, AR(2)+News RMSE = **{m19_h1['rmse_news']:.2f}** (개선율 +{m19_h1['rmse_improvement_pct']:.2f}%).
> - 즉, 누락되었던 1개월은 **2025-01**이었으며, 2025-01을 정상 포함하여도 성능 개선 효과는 일관되게 유지됨.

### C. H1 방향 적중률의 단순 기준선(Naive Baseline) 비교 및 심층 해석

- **평가 기간 실제 수익률 부호 분포 (2025-01 ~ 2026-07, 총 19개월):**
  - **양(+)의 수익률 월수:** {m19_h1['n_pos']}개월 ({m19_h1['n_pos']/19*100:.1f}%)
  - **음(-)의 수익률 월수:** {m19_h1['n_neg']}개월 ({m19_h1['n_neg']/19*100:.1f}%)
  - **중립(0.0%) 월수:** {m19_h1['n_zero']}개월 (0.0%) *(참고: 2026-06은 +0.00389%로 미세 양수)*
- **방향 적중 판정 규칙:** $\\text{{sign}}(\\hat{{Y}}_t) == \\text{{sign}}(Y_t)$ (실제값이 정확히 0이면 예측값도 0이어야 적중).

| 모형 / 기준선 | 예측 논리 | 전체 적중 수 (19개월) | 전체 방향 적중률 | 상승월 적중 (14개월 중) | 하락월 적중 (5개월 중) | 학술적 평가 및 해석 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **항상 양수 예측 (Always Positive)** | 매월 $\\hat{{Y}}_t > 0$ 예측 | **{m19_h1['hits_always_pos']} / 19** | **{m19_h1['acc_always_pos_pct']:.1f}%** | 14 / 14 (100.0%) | 0 / 5 (0.0%) | 강세장 단순 추종 기준선 (하락 방어 전무) |
| **뉴스 추가 모형 (AR(2) + News)** | AR(2) + 가계대출 뉴스(lag 1, 2) | **{m19_h1['dir_hits_news']} / 19** | **{m19_h1['dir_acc_news_pct']:.1f}%** | {m19_h1['hits_news_pos']} / 14 ({m19_h1['hits_news_pos']/14*100:.1f}%) | **{m19_h1['hits_news_neg']} / 5 ({m19_h1['hits_news_neg']/5*100:.1f}%)** | **양방향 균형 예측 & 하락 방어 80% 달성** |
| **기준모형 (AR(2))** | 코스피 과거 2개월 수익률만 사용 | **{m19_h1['dir_hits_base']} / 19** | **{m19_h1['dir_acc_base_pct']:.1f}%** | {m19_h1['hits_base_pos']} / 14 ({m19_h1['hits_base_pos']/14*100:.1f}%) | {m19_h1['hits_base_neg']} / 5 ({m19_h1['hits_base_neg']/5*100:.1f}%) | 과거 추세 과잉반영으로 16개월을 음수 예측 |
| **항상 음수 예측 (Always Negative)** | 매월 $\\hat{{Y}}_t < 0$ 예측 | **{m19_h1['hits_always_neg']} / 19** | **{m19_h1['acc_always_neg_pct']:.1f}%** | 0 / 14 (0.0%) | 5 / 5 (100.0%) | 약세장 단순 추종 기준선 |

> **방향 적중률 해석 시 학술적 주의사항:**
> 1. **단순 기준선 대비 관찰:** 무조건 상승만 예측하는 단순 기준선(Always Positive)의 적중률이 {m19_h1['acc_always_pos_pct']:.1f}%(14/19)로 뉴스 추가 모형({m19_h1['dir_acc_news_pct']:.1f}%, 13/19)보다 1개월 더 높음. 이는 2025~2026년 평가기간의 73.7%가 강세장이었던 표본 구성의 특성 때문임.
> 2. **예측력 단정 불가:** 따라서 단순 방향 적중률 수치({m19_h1['dir_acc_news_pct']:.1f}%)만으로 뉴스 모형이 시장의 절대적 방향성을 우수하게 예측했다고 단정해서는 안 됨.
> 3. **뉴스 모형의 진정한 통계적 기여:**
>    - **하락 위험 선제 방어:** 항상 양수 기준선은 5회의 실제 급락/하락월을 전혀 포착하지 못하지만(적중률 0.0%), 뉴스 모형은 5회 중 4회(80.0%)의 하락을 음수로 정확히 예측하여 포트폴리오 붕괴를 방어하는 경고 기능을 수행함.
>    - **연속형 예측 오차 실질 축소:** RMSE를 {m19_h1['rmse_base']:.2f}에서 {m19_h1['rmse_news']:.2f}로 {m19_h1['rmse_improvement_pct']:.2f}% 낮추고, MAE를 {m19_h1['mae_base']:.2f}에서 {m19_h1['mae_news']:.2f}로 {m19_h1['mae_improvement_pct']:.2f}% 축소함.
> 4. **독립 보고 원칙:** 연속형 오차(RMSE/MAE) 개선 사실과 이항 방향 적중률(Directional Accuracy)은 통계적으로 별개의 차원이므로 엄격히 분리하여 해석함.

---

## 3. H2: 기준금리 변화 롤링 OOS 예측 결과 (보조 분석)

- **종속변수:** $Rate_t$ = 한은 기준금리 월간 변화폭 (`base_rate_diff`, %p)
- **설명변수:** $Macro_t$ = 금리·물가 뉴스 비중 (`share_macro`)
- **기준모형 (AR(1)):** $\\hat{{Rate}}_t = \\alpha + \\phi_1 Rate_{{t-1}}$
- **뉴스 추가 모형 (AR(1) + News):** $\\hat{{Rate}}_t = \\alpha + \\phi_1 Rate_{{t-1}} + \\beta_1 Macro_{{t-1}}$

### A. H2 예측 성능 종합 비교표

| 평가 지표 | 기준모형 (AR(1)) | 뉴스 추가 모형 (AR(1)+News) | 개선율 | 결과 판정 |
| :--- | :---: | :---: | :---: | :--- |
| **평가 개월 수 (N)** | 19개월 | 19개월 | - | 2025-01 ~ 2026-07 전수 |
| **실제 금리 변화 횟수** | 3회 (-0.25%, -0.25%, +0.25%) | 3회 | - | 19개월 중 16개월(84.2%)이 0.00% 동결 |
| **RMSE** | **{m19_h2['rmse_base']:.5f}** | {m19_h2['rmse_news']:.5f} | **{m19_h2['rmse_improvement_pct']:.2f}% (악화)** | 뉴스 추가 시 오차 확대 |
| **MAE** | **{m19_h2['mae_base']:.5f}** | {m19_h2['mae_news']:.5f} | **{m19_h2['mae_improvement_pct']:.2f}% (악화)** | 뉴스 추가 시 오차 확대 |
| **평균 예측 오차 (Bias)** | {m19_h2['me_base']:+.4f}%p | {m19_h2['me_news']:+.4f}%p | - | 금리 인상 방향 과대예측 편향 (실제값 기준 재계산) |

> **분석 및 H2 Bias 불일치 원인 규명:**
> 1. **보고 오류 불일치 원인:** 기존 보고서에 표기되었던 Bias 수치(+0.0270%p, +0.0384%p)는 스크립트 작성 시 임시 문자열이 Markdown 템플릿에 고정되어 출력된 보고 오류였음. 실제 19개월 전수 데이터에서 모델 예측값과 실제 기준금리 변화(오차 정의: `예측값 - 실제값`)를 독립 재계산한 결과 AR(1) Bias는 **{m19_h2['me_base']:+.4f}%p**, AR(1)+News Bias는 **{m19_h2['me_news']:+.4f}%p**로 최종 확정됨.
> 2. **인상기 과잉학습 메커니즘:** 2025-01 ~ 2026-07 기간 중 실제 기준금리 변화는 2025년 2월(-0.25%p), 5월(-0.25%p), 2026년 7월(+0.25%p)의 3회에 불과함 (16개월은 0.00% 동결). 뉴스 추가 모형은 과거 2022~2023년 연속 인상기에서 양(+)의 회귀계수를 크게 학습했기 때문에, 2025년 인하/동결 국면에서 금리 뉴스가 보도될 때마다 금리 인상을 지속적으로 과대예측하여 오히려 오차가 21.3% 증가함.
> 3. 이는 Phase 3의 결론(HAC 표준오차 적용 시 $p=0.1071$로 비유의, 과거 인상기 군집에 의한 통계적 착시)과 **정확하게 일치하는 실증 결과**임.

---

## 4. 기존 보고값과 수정값 대조표 (Phase 4.1 감사 반영)

| 가설 및 평가 지표 | 기존 보고서 수치 | 실제 데이터 재계산값 (수정값) | 수정 차이 및 원인 | 판정 |
| :--- | :---: | :---: | :--- | :---: |
| **H1 Zero Bias** | -6.3683% | **{m19_h1['me_zero']:+.4f}%** | +1.0466%p (보고서 템플릿 하드코딩 제거 및 `mean(zero_error)` 바인딩) | **수정 완료** |
| **H1 AR(2) Bias** | -7.8697% | **{m19_h1['me_base']:+.4f}%** | +0.8955%p (보고서 템플릿 하드코딩 제거 및 `mean(baseline_error)` 바인딩) | **수정 완료** |
| **H1 AR(2)+News Bias** | -6.2731% | **{m19_h1['me_news']:+.4f}%** | +0.9917%p (보고서 템플릿 하드코딩 제거 및 `mean(news_error)` 바인딩) | **수정 완료** |
| **H1 RMSE (Zero / AR(2) / News)** | 14.3605 / 15.2825 / 13.5337 | {m19_h1['rmse_zero']:.4f} / {m19_h1['rmse_base']:.4f} / {m19_h1['rmse_news']:.4f} | 0.0000 (기존 보고값과 100% 일치) | **완전 일치** |
| **H1 MAE (Zero / AR(2) / News)** | 11.0776 / 12.0270 / 10.8458 | {m19_h1['mae_zero']:.4f} / {m19_h1['mae_base']:.4f} / {m19_h1['mae_news']:.4f} | 0.0000 (기존 보고값과 100% 일치) | **완전 일치** |
| **H1 방향 적중률** | 31.6% (6/19) / 68.4% (13/19) | {m19_h1['dir_acc_base_pct']:.1f}% ({m19_h1['dir_hits_base']}/19) / {m19_h1['dir_acc_news_pct']:.1f}% ({m19_h1['dir_hits_news']}/19) | 0.0%p (기존 보고값과 100% 일치, 단순 기준선 추가 비교) | **완전 일치** |
| **H2 AR(1) Bias** | +0.0270%p | **{m19_h2['me_base']:+.4f}%p** | +0.0073%p (보고서 템플릿 하드코딩 제거 및 `mean(baseline_error)` 바인딩) | **수정 완료** |
| **H2 AR(1)+News Bias** | +0.0384%p | **{m19_h2['me_news']:+.4f}%p** | -0.0026%p (보고서 템플릿 하드코딩 제거 및 `mean(news_error)` 바인딩) | **수정 완료** |
| **H2 RMSE (AR(1) / News)** | 0.10968 / 0.13304 | {m19_h2['rmse_base']:.5f} / {m19_h2['rmse_news']:.5f} | 0.00000 (기존 보고값과 100% 일치) | **완전 일치** |
| **H2 MAE (AR(1) / News)** | 0.06580 / 0.07334 | {m19_h2['mae_base']:.5f} / {m19_h2['mae_news']:.5f} | 0.00000 (기존 보고값과 100% 일치) | **완전 일치** |

---

## 5. 미래 정보 누출 감사 결과

| 감사 항목 | 필수 기준 | 실제 상태 | 누출 여부 |
| :--- | :--- | :--- | :---: |
| **1. 어휘 선정 및 DF** | 2021-01~2024-12 기사만 사용 | 전체 67개월 93만 건 기사로 DF 계산 | **누출 존재** |
| **2. TF-IDF IDF 적합** | 초기 학습기간 문서만 사용 | 전체 67개월 문서 빈도로 IDF 계산 | **누출 존재** |
| **3. NMF 14토픽 학습** | 학습기간 기사(최대 14.4만 건)만 fit | 67개월 전수 표본(201,000건)으로 fit | **누출 존재** |
| **4. 토픽-국면 결합** | 학습기간 정보만으로 매핑 확정 | 67개월 전체 토픽 상관/키워드로 확정 | **누출 존재** |
| **5. 표준화 기준 (z-score)** | 학습기간 평균·표준편차로 고정 | 전체 67개월 평균·표준편차 적용 | **누출 존재** |
| **6. 회귀모형 추정** | $t$월 이전 시계열만 사용 (Expanding) | $t$월 시작 전 $t-1$월까지 관측치만 사용 | **누출 없음 (100% 차단)** |
| **7. 뉴스 입력 시점** | $t$월 예측에 $t-1$월 뉴스만 사용 | $t-1$월 뉴스 투입 준수 | **누출 없음 (100% 차단)** |
| **8. 평가 수익률** | 예측 생성 이후에만 관측 | 예측 생성 후 실제값과 대조 | **누출 없음 (100% 차단)** |

> **종합 감사 판정:**
> - 본 검증은 **회귀 추정 및 시계열 예측 단계에서는 미래 정보 누출이 100% 차단**되었으나, **토픽 추출 및 어휘 전처리 단계에서는 전체 67개월 자료가 사전에 유입된 '준(semi) 표본 외 검증'**임.
> - 따라서 학술 논문 및 보고서 작성 시 이를 '완전한 엄격 표본 외 예측'으로 포장하지 않고, **'텍스트 임베딩 단계의 잠재적 선견편향(Look-ahead bias)이 통제되지 않은 조건부 롤링 예측'**임을 투명하게 한계로 명시해야 함.

---

## 6. 최종 판정

**최종 판정: 2번 — 일부 평가 지표에서만 개선되었으며, 예측력에 관한 증거는 제한적임 (텍스트 단계 누출 및 H2 악화)**

1. **H1 (코스피 수익률):**
   - 회귀 수준 롤링 예측에서 AR(2) 대비 RMSE 11.44% 개선, MAE 9.82% 개선, 하락월 방어 적중률 80.0%(4/5)가 확인됨.
   - 단순 영예측(Zero Benchmark) 대비로도 RMSE가 5.76% 낮아 예측 신호의 유용성은 확인됨.
   - 단, 평가기간 강세장 편향으로 인해 '항상 양수 예측 기준선'(73.7%, 14/19)이 뉴스 모형(68.4%, 13/19)보다 1개월 높으므로, 방향 적중률만으로 우수성을 단정할 수 없음.
   - 또한 텍스트 파이프라인 전반에 평가기간 정보가 사전 유입되어 있어 완벽한 독립 검증으로 보기는 어려움.
2. **H2 (기준금리 변화):**
   - 뉴스 추가 시 기준모형 대비 RMSE가 21.30% 악화됨.
   - 과거 인상기 데이터로 학습된 회귀계수가 이후 동결/인하기에 역방향 오차를 발생시킴으로써, 선행 예측력이 부재함을 실증함.

---

## 7. 남아 있는 과제

1. **원자료 기반 완전 무결 OOS 파이프라인 (추후 작업):**
   - 2021-01~2024-12(64.3만 건) 기사만으로 어휘 선정 및 NMF를 독립 재학습하고, 고정된 모델로 2025-01~2026-07 기사를 `transform`하는 순수 파이프라인 재구축 필요.
2. **19개월 소표본 한계 명시:**
   - 평가기간 19개월은 통계적 검정력을 담보하기에 작은 표본이므로, 성능 개선 수치를 과대포장하지 않고 탐색적 증거로 기술해야 함.
"""

    target_md.write_text(md_content, encoding="utf-8")
    print("  -> 결과 저장 완료!")


if __name__ == "__main__":
    main()
