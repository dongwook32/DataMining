import subprocess
import os
import io
import json
import math
import pandas as pd
import numpy as np

repo = r"C:\Users\CDW\1_Project\DataMining"
web_dir = os.path.join(repo, "research_web")
data_dir = os.path.join(web_dir, "data")
fig_dir = os.path.join(web_dir, "assets", "figures")

os.makedirs(data_dir, exist_ok=True)
os.makedirs(fig_dir, exist_ok=True)

def git_read_bytes(path, rev="origin/main"):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=repo, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"Failed to read {path} from {rev}: {r.stderr.decode('utf-8', 'replace')}")
    return r.stdout

def git_read_csv(path, rev="origin/main"):
    b = git_read_bytes(path, rev)
    return pd.read_csv(io.BytesIO(b))

def df_to_records(df):
    # Replace NaN/inf with None for clean JSON
    records = df.replace([np.inf, -np.inf], np.nan).where(pd.notnull(df), None).to_dict(orient="records")
    # Clean any remaining float nan
    cleaned = []
    for row in records:
        new_row = {}
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                new_row[k] = None
            else:
                new_row[k] = v
        cleaned.append(new_row)
    return cleaned

print("1. Loading monthly panel and topic/regime shares...")
monthly_panel_df = pd.read_csv(os.path.join(repo, "data", "processed", "panel", "monthly_panel.csv"))
topic_share_400_df = git_read_csv("data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/monthly_topic_share.csv")
regime_400_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/monthly_regime_share_400.csv")
regime_800_7_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/monthly_regime_share_800_7regime.csv")
regime_800_6_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/monthly_regime_share_800_legacy6.csv")
single_multi_monthly_df = git_read_csv("data/processed/supplemental_validation/single_vs_multi_monthly.csv")

# Merge 67-month study panel with topic shares, regime shares (400 & 800), and single_vs_multi
study_panel_67 = monthly_panel_df[monthly_panel_df["month"] >= "2021-01"].copy()
study_panel_67 = study_panel_67.merge(
    topic_share_400_df.drop(columns=["n_docs", "n_valid"], errors="ignore"),
    on="month", how="left"
)
regime_400_cols = ["month", "n_docs", "n_valid", "period",
                   "share_macro", "share_realestate", "share_aichip", "share_market", "share_earnings", "share_capital", "residual_share",
                   "z_macro", "z_realestate", "z_aichip", "z_market", "z_earnings", "z_capital"]
study_panel_67 = study_panel_67.merge(regime_400_df[regime_400_cols], on="month", how="left")

regime_800_cols = {
    "share_macro": "share800_macro",
    "share_realestate": "share800_realestate",
    "share_hhdebt": "share800_hhdebt",
    "share_aichip": "share800_aichip",
    "share_market": "share800_market",
    "share_earnings": "share800_earnings",
    "share_capital": "share800_capital",
    "residual_share": "residual800_share",
    "z_macro": "z800_macro",
    "z_realestate": "z800_realestate",
    "z_hhdebt": "z800_hhdebt",
    "z_aichip": "z800_aichip",
    "z_market": "z800_market",
    "z_earnings": "z800_earnings",
    "z_capital": "z800_capital",
}
r800_sub = regime_800_7_df[["month"] + list(regime_800_cols.keys())].rename(columns=regime_800_cols)
study_panel_67 = study_panel_67.merge(r800_sub, on="month", how="left")

if "month" in single_multi_monthly_df.columns:
    sm_cols = [c for c in single_multi_monthly_df.columns if c not in study_panel_67.columns or c == "month"]
    study_panel_67 = study_panel_67.merge(single_multi_monthly_df[sm_cols], on="month", how="left")

print("2. Loading NMF Convergence & Topic tables...")
convergence_metrics_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/convergence_metrics.csv")
topic_alignment_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/topic_alignment.csv")
topic_mapping_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/topic_mapping_comparison.csv")
topic_terms_400_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/topic_terms_400.csv")
topic_terms_800_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/topic_terms_800.csv")
topic_quality_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/topic_quality_comparison.csv")
topic_model_comp_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_161800/topic_model_comparison_metrics.csv")
topic_stability_summary_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_summary.csv")

