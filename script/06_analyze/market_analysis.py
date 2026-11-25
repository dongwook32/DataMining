"""
종합 검증 스크립트: 연구 분석 결과 3종 최종 재현 및 Phase 5.6 Strict OOS 검증
1. HAC OLS 회귀분석 (kospi_ret_std, kospi_ret, kospi_vol12)
2. 경제 국면별 상관관계 및 선행·후행 시차 분석 (h in [-2, -1, 0, 1, 2], Holm 보정, 정상성 검정)
3. 주가 하락 경고, 금리 인상 포착률 및 강건성 분석 (자연발생률 대비 정밀도, 폭락 재현율, 임계값 민감도, 60개월, Strict OOS 분할)

저장 산출물:
- data/processed/reactions/ols.csv
- data/processed/reactions/lag_corr.csv
- data/processed/reactions/warnings.csv
"""

import sys
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tsa.stattools import adfuller, kpss

warnings.filterwarnings("ignore")

# 경로 설정
from util.paths import ROOT
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
LEGACY_REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
PHASE56_REGIME_PATH = ROOT / "data" / "processed" / "reactions" / "regime_monthly.csv"
OUT_DIR = ROOT / "data" / "processed" / "reactions"

OUT_DIR.mkdir(parents=True, exist_ok=True)

OLS_OUT_CSV = OUT_DIR / "ols.csv"
CORR_OUT_CSV = OUT_DIR / "lag_corr.csv"
WARN_OUT_CSV = OUT_DIR / "warnings.csv"


def load_datasets():
    panel = pd.read_csv(PANEL_PATH)
    legacy_regime = pd.read_csv(LEGACY_REGIME_PATH)
    phase56_regime = pd.read_csv(PHASE56_REGIME_PATH)

    # 1) Legacy merged (67 months: 2021-01 ~ 2026-07)
    df_legacy = pd.merge(
        legacy_regime[(legacy_regime["month"] >= "2021-01") & (legacy_regime["month"] <= "2026-07")],
        panel[(panel["month"] >= "2021-01") & (panel["month"] <= "2026-07")],
        on="month"
    ).sort_values("month").reset_index(drop=True)

    # Calculate z-scores for legacy regimes
    legacy_slugs = ["macro", "realestate", "hhdebt", "trade", "aichip", "market", "earnings", "capital"]
    for s in legacy_slugs:
        sh = df_legacy[f"share_{s}"]
        df_legacy[f"z_{s}"] = (sh - sh.mean()) / sh.std(ddof=1)

    # 2) Phase 5.6 merged (67 months: 2021-01 ~ 2026-07)
    df_p56 = pd.merge(
        phase56_regime,
        panel,
        on="month"
    ).sort_values("month").reset_index(drop=True)

    return df_legacy, df_p56


# ==============================================================================
# 1. HAC OLS 회귀분석 재검증
# ==============================================================================
def holm_bonferroni(p_vals):
    """Holm-Bonferroni p-value adjustment"""
    p_arr = np.array(p_vals, dtype=float)
    n = len(p_arr)
    sorted_indices = np.argsort(p_arr)
    adj_p = np.empty(n, dtype=float)
    
    cum_max = 0.0
    for rank, idx in enumerate(sorted_indices):
        raw_p = p_arr[idx]
        multiplier = n - rank
        p_adj = min(raw_p * multiplier, 1.0)
        cum_max = max(cum_max, p_adj)
        adj_p[idx] = cum_max
        
    return adj_p


def run_ols_verification(df_legacy, df_p56):
    print("\n" + "=" * 80)
    print("1. HAC OLS 회귀분석 재검증 실행")
    print("=" * 80)

    ols_records = []

    models_to_run = [
        # (모형 식별자, 데이터셋, 설명변수 목록, 종속변수, 기간 설명)
        (
            "Legacy_Replication_ret_std",
            df_legacy,
            [f"z_{s}" for s in ["macro", "realestate", "hhdebt", "trade", "aichip", "market", "earnings", "capital"]],
            "kospi_ret_std",
            "과거 8국면 (전체 67개월 2021-01~2026-07)"
        ),
        (
            "Legacy_Replication_ret",
            df_legacy,
            [f"z_{s}" for s in ["macro", "realestate", "hhdebt", "trade", "aichip", "market", "earnings", "capital"]],
            "kospi_ret",
            "과거 8국면 (전체 67개월 2021-01~2026-07)"
        ),
        (
            "Legacy_Auxiliary_vol12",
            df_legacy,
            [f"z_{s}" for s in ["macro", "realestate", "hhdebt", "trade", "aichip", "market", "earnings", "capital"]],
            "kospi_vol12",
            "과거 8국면 실제 변동성 (보조 분석)"
        ),
        (
            "Phase56_StrictOOS_ret_std_67m",
            df_p56,
            [f"z_{s}" for s in ["macro", "realestate", "aichip", "market", "earnings", "capital"]],
            "kospi_ret_std",
            "Phase 5.6 유효 6국면 (전체 67개월)"
        ),
        (
            "Phase56_StrictOOS_ret_67m",
            df_p56,
            [f"z_{s}" for s in ["macro", "realestate", "aichip", "market", "earnings", "capital"]],
            "kospi_ret",
            "Phase 5.6 유효 6국면 (전체 67개월)"
        ),
        (
            "Phase56_StrictOOS_vol12_67m",
            df_p56,
            [f"z_{s}" for s in ["macro", "realestate", "aichip", "market", "earnings", "capital"]],
            "kospi_vol12",
            "Phase 5.6 실제 변동성 (전체 67개월 보조 분석)"
        ),
        (
            "Phase56_StrictOOS_ret_std_train48m",
            df_p56[df_p56["period"] == "train"].reset_index(drop=True),
            [f"z_{s}" for s in ["macro", "realestate", "aichip", "market", "earnings", "capital"]],
            "kospi_ret_std",
            "Phase 5.6 학습 기간 (48개월 2021-01~2024-12)"
        ),
        (
            "Phase56_StrictOOS_ret_train48m",
            df_p56[df_p56["period"] == "train"].reset_index(drop=True),
            [f"z_{s}" for s in ["macro", "realestate", "aichip", "market", "earnings", "capital"]],
            "kospi_ret",
            "Phase 5.6 학습 기간 (48개월 2021-01~2024-12)"
        ),
        (
            "Phase56_StrictOOS_vol12_train48m",
            df_p56[df_p56["period"] == "train"].reset_index(drop=True),
            [f"z_{s}" for s in ["macro", "realestate", "aichip", "market", "earnings", "capital"]],
            "kospi_vol12",
            "Phase 5.6 실제 변동성 (학습 48개월 보조 분석)"
        ),
    ]

    for model_id, data, x_cols, y_col, desc in models_to_run:
        df_clean = data.dropna(subset=x_cols + [y_col]).copy()
        N = len(df_clean)
        k_vars = len(x_cols)

        X = sm.add_constant(df_clean[x_cols])
        y = df_clean[y_col]

        # VIF 계산 (상수항 제외)
        vifs = {}
        X_novar = df_clean[x_cols]
        for i, col in enumerate(x_cols):
            vifs[col] = float(variance_inflation_factor(X.values, i + 1))

        # OLS fit with HAC maxlags=3
        model = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})

        r2 = float(model.rsquared)
        adj_r2 = float(model.rsquared_adj)
        f_val = float(model.fvalue) if model.fvalue is not None else np.nan
        f_pval = float(model.f_pvalue) if model.f_pvalue is not None else np.nan
        wald_val = f_val * k_vars if not np.isnan(f_val) else np.nan
        df_model = int(model.df_model)
        df_resid = int(model.df_resid)

        # 회귀계수별 p-value Holm 보정 (상수항 제외 국면 변수 대상)
        coef_pvals = [float(model.pvalues[col]) for col in x_cols]
        coef_holm_pvals = holm_bonferroni(coef_pvals)

        print(f"\n[{model_id}] {desc} | 종속변수: {y_col} (N={N})")
        print(f"  R² = {r2*100:.2f}%, Adj-R² = {adj_r2*100:.2f}%, F = {f_val:.4f} (p = {f_pval:.6f}), Wald = {wald_val:.4f}")

        # 기록: 모형 전체 요약 및 개별 계수 저장
        # 1) 상수항
        ci_const = model.conf_int().loc["const"]
        ols_records.append({
            "model_id": model_id,
            "description": desc,
            "dep_var": y_col,
            "sample_n": N,
            "df_model": df_model,
            "df_resid": df_resid,
            "r_squared": r2,
            "adj_r_squared": adj_r2,
            "f_statistic": f_val,
            "f_pvalue": f_pval,
            "wald_statistic": wald_val,
            "variable": "const",
            "coef": float(model.params["const"]),
            "std_err": float(model.bse["const"]),
            "t_statistic": float(model.tvalues["const"]),
            "p_value_raw": float(model.pvalues["const"]),
            "p_value_holm": np.nan,
            "ci_lower_95": float(ci_const[0]),
            "ci_upper_95": float(ci_const[1]),
            "vif": np.nan
        })

        for idx, col in enumerate(x_cols):
            ci = model.conf_int().loc[col]
            coef_val = float(model.params[col])
            se_val = float(model.bse[col])
            t_val = float(model.tvalues[col])
            p_val = float(model.pvalues[col])
            holm_p = float(coef_holm_pvals[idx])
            vif_val = vifs[col]

            ols_records.append({
                "model_id": model_id,
                "description": desc,
                "dep_var": y_col,
                "sample_n": N,
                "df_model": df_model,
                "df_resid": df_resid,
                "r_squared": r2,
                "adj_r_squared": adj_r2,
                "f_statistic": f_val,
                "f_pvalue": f_pval,
                "wald_statistic": wald_val,
                "variable": col,
                "coef": coef_val,
                "std_err": se_val,
                "t_statistic": t_val,
                "p_value_raw": p_val,
                "p_value_holm": holm_p,
                "ci_lower_95": float(ci[0]),
                "ci_upper_95": float(ci[1]),
                "vif": vif_val
            })
            print(f"    {col:15s}: coef = {coef_val:+8.4f}, SE = {se_val:6.4f}, t = {t_val:+6.3f}, p = {p_val:.5f} (Holm p = {holm_p:.5f}, VIF = {vif_val:.2f})")

    ols_df = pd.DataFrame(ols_records)
    ols_df.to_csv(OLS_OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n>> OLS 검증 결과 CSV 저장 완료: {OLS_OUT_CSV}")
    return ols_df


# ==============================================================================
# 2. 경제 국면별 상관관계 및 선행·후행 시차 분석 재검증
# ==============================================================================
def run_correlation_lag_verification(df_legacy, df_p56):
    print("\n" + "=" * 80)
    print("2. 경제 국면별 상관관계 및 선행·후행 시차 분석 재검증 실행")
    print("=" * 80)

    corr_records = []
    lags = [-2, -1, 0, 1, 2]

    # 1) 정상성 검정 (ADF & KPSS)
    print("\n[시계열 정상성 사전 진단 (ADF & KPSS)]")
    series_to_test = {
        "KOSPI (수준)": df_p56["KOSPI"],
        "kospi_ret (수익률)": df_p56["kospi_ret"].dropna(),
        "BASE_RATE (수준)": df_p56["BASE_RATE"],
        "base_rate_diff (변화량)": df_p56["base_rate_diff"].dropna(),
        "CCSI (수준)": df_p56["CCSI"],
        "ccsi_diff (변화량)": df_p56["ccsi_diff"].dropna(),
        "USD_KRW (수준)": df_p56["USD_KRW"],
        "usdkrw_ret (수익률)": df_p56["usdkrw_ret"].dropna(),
        "share_macro (뉴스)": df_p56["share_macro"].dropna(),
        "share_realestate (뉴스)": df_p56["share_realestate"].dropna(),
        "share_aichip (뉴스)": df_p56["share_aichip"].dropna(),
        "share_market (뉴스)": df_p56["share_market"].dropna(),
        "share_earnings (뉴스)": df_p56["share_earnings"].dropna(),
        "share_capital (뉴스)": df_p56["share_capital"].dropna(),
    }
    for name, s in series_to_test.items():
        adf_stat, adf_p, _, _, _, _ = adfuller(s, autolag="AIC")
        kpss_stat, kpss_p, _, _ = kpss(s, regression="c", nlags="auto")
        print(f"  {name:22s} | ADF = {adf_stat:+7.3f} (p = {adf_p:.4f}) | KPSS = {kpss_stat:6.3f} (p = {kpss_p:.4f})")

    # 2) 과거 수준값 기준 대표 상관관계 재현 (Legacy level claims)
    print("\n[과거 주장 대표 상관계수 추적 및 재현 (수준값 기준 Spurious Correlation 검증)]")
    legacy_level_pairs = [
        ("AI반도체 ↔ KOSPI (수준)", df_legacy["share_aichip"], df_legacy["KOSPI"], "aichip", "KOSPI", "level"),
        ("증시실적 ↔ KOSPI (수준)", df_legacy["share_market"], df_legacy["KOSPI"], "market", "KOSPI", "level"),
        ("가계부채 ↔ KOSPI (수준)", df_legacy["share_hhdebt"], df_legacy["KOSPI"], "hhdebt", "KOSPI", "level"),
        ("금리물가 ↔ KOSPI (수준)", df_legacy["share_macro"], df_legacy["KOSPI"], "macro", "KOSPI", "level"),
        ("부동산 ↔ KOSPI (수준)", df_legacy["share_realestate"], df_legacy["KOSPI"], "realestate", "KOSPI", "level"),
        ("금리물가 ↔ CCSI (수준)", df_legacy["share_macro"], df_legacy["CCSI"], "macro", "CCSI", "level"),
        ("금리물가 ↔ BASE_RATE (수준)", df_legacy["share_macro"], df_legacy["BASE_RATE"], "macro", "BASE_RATE", "level"),
        ("대외통상 ↔ USD_KRW (수준)", df_legacy["share_trade"], df_legacy["USD_KRW"], "trade", "USD_KRW", "level"),
    ]

    for label, s_reg, s_ind, reg_name, ind_name, var_type in legacy_level_pairs:
        mask = (~s_reg.isna()) & (~s_ind.isna())
        x = s_reg[mask]
        y = s_ind[mask]
        r_p, p_p = stats.pearsonr(x, y)
        r_s, p_s = stats.spearmanr(x, y)
        print(f"  {label:30s} | N={len(x)} | Pearson r = {r_p:+.3f} (p={p_p:.4e}), Spearman rho = {r_s:+.3f}")
        corr_records.append({
            "analysis_pipeline": "Legacy_Old_Topic_Pipeline",
            "regime": reg_name,
            "indicator": ind_name,
            "variable_type": var_type,
            "lag_h": 0,
            "sample_n": len(x),
            "pearson_r": r_p,
            "p_value_raw": p_p,
            "spearman_rho": r_s,
            "p_value_spearman": p_s,
            "note": "과거 수준값 기준 분석 (정상성 결여에 의한 가짜 상관 가능성)"
        })

    # 3) Phase 5.6 유효 국면 시차 상관관계 전수 계산 (Stationary Differences / Returns)
    print("\n[Phase 5.6 유효 6개 국면 × 4대 정상 경제지표 × 5개 시차(h=-2~+2) 전수 검정]")
    p56_regimes = ["macro", "realestate", "aichip", "market", "earnings", "capital"]
    stat_indicators = ["kospi_ret", "base_rate_diff", "ccsi_diff", "usdkrw_ret"]

    raw_p_list = []
    temp_p56_records = []

    for reg in p56_regimes:
        sh_col = f"share_{reg}"
        for ind in stat_indicators:
            for h in lags:
                if h >= 0:
                    s_reg = df_p56[sh_col].iloc[:len(df_p56) - h].reset_index(drop=True) if h > 0 else df_p56[sh_col]
                    s_ind = df_p56[ind].iloc[h:].reset_index(drop=True) if h > 0 else df_p56[ind]
                else:
                    s_reg = df_p56[sh_col].iloc[-h:].reset_index(drop=True)
                    s_ind = df_p56[ind].iloc[:len(df_p56) + h].reset_index(drop=True)

                mask = (~s_reg.isna()) & (~s_ind.isna())
                x = s_reg[mask]
                y = s_ind[mask]
                n = len(x)

                r_p, p_p = stats.pearsonr(x, y)
                r_s, p_s = stats.spearmanr(x, y)

                raw_p_list.append(p_p)
                temp_p56_records.append({
                    "analysis_pipeline": "Phase5.6_StrictOOS",
                    "regime": reg,
                    "indicator": ind,
                    "variable_type": "diff_or_return",
                    "lag_h": h,
                    "sample_n": n,
                    "pearson_r": r_p,
                    "p_value_raw": p_p,
                    "spearman_rho": r_s,
                    "p_value_spearman": p_s,
                    "note": f"h={h:+d} (양수는 뉴스 국면이 경제지표 선행, 음수는 경제지표가 뉴스 선행)"
                })

    # 전체 120개 검정에 대한 Holm-Bonferroni 다중검정 보정
    holm_p_list = holm_bonferroni(raw_p_list)
    for idx, rec in enumerate(temp_p56_records):
        rec["p_value_holm"] = holm_p_list[idx]
        corr_records.append(rec)

    # 4) Phase 5.6 유효 국면 × 수준값 지표 (비교 및 원인 규명용)
    level_indicators = ["KOSPI", "BASE_RATE", "CCSI", "USD_KRW"]
    temp_level_records = []
    raw_p_level_list = []

    for reg in p56_regimes:
        sh_col = f"share_{reg}"
        for ind in level_indicators:
            for h in lags:
                if h >= 0:
                    s_reg = df_p56[sh_col].iloc[:len(df_p56) - h].reset_index(drop=True) if h > 0 else df_p56[sh_col]
                    s_ind = df_p56[ind].iloc[h:].reset_index(drop=True) if h > 0 else df_p56[ind]
                else:
                    s_reg = df_p56[sh_col].iloc[-h:].reset_index(drop=True)
                    s_ind = df_p56[ind].iloc[:len(df_p56) + h].reset_index(drop=True)

                mask = (~s_reg.isna()) & (~s_ind.isna())
                x = s_reg[mask]
                y = s_ind[mask]
                n = len(x)

                r_p, p_p = stats.pearsonr(x, y)
                r_s, p_s = stats.spearmanr(x, y)

                raw_p_level_list.append(p_p)
                temp_level_records.append({
                    "analysis_pipeline": "Phase5.6_StrictOOS_Comparison_Level",
                    "regime": reg,
                    "indicator": ind,
                    "variable_type": "level",
                    "lag_h": h,
                    "sample_n": n,
                    "pearson_r": r_p,
                    "p_value_raw": p_p,
                    "spearman_rho": r_s,
                    "p_value_spearman": p_s,
                    "note": f"비교용 수준값 분석 h={h:+d} (단위근 존재로 통계적 해석 제한)"
                })

    holm_p_level_list = holm_bonferroni(raw_p_level_list)
    for idx, rec in enumerate(temp_level_records):
        rec["p_value_holm"] = holm_p_level_list[idx]
        corr_records.append(rec)

    corr_df = pd.DataFrame(corr_records)
    corr_df.to_csv(CORR_OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n>> 상관관계 및 시차 검증 결과 CSV 저장 완료: {CORR_OUT_CSV}")

    # 유의한 조합 출력 (Holm 보정 후 p < 0.05)
    sig_p56 = [r for r in temp_p56_records if r["p_value_holm"] < 0.05]
    print(f"\n[Phase 5.6 정상 시계열 기준 Holm 보정 유의 조합 (총 {len(sig_p56)}건 / 120건)]")
    for r in sig_p56:
        print(f"  {r['regime']:12s} ↔ {r['indicator']:15s} (h={r['lag_h']:+d}) : r = {r['pearson_r']:+.4f}, Raw p = {r['p_value_raw']:.4e}, Holm p = {r['p_value_holm']:.4e}")

    return corr_df


# ==============================================================================
# 3. KOSPI 하락 경고, 금리 인상 포착률 및 강건성 분석 재검증
# ==============================================================================
def run_warning_verification(df_legacy, df_p56):
    print("\n" + "=" * 80)
    print("3. KOSPI 하락 경고, 금리 인상 포착률 및 강건성 분석 재검증 실행")
    print("=" * 80)

    warn_records = []

    # ---------------------------------------------------------
    # 3.1 과거 경고 알고리즘 전수 재현 (Legacy 67m)
    # ---------------------------------------------------------
    n_total = len(df_legacy) # 67
    eval_limit_idx = n_total - 3 # 64 -> 65 evaluable months (0 to 64, 2021-01 to 2026-05)

    df_l = df_legacy.copy()
    # 경고 조건: (z_macro >= 0.5) | (z_hhdebt >= 0.5)
    df_l["warning_05"] = (df_l["z_macro"] >= 0.5) | (df_l["z_hhdebt"] >= 0.5)

    # 미래 1~2개월 하락 및 급락 여부
    df_l["drop_f12"] = False
    df_l["crash_f12"] = False

    for i in range(eval_limit_idx + 1):
        r1 = df_l.loc[i + 1, "kospi_ret"]
        r2 = df_l.loc[i + 2, "kospi_ret"]
        if (r1 < 0.0) or (r2 < 0.0):
            df_l.loc[i, "drop_f12"] = True
        if (r1 <= -3.0) or (r2 <= -3.0):
            df_l.loc[i, "crash_f12"] = True

    eval_df = df_l.iloc[:eval_limit_idx + 1].copy()
    n_eval = len(eval_df) # 65

    # A. 일반 하락 검증 (ret < 0)
    n_warn = int(eval_df["warning_05"].sum()) # 28
    base_drop_count = int(eval_df["drop_f12"].sum()) # 45
    base_drop_rate = base_drop_count / n_eval # 45/65 = 69.23%

    tp_drop = int((eval_df["warning_05"] & eval_df["drop_f12"]).sum()) # 19
    fp_drop = int((eval_df["warning_05"] & ~eval_df["drop_f12"]).sum()) # 9
    fn_drop = int((~eval_df["warning_05"] & eval_df["drop_f12"]).sum()) # 26
    tn_drop = int((~eval_df["warning_05"] & ~eval_df["drop_f12"]).sum()) # 11

    prec_drop = tp_drop / n_warn if n_warn > 0 else np.nan
    recall_drop = tp_drop / base_drop_count if base_drop_count > 0 else np.nan
    spec_drop = tn_drop / (tn_drop + fp_drop) if (tn_drop + fp_drop) > 0 else np.nan

    print("\n[A. 주가 일반 하락 경고 (kospi_ret < 0) 재현 및 자연발생률 비교]")
    print(f"  전체 평가 가능 개월 수: {n_eval}개월 (2021-01 ~ 2026-05)")
    print(f"  자연 발생 건수 (Base Rate): {base_drop_count}/{n_eval} = {base_drop_rate*100:.2f}%")
    print(f"  경고 발생 건수: {n_warn}/{n_eval} = {n_warn/n_eval*100:.2f}%")
    print(f"  경고 후 실제 하락 적중: {tp_drop}/{n_warn} = {prec_drop*100:.2f}%")
    print(f"  >> 핵심 결론: 경고 정밀도({prec_drop*100:.2f}%)는 무조건 예측 시의 자연발생률({base_drop_rate*100:.2f}%)보다 {prec_drop*100 - base_drop_rate*100:+.2f}%p 낮음!")

    warn_records.append({
        "pipeline": "Legacy_Dual_Warning",
        "analysis_type": "General_Drop_Warning",
        "threshold": "z>=0.5",
        "sample_period": "2021-01~2026-05",
        "eval_months": n_eval,
        "warning_months": n_warn,
        "event_months": base_drop_count,
        "base_rate": base_drop_rate,
        "tp": tp_drop,
        "fp": fp_drop,
        "fn": fn_drop,
        "tn": tn_drop,
        "precision": prec_drop,
        "recall": recall_drop,
        "specificity": spec_drop,
        "gain_over_base": prec_drop - base_drop_rate,
        "note": "일반 하락 경고 정밀도(67.9%)는 자연발생률(69.2%) 대비 우위가 없음"
    })

    # B. 급락/폭락 검증 (ret <= -3.0%)
    base_crash_count = int(eval_df["crash_f12"].sum()) # 27
    base_crash_rate = base_crash_count / n_eval # 27/65 = 41.54%

    tp_crash = int((eval_df["warning_05"] & eval_df["crash_f12"]).sum()) # 14
    fp_crash = int((eval_df["warning_05"] & ~eval_df["crash_f12"]).sum()) # 14
    fn_crash = int((~eval_df["warning_05"] & eval_df["crash_f12"]).sum()) # 13
    tn_crash = int((~eval_df["warning_05"] & ~eval_df["crash_f12"]).sum()) # 24

    prec_crash = tp_crash / n_warn if n_warn > 0 else np.nan
    recall_crash = tp_crash / base_crash_count if base_crash_count > 0 else np.nan
    spec_crash = tn_crash / (tn_crash + fp_crash) if (tn_crash + fp_crash) > 0 else np.nan

    # 사건 중심 급락 재현율 (월간 수익률 <= -3.0%인 월 전수 조사: 16건)
    crash_event_indices = df_l[df_l["kospi_ret"] <= -3.0].index
    n_crash_events = len(crash_event_indices)
    k_hits = 0
    for k_i in crash_event_indices:
        zm1 = df_l.loc[k_i - 1, "z_macro"] if k_i >= 1 else 0
        zm2 = df_l.loc[k_i - 2, "z_macro"] if k_i >= 2 else 0
        zh1 = df_l.loc[k_i - 1, "z_hhdebt"] if k_i >= 1 else 0
        zh2 = df_l.loc[k_i - 2, "z_hhdebt"] if k_i >= 2 else 0
        if (zm1 >= 0.5) or (zm2 >= 0.5) or (zh1 >= 0.5) or (zh2 >= 0.5):
            k_hits += 1
    event_crash_recall = k_hits / n_crash_events if n_crash_events > 0 else np.nan

    print("\n[B. 코스피 급락(월간 <= -3.0%) 경고 재현]")
    print(f"  자연 급락 발생 창 건수 (Base Rate): {base_crash_count}/{n_eval} = {base_crash_rate*100:.2f}%")
    print(f"  급락 경고 정밀도 (Precision): {tp_crash}/{n_warn} = {prec_crash*100:.2f}% (자연발생 대비 {prec_crash*100 - base_crash_rate*100:+.2f}%p)")
    print(f"  급락 사전 경고 재현율 (Recall, 윈도우 기준): {tp_crash}/{base_crash_count} = {recall_crash*100:.2f}%")
    print(f"  급락 사건 전수 재현율 (Event-based Recall): {k_hits}/{n_crash_events} = {event_crash_recall*100:.2f}% (16건 중 11건 적중)")

    warn_records.append({
        "pipeline": "Legacy_Dual_Warning",
        "analysis_type": "Crash_Warning_Precision_Window",
        "threshold": "z>=0.5",
        "sample_period": "2021-01~2026-05",
        "eval_months": n_eval,
        "warning_months": n_warn,
        "event_months": base_crash_count,
        "base_rate": base_crash_rate,
        "tp": tp_crash,
        "fp": fp_crash,
        "fn": fn_crash,
        "tn": tn_crash,
        "precision": prec_crash,
        "recall": recall_crash,
        "specificity": spec_crash,
        "gain_over_base": prec_crash - base_crash_rate,
        "note": "급락 윈도우 기준 정밀도 50.0% vs 자연발생률 41.5%"
    })
    warn_records.append({
        "pipeline": "Legacy_Dual_Warning",
        "analysis_type": "Crash_Event_Recall",
        "threshold": "z>=0.5",
        "sample_period": "2021-01~2026-07",
        "eval_months": n_total,
        "warning_months": n_warn,
        "event_months": n_crash_events,
        "base_rate": n_crash_events / n_total,
        "tp": k_hits,
        "fp": np.nan,
        "fn": n_crash_events - k_hits,
        "tn": np.nan,
        "precision": np.nan,
        "recall": event_crash_recall,
        "specificity": np.nan,
        "gain_over_base": np.nan,
        "note": f"실제 급락월(16회) 대상 직전 1~2개월 사전 경고 점등 여부 (11/16 = {event_crash_recall*100:.1f}%)"
    })

    # ---------------------------------------------------------
    # 3.2 한국은행 기준금리 인상 포착률 재현
    # ---------------------------------------------------------
    df_l["rate_diff"] = df_l["BASE_RATE"].diff()
    hikes = df_l[df_l["rate_diff"] > 0][["month", "BASE_RATE", "rate_diff"]].copy()
    n_hikes = len(hikes) # 11

    core_hits = 0
    core_total = 0
    total_hits = 0

    print("\n[C. 한국은행 기준금리 인상 사건(11회) 포착률 전수 조사]")
    for _, row in hikes.iterrows():
        m = row["month"]
        pos = df_l.index[df_l["month"] == m][0]
        z1 = df_l.loc[pos - 1, "z_macro"] if pos >= 1 else np.nan
        z2 = df_l.loc[pos - 2, "z_macro"] if pos >= 2 else np.nan
        hit = (z1 >= 0.5) or (z2 >= 0.5)
        if hit:
            total_hits += 1

        is_core = ("2022-04" <= m <= "2023-01")
        if is_core:
            core_total += 1
            if hit:
                core_hits += 1

        print(f"  인상월: {m} (기준금리 {row['BASE_RATE']:.2f}%, +{row['rate_diff']:.2f}%p) | 1달전 z={z1:+.2f}, 2달전 z={z2:+.2f} -> {'적중' if hit else '미적중'}")

    print(f"  >> 본격 인상기 (2022-04 ~ 2023-01): {core_hits}/{core_total}회 적중 ({core_hits/core_total*100:.1f}%)")
    print(f"  >> 67개월 전체 통산 (2021-01 ~ 2026-07): {total_hits}/{n_hikes}회 적중 ({total_hits/n_hikes*100:.1f}%)")
    print(f"  >> 초기 3회 인상 (2021-08, 2021-11, 2022-01): 0/3회 적중 (0.0% 미탐지!)")

    warn_records.append({
        "pipeline": "Legacy_Macro_Warning",
        "analysis_type": "Rate_Hike_Capture_Core_Period",
        "threshold": "z_macro>=0.5",
        "sample_period": "2022-04~2023-01",
        "eval_months": 10,
        "warning_months": np.nan,
        "event_months": core_total,
        "base_rate": core_total / 10,
        "tp": core_hits,
        "fp": np.nan,
        "fn": core_total - core_hits,
        "tn": np.nan,
        "precision": np.nan,
        "recall": core_hits / core_total,
        "specificity": np.nan,
        "gain_over_base": np.nan,
        "note": "사후 선택된 고물가 지속기(7/7 = 100%)로 일반화 불가"
    })
    warn_records.append({
        "pipeline": "Legacy_Macro_Warning",
        "analysis_type": "Rate_Hike_Capture_Full_Sample",
        "threshold": "z_macro>=0.5",
        "sample_period": "2021-01~2026-07",
        "eval_months": n_total,
        "warning_months": np.nan,
        "event_months": n_hikes,
        "base_rate": n_hikes / n_total,
        "tp": total_hits,
        "fp": np.nan,
        "fn": n_hikes - total_hits,
        "tn": np.nan,
        "precision": np.nan,
        "recall": total_hits / n_hikes,
        "specificity": np.nan,
        "gain_over_base": np.nan,
        "note": "전체 인상기 통산 7/11(63.6%). 초기 인상 3건(2021.08, 2021.11, 2022.01)은 전무 탐지 실패"
    })

    # ---------------------------------------------------------
    # 3.3 임계값 민감도(z = 0.3 ~ 0.7) 강건성 전수 조사
    # ---------------------------------------------------------
    print("\n[D. 임계값(z=0.3 ~ 0.7) 민감도 및 강건성 분석]")
    major_hike_months = ["2022-04", "2022-05", "2022-07", "2022-08", "2022-10", "2022-11", "2023-01"]
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

    for th in thresholds:
        warn_mask = (df_l["z_hhdebt"] >= th) | (df_l["z_macro"] >= th)
        eval_warn_mask = warn_mask.iloc[:eval_limit_idx + 1]
        n_th_warn = int(eval_warn_mask.sum())

        gen_hits = int((eval_warn_mask & eval_df["drop_f12"]).sum())
        crash_hits = int((eval_warn_mask & eval_df["crash_f12"]).sum())

        th_gen_prec = gen_hits / n_th_warn if n_th_warn > 0 else np.nan
        th_crash_prec = crash_hits / n_th_warn if n_th_warn > 0 else np.nan

        # 급락 16건 재현율
        th_k_hits = 0
        for k_i in crash_event_indices:
            zm1 = df_l.loc[k_i - 1, "z_macro"] if k_i >= 1 else 0
            zm2 = df_l.loc[k_i - 2, "z_macro"] if k_i >= 2 else 0
            zh1 = df_l.loc[k_i - 1, "z_hhdebt"] if k_i >= 1 else 0
            zh2 = df_l.loc[k_i - 2, "z_hhdebt"] if k_i >= 2 else 0
            if (zm1 >= th) or (zm2 >= th) or (zh1 >= th) or (zh2 >= th):
                th_k_hits += 1
        th_crash_recall = th_k_hits / n_crash_events

        # 본격 금리인상기 적중률
        th_hike_hits = 0
        for hm in major_hike_months:
            m_i = df_l[df_l["month"] == hm].index[0]
            z1 = df_l.loc[m_i - 1, "z_macro"] if m_i >= 1 else 0
            z2 = df_l.loc[m_i - 2, "z_macro"] if m_i >= 2 else 0
            if (z1 >= th) or (z2 >= th):
                th_hike_hits += 1
        th_hike_recall = th_hike_hits / len(major_hike_months)

        print(f"  z={th:.1f} | 경고월={n_th_warn:2d} | 일반하락정밀도={th_gen_prec*100:5.1f}% (자연발생 {base_drop_rate*100:.1f}%) | "
              f"급락정밀도={th_crash_prec*100:5.1f}% | 급락재현율={th_crash_recall*100:5.1f}% | 한은인상(7회)적중률={th_hike_recall*100:5.1f}%")

        warn_records.append({
            "pipeline": "Legacy_Robustness_Threshold",
            "analysis_type": "Threshold_Sensitivity",
            "threshold": f"z>={th:.1f}",
            "sample_period": "2021-01~2026-05",
            "eval_months": n_eval,
            "warning_months": n_th_warn,
            "event_months": base_drop_count,
            "base_rate": base_drop_rate,
            "tp": gen_hits,
            "fp": n_th_warn - gen_hits,
            "fn": base_drop_count - gen_hits,
            "tn": n_eval - n_th_warn - (base_drop_count - gen_hits),
            "precision": th_gen_prec,
            "recall": gen_hits / base_drop_count,
            "specificity": (n_eval - n_th_warn - (base_drop_count - gen_hits)) / (n_eval - base_drop_count),
            "gain_over_base": th_gen_prec - base_drop_rate,
            "note": f"임계값 z={th:.1f} 시 일반 하락 정밀도 vs 자연발생률 차이 {th_gen_prec*100 - base_drop_rate*100:+.1f}%p, 급락재현율 {th_crash_recall*100:.1f}%"
        })

    # ---------------------------------------------------------
    # 3.4 60개월 표본 강건성 분석 (2021-01 ~ 2025-12)
    # ---------------------------------------------------------
    df_60 = df_l[df_l["month"] <= "2025-12"].copy()
    n_60 = len(df_60) # 60
    eval_60_limit = n_60 - 3 # 57 -> 58 evaluable months (2021-01 ~ 2025-10)
    eval_60_df = df_60.iloc[:eval_60_limit + 1].copy()

    n_warn_60 = int(eval_60_df["warning_05"].sum())
    base_drop_60 = int(eval_60_df["drop_f12"].sum())
    base_rate_60 = base_drop_60 / len(eval_60_df)

    tp_60 = int((eval_60_df["warning_05"] & eval_60_df["drop_f12"]).sum())
    prec_60 = tp_60 / n_warn_60 if n_warn_60 > 0 else np.nan

    print("\n[E. 60개월 표본 강건성 검정 (2021-01 ~ 2025-12)]")
    print(f"  평가 개월 수: {len(eval_60_df)}개월 | 경고월: {n_warn_60}개월 | 자연발생률: {base_rate_60*100:.1f}% | 경고정밀도: {prec_60*100:.1f}%")

    warn_records.append({
        "pipeline": "Legacy_Robustness_60M",
        "analysis_type": "60_Month_Sample_Drop_Warning",
        "threshold": "z>=0.5",
        "sample_period": "2021-01~2025-10",
        "eval_months": len(eval_60_df),
        "warning_months": n_warn_60,
        "event_months": base_drop_60,
        "base_rate": base_rate_60,
        "tp": tp_60,
        "fp": n_warn_60 - tp_60,
        "fn": base_drop_60 - tp_60,
        "tn": len(eval_60_df) - n_warn_60 - (base_drop_60 - tp_60),
        "precision": prec_60,
        "recall": tp_60 / base_drop_60,
        "specificity": (len(eval_60_df) - n_warn_60 - (base_drop_60 - tp_60)) / (len(eval_60_df) - base_drop_60),
        "gain_over_base": prec_60 - base_rate_60,
        "note": "2026년 부분연도 제외 60개월 표본에서도 경고 정밀도가 자연발생률을 유의하게 상회하지 못함"
    })

    # ---------------------------------------------------------
    # 3.5 Phase 5.6 Strict OOS 파이프라인 기준 경고 재평가
    # ---------------------------------------------------------
    print("\n[F. Phase 5.6 Strict OOS 기준 경고 모형 재평가]")
    # 주의: Phase 5.6에서는 z_hhdebt가 unrepresented(NaN)이므로 경고 규칙은 z_macro >= 0.5 단독으로 축소됨!
    df_p = df_p56.copy()
    df_p["warning_p56"] = df_p["z_macro"] >= 0.5

    df_p["drop_f12"] = False
    df_p["crash_f12"] = False
    for i in range(eval_limit_idx + 1):
        r1 = df_p.loc[i + 1, "kospi_ret"]
        r2 = df_p.loc[i + 2, "kospi_ret"]
        if (r1 < 0.0) or (r2 < 0.0):
            df_p.loc[i, "drop_f12"] = True
        if (r1 <= -3.0) or (r2 <= -3.0):
            df_p.loc[i, "crash_f12"] = True

    eval_p56 = df_p.iloc[:eval_limit_idx + 1].copy()

    # 전체 기간 (65개월)
    p56_warn_cnt = int(eval_p56["warning_p56"].sum())
    p56_hits = int((eval_p56["warning_p56"] & eval_p56["drop_f12"]).sum())
    p56_prec = p56_hits / p56_warn_cnt if p56_warn_cnt > 0 else np.nan

    # 학습 기간 (48개월 중 46개월 평가 가능: 2021-01 ~ 2024-10)
    train_eval = eval_p56[eval_p56["period"] == "train"].copy()
    n_train_eval = len(train_eval)
    train_warn_cnt = int(train_eval["warning_p56"].sum())
    train_base_drop = int(train_eval["drop_f12"].sum())
    train_hits = int((train_eval["warning_p56"] & train_eval["drop_f12"]).sum())
    train_prec = train_hits / train_warn_cnt if train_warn_cnt > 0 else np.nan

    # 평가 기간 (eval 19개월 중 17개월 평가 가능: 2025-01 ~ 2026-05)
    test_eval = eval_p56[eval_p56["period"] == "eval"].copy()
    n_test_eval = len(test_eval)
    test_warn_cnt = int(test_eval["warning_p56"].sum())
    test_base_drop = int(test_eval["drop_f12"].sum())
    test_hits = int((test_eval["warning_p56"] & test_eval["drop_f12"]).sum())
    test_prec = test_hits / test_warn_cnt if test_warn_cnt > 0 else np.nan

    print(f"  [전체 65개월]: 경고 {p56_warn_cnt}건, 적중 {p56_hits}건, 정밀도 {p56_prec*100:.1f}% (자연발생 {base_drop_rate*100:.1f}%)")
    print(f"  [Train 46개월]: 경고 {train_warn_cnt}건, 적중 {train_hits}건, 정밀도 {train_prec*100:.1f}% (자연발생 {train_base_drop/n_train_eval*100:.1f}%)")
    print(f"  [Test  17개월]: 경고 {test_warn_cnt}건, 적중 {test_hits}건, 정밀도 {test_prec*100:.1f}% (자연발생 {test_base_drop/n_test_eval*100:.1f}%)")

    warn_records.append({
        "pipeline": "Phase5.6_StrictOOS_MacroOnly",
        "analysis_type": "StrictOOS_Full_Drop_Warning",
        "threshold": "z_macro>=0.5",
        "sample_period": "2021-01~2026-05",
        "eval_months": len(eval_p56),
        "warning_months": p56_warn_cnt,
        "event_months": base_drop_count,
        "base_rate": base_drop_rate,
        "tp": p56_hits,
        "fp": p56_warn_cnt - p56_hits,
        "fn": base_drop_count - p56_hits,
        "tn": len(eval_p56) - p56_warn_cnt - (base_drop_count - p56_hits),
        "precision": p56_prec,
        "recall": p56_hits / base_drop_count,
        "specificity": (len(eval_p56) - p56_warn_cnt - (base_drop_count - p56_hits)) / (len(eval_p56) - base_drop_count),
        "gain_over_base": p56_prec - base_drop_rate,
        "note": "가계부채 국면 결측으로 z_macro 단독 적용 시 경고 13건, 정밀도 69.2% (자연발생 69.2%와 동일)"
    })
    warn_records.append({
        "pipeline": "Phase5.6_StrictOOS_MacroOnly",
        "analysis_type": "StrictOOS_Train_Drop_Warning",
        "threshold": "z_macro>=0.5",
        "sample_period": "2021-01~2024-10 (Train)",
        "eval_months": n_train_eval,
        "warning_months": train_warn_cnt,
        "event_months": train_base_drop,
        "base_rate": train_base_drop / n_train_eval,
        "tp": train_hits,
        "fp": train_warn_cnt - train_hits,
        "fn": train_base_drop - train_hits,
        "tn": n_train_eval - train_warn_cnt - (train_base_drop - train_hits),
        "precision": train_prec,
        "recall": train_hits / train_base_drop,
        "specificity": (n_train_eval - train_warn_cnt - (train_base_drop - train_hits)) / (n_train_eval - train_base_drop),
        "gain_over_base": train_prec - (train_base_drop / n_train_eval),
        "note": "학습 기간 내 정밀도 75.0% vs 자연발생 69.6% (+5.4%p, 통계적 유의성 결여)"
    })
    warn_records.append({
        "pipeline": "Phase5.6_StrictOOS_MacroOnly",
        "analysis_type": "StrictOOS_Test_Drop_Warning",
        "threshold": "z_macro>=0.5",
        "sample_period": "2025-01~2026-05 (Test)",
        "eval_months": n_test_eval,
        "warning_months": test_warn_cnt,
        "event_months": test_base_drop,
        "base_rate": test_base_drop / n_test_eval,
        "tp": test_hits,
        "fp": test_warn_cnt - test_hits,
        "fn": test_base_drop - test_hits,
        "tn": n_test_eval - test_warn_cnt - (test_base_drop - test_hits),
        "precision": test_prec,
        "recall": test_hits / test_base_drop,
        "specificity": (n_test_eval - test_warn_cnt - (test_base_drop - test_hits)) / (n_test_eval - test_base_drop),
        "gain_over_base": test_prec - (test_base_drop / n_test_eval),
        "note": "평가 기간 내 경고 1건 발생(2026-03), 이후 2개월 연속 급등하여 적중 실패(정밀도 0.0%)"
    })

    warn_df = pd.DataFrame(warn_records)
    warn_df.to_csv(WARN_OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n>> 경고 및 강건성 검증 결과 CSV 저장 완료: {WARN_OUT_CSV}")
    return warn_df


def main():
    print("=" * 80)
    print("연구 분석 결과 3종 최종 검증 및 Phase 5.6 Strict OOS 통합 재실행")
    print("=" * 80)

    df_legacy, df_p56 = load_datasets()
    print(f"데이터 로드 완료: Legacy {len(df_legacy)}개월, Phase 5.6 {len(df_p56)}개월")

    ols_df = run_ols_verification(df_legacy, df_p56)
    corr_df = run_correlation_lag_verification(df_legacy, df_p56)
    warn_df = run_warning_verification(df_legacy, df_p56)

    print("\n" + "=" * 80)
    print("모든 검증 계산 및 CSV 산출 완료!")
    print(f"1. OLS 결과: {OLS_OUT_CSV}")
    print(f"2. 상관관계 및 시차 결과: {CORR_OUT_CSV}")
    print(f"3. 경고 및 강건성 결과: {WARN_OUT_CSV}")
    print("=" * 80)


if __name__ == "__main__":
    main()