print("3. Loading Downstream Sensitivity & Multi-Regime & Case Studies...")
regime_share_metrics_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/regime_share_metrics.csv")
hac_regression_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/hac_regression_comparison.csv")
strict_oos_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/strict_oos_comparison.csv")
multiregime_comp_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/multiregime_comparison.csv")
single_vs_multi_metrics_df = git_read_csv("data/processed/supplemental_validation/single_vs_multi_metrics.csv")
single_vs_multi_combos_df = git_read_csv("data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv")
case_monthly_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_161800/multi_regime_case_monthly.csv")
case_articles_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_161800/multi_regime_case_articles.csv")

print("4. Loading Weekly News vs Naver Search Data (292 weeks)...")
weekly_panel_df = git_read_csv("data/processed/supplemental_validation/news_search_weekly_panel.csv")
# Also compute 1st differences (Method B: split then diff, and Method C: full diff) for interactive plotting!
news_cols = [c for c in weekly_panel_df.columns if c.startswith("news_share_")]
search_cols = [c for c in weekly_panel_df.columns if c.startswith("search_")]
for c in news_cols + search_cols:
    # Method B: diff within each period (train vs eval)
    weekly_panel_df[f"d_{c}"] = weekly_panel_df.groupby("period")[c].diff()

naver_weekly_comp_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/naver_weekly_comparison.csv")
news_search_hac_df = git_read_csv("data/processed/supplemental_validation/news_search_hac_results.csv")
news_search_lag_df = git_read_csv("data/processed/supplemental_validation/news_search_lag_results.csv")
news_search_boot_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_161800/news_search_block_bootstrap_ci.csv")
weekly_diff_method_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_A3_2_WEEKLY_PERIOD_AUDIT_01/weekly_diff_method_comparison.csv")
weekly_period_audit_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_A3_2_WEEKLY_PERIOD_AUDIT_01/weekly_period_count_audit.csv")

print("5. Loading Audits, Claims & Verified References...")
final_approved_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_A3_CONSISTENCY_AUDIT_01/final_approved_numbers.csv")
claim_verif_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_A3_CONSISTENCY_AUDIT_01/claim_verification_table.csv")
ref_verif_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_A5_REFERENCE_AUDIT_01/reference_verification_table.csv")
ref_corr_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_A5_1_REFERENCE_CORRECTION_01/reference_corrections.csv")
lit_matrix_df = git_read_csv("data/processed/reviewer_readiness/RUN_20261106_161800/literature_comparison_matrix.csv")

# Extract PNG figures from origin/main
png_files = {
    "reconstruction_error.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/convergence_figures/reconstruction_error.png",
    "topic_similarity.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/convergence_figures/topic_similarity.png",
    "topic_quality_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/convergence_figures/topic_quality_comparison.png",
    "regime_share_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/regime_share_comparison.png",
    "regime_share_difference.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/regime_share_difference.png",
    "multiregime_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/multiregime_comparison.png",
    "hac_coefficient_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/hac_coefficient_comparison.png",
    "strict_oos_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/strict_oos_comparison.png",
    "naver_weekly_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/naver_weekly_comparison.png",
    "weekly_news_search_trends.png": "data/processed/supplemental_validation/news_search_figures/weekly_news_search_trends.png",
    "eval_oos_bootstrap_ci.png": "data/processed/reviewer_readiness/RUN_20261106_161800/news_search_robustness_figures/eval_oos_bootstrap_ci.png",
    "case_study_z_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_161800/multi_regime_case_figures/case_study_z_comparison.png",
    "k_sensitivity_comparison.png": "data/processed/reviewer_readiness/RUN_20261106_161800/topic_model_comparison_figures/k_sensitivity_comparison.png",
    "topic_stability_by_topic.png": "data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_figures/topic_stability_by_topic.png",
}

for fname, gpath in png_files.items():
    try:
        b = git_read_bytes(gpath)
        with open(os.path.join(fig_dir, fname), "wb") as f:
            f.write(b)
        print(f"  Saved figure: {fname} ({len(b)} bytes)")
    except Exception as e:
        print(f"  Warning figure {fname}: {e}")

bundle = {
    "meta": {
        "title": "뉴스 빅데이터와 NMF 기반 한국형 경제 이슈 다중 국면 탐지 및 다각적 실증 검증",
        "subtitle": "JKIICE 최종 연구 성과 및 다차원 실증 데이터 대시보드 (Phase 5.6 Strict OOS & A-2~A-6.1 통합)",
        "total_docs_raw": 933225,
        "total_docs_valid": 931709,
        "train_docs": 643095,
        "oos_docs": 288614,
        "total_months": 67,
        "train_months": 48,
        "oos_months": 19,
        "macro_panel_months": 127,
        "vocab_size_train": 22193,
        "stratified_sample_docs": 144000,
        "nmf_k": 14,
        "core_regimes_count": 6,
        "converged_regimes_count": 7,
        "nmf400_err": 369.804840,
        "nmf800_err": 369.777710,
        "nmf800_iter": 447,
        "err_diff_pct": 0.007336,
        "cosine_mean_14": 0.980223,
        "cosine_mean_13": 0.995269,
        "cosine_median_13": 0.999093,
        "weekly_raw_total": 292,
        "weekly_diff_total": 291,
        "weekly_raw_train": 209,
        "weekly_diff_train": 208,
        "weekly_raw_oos": 83,
        "weekly_diff_oos_method_b": 82,
        "weekly_diff_oos_method_c": 83,
    },
    "study_panel_67m": df_to_records(study_panel_67),
    "macro_panel_127m": df_to_records(monthly_panel_df[["month", "date", "in_study", "KOSPI", "USD_KRW", "CPI", "CCSI", "BASE_RATE", "kospi_ret", "usdkrw_ret", "cpi_mom", "ccsi_diff", "base_rate_diff", "cpi_yoy", "kospi_vol3", "kospi_vol12", "kospi_ret_std", "news_n"]]),
    "convergence_metrics": df_to_records(convergence_metrics_df),
    "topic_alignment": df_to_records(topic_alignment_df[topic_alignment_df["pair"] == "NMF-400_vs_NMF-800"]),
    "topic_mapping": df_to_records(topic_mapping_df),
    "topic_terms_400": df_to_records(topic_terms_400_df),
    "topic_terms_800": df_to_records(topic_terms_800_df),
    "topic_model_comparison": df_to_records(topic_model_comp_df),
    "topic_stability_summary": df_to_records(topic_stability_summary_df),
    "regime_share_metrics": df_to_records(regime_share_metrics_df),
    "hac_regression": df_to_records(hac_regression_df),
    "strict_oos_early_warning": df_to_records(strict_oos_df),
    "multiregime_comparison": df_to_records(multiregime_comp_df),
    "single_vs_multi_metrics": df_to_records(single_vs_multi_metrics_df),
    "single_vs_multi_combos": df_to_records(single_vs_multi_combos_df),
    "case_studies_monthly": df_to_records(case_monthly_df),
    "case_studies_articles": df_to_records(case_articles_df),
    "weekly_panel_292w": df_to_records(weekly_panel_df),
    "naver_weekly_comparison": df_to_records(naver_weekly_comp_df),
    "news_search_hac": df_to_records(news_search_hac_df),
    "news_search_lag": df_to_records(news_search_lag_df),
    "news_search_bootstrap": df_to_records(news_search_boot_df),
    "weekly_diff_method_comparison": df_to_records(weekly_diff_method_df),
    "weekly_period_count_audit": df_to_records(weekly_period_audit_df),
    "final_approved_numbers": df_to_records(final_approved_df),
    "claim_verification": df_to_records(claim_verif_df),
    "reference_verification": df_to_records(ref_verif_df),
    "reference_corrections": df_to_records(ref_corr_df),
    "literature_comparison": df_to_records(lit_matrix_df),
}

json_path = os.path.join(data_dir, "research_data.json")
js_path = os.path.join(data_dir, "research_data.js")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(bundle, f, ensure_ascii=False, indent=2)

with open(js_path, "w", encoding="utf-8") as f:
    f.write("window.RESEARCH_DATA = ")
    json.dump(bundle, f, ensure_ascii=False)
    f.write(";\n")

print(f"Successfully generated {json_path} ({os.path.getsize(json_path)} bytes) and {js_path} ({os.path.getsize(js_path)} bytes)")

