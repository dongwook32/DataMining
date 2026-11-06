"""67개월 전체 사건 전수 조사 및 핵심 실증 수치 재현 스크립트.

연구의 4대 핵심 실증 성과를 단 1초 만에 전수 재현 및 검증한다:
1. 한국은행 기준금리 인상 사건 사전 적중률 (67개월 전체 7/11, 본격 인상기 7/7 100%)
2. 주식시장(코스피) 악재 경고 정밀도 (일반 하락 19/28 = 67.9%, 급락 14/28 = 50.0%) 및 급락 재현율 (11/16 = 68.8%)
3. 주요 지표별 시차 선행성 피크 (CCSI 1달 선행, 기준금리 2달 선행, 코스피 2달 선행)
4. HAC OLS 회귀분석 모형 성과 (과거 변동성 기준 코스피 표준화 수익률 R²=22.8%, F=4.75, p=0.00016)

실행:
    python -m analysis.verify_leading_episodes
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

from config import project_root
from analysis.event_definitions import KOSPI_CRASH_THRESHOLD, KOSPI_DROP_THRESHOLD

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"


def load_data() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_PATH, dtype={"month": str})
    regimes = pd.read_csv(REGIME_PATH, dtype={"month": str})
    df = regimes.merge(panel, on="month", how="inner").sort_values("month").reset_index(drop=True)
    return df


def verify_bok_hikes(df: pd.DataFrame) -> None:
    print("=" * 70)
    print("1. 한국은행 기준금리 인상 사건 전수 조사 (67개월)")
    print("=" * 70)
    
    # 금리·물가 z-score (ddof=1)
    sh_macro = df["share_macro"]
    z_macro = (sh_macro - sh_macro.mean()) / sh_macro.std(ddof=1)
    df["z_macro"] = z_macro
    
    # 기준금리 인상월 추출
    df["rate_diff"] = df["BASE_RATE"].diff()
    hikes = df[df["rate_diff"] > 0][["month", "BASE_RATE", "rate_diff"]].copy()
    
    core_hits = 0
    core_total = 0
    total_hits = 0
    
    for _, row in hikes.iterrows():
        m = row["month"]
        pos = df.index[df["month"] == m][0]
        z1 = df.loc[pos - 1, "z_macro"] if pos >= 1 else np.nan
        z2 = df.loc[pos - 2, "z_macro"] if pos >= 2 else np.nan
        m1 = df.loc[pos - 1, "month"] if pos >= 1 else ""
        m2 = df.loc[pos - 2, "month"] if pos >= 2 else ""
        
        hit = (z1 >= 0.5) or (z2 >= 0.5)
        if hit:
            total_hits += 1
            
        is_core = ("2022-04" <= m <= "2023-01")
        if is_core:
            core_total += 1
            if hit:
                core_hits += 1
                
        status = "★ 적중 (사전경고)" if hit else "미적중"
        print(f"인상월: {m} (기준금리 {row['BASE_RATE']:.2f}%, +{row['rate_diff']:.2f}%p) | "
              f"1달전 {m1}(z={z1:+.2f}), 2달전 {m2}(z={z2:+.2f}) -> {status}")
              
    print("-" * 70)
    print(f">> [본격 인상기 (2022.04~2023.01)]: {core_hits}/{core_total}회 적중 ({core_hits/core_total*100:.1f}%)")
    print(f">> [67개월 전체 통산]: {total_hits}/{len(hikes)}회 적중 ({total_hits/len(hikes)*100:.1f}%)\n")


def verify_stock_drop_warning(df: pd.DataFrame) -> None:
    print("=" * 70)
    print("2. 주식시장(코스피) 악재 경고등 정밀도 및 급락 재현율 전수 조사 (z >= 0.5)")
    print("=" * 70)
    
    z_macro = (df["share_macro"] - df["share_macro"].mean()) / df["share_macro"].std(ddof=1)
    z_hhdebt = (df["share_hhdebt"] - df["share_hhdebt"].mean()) / df["share_hhdebt"].std(ddof=1)
    df["z_macro"] = z_macro
    df["z_hhdebt"] = z_hhdebt
    
    n_total = len(df)
    eval_limit_idx = n_total - 3  # 마지막 2개월(2026-06, 2026-07)은 t+1, t+2 전부 관측 불가하여 제외

    # (1) 조기경보 정밀도 (Precision) 전수 조사
    df["warning"] = (df["z_macro"] >= 0.5) | (df["z_hhdebt"] >= 0.5)
    warn_df = df[df["warning"]].copy()
    
    # 평가 가능한 경고월 필터링
    eval_warn_df = warn_df[warn_df.index <= eval_limit_idx].copy()
    excluded_warn_df = warn_df[warn_df.index > eval_limit_idx].copy()
    
    gen_hits = 0
    crash_hits = 0
    
    print("[악재 경고월별 t+1, t+2 관측 및 적중 여부]")
    for idx, row in eval_warn_df.iterrows():
        pos = row.name
        ret1 = df.loc[pos + 1, "kospi_ret"]
        ret2 = df.loc[pos + 2, "kospi_ret"]
        m1 = df.loc[pos + 1, "month"]
        m2 = df.loc[pos + 2, "month"]
        
        hit_gen = (ret1 < KOSPI_DROP_THRESHOLD) or (ret2 < KOSPI_DROP_THRESHOLD)
        hit_crash = (ret1 <= KOSPI_CRASH_THRESHOLD) or (ret2 <= KOSPI_CRASH_THRESHOLD)
        
        if hit_gen:
            gen_hits += 1
        if hit_crash:
            crash_hits += 1
            
        status_gen = "일반하락 적중" if hit_gen else "하락 미적중"
        status_crash = "★ 급락 적중" if hit_crash else "급락 미적중"
        
        print(f"경고월: {row['month']} (금리물가 z={row['z_macro']:+.2f}, 가계대출 z={row['z_hhdebt']:+.2f}) | "
              f"1달뒤 {m1}({ret1:+.2f}%), 2달뒤 {m2}({ret2:+.2f}%) -> {status_gen} | {status_crash}")
              
    if len(excluded_warn_df) > 0:
        print(f"\n[평가 제외된 경고월 (이후 1~2개월 미관측)]: {excluded_warn_df['month'].tolist()}")
    else:
        print(f"\n[평가 제외된 경고월]: 없음 (모든 경고월이 2026-05 이전 관측 구간에 포함)")
        
    print("-" * 70)
    print(f">> 총 경고 점등 개월 수: {len(warn_df)}개월 (평가 가능 경고월: {len(eval_warn_df)}개월)")
    print(f">> [지표 1. 일반 하락 정밀도 (ret < 0)]: {gen_hits}/{len(eval_warn_df)} = {gen_hits/len(eval_warn_df)*100:.1f}%")
    print(f">> [지표 2. 급락 경고 정밀도 (ret <= {KOSPI_CRASH_THRESHOLD}%)]: {crash_hits}/{len(eval_warn_df)} = {crash_hits/len(eval_warn_df)*100:.1f}%")
    
    # 65개월 전체 기간의 베이스 레이트 (경고 점등 여부와 무관한 자연 발생 확률)
    base_gen = 0
    base_crash = 0
    for i in range(eval_limit_idx + 1):
        r1 = df.loc[i + 1, "kospi_ret"]
        r2 = df.loc[i + 2, "kospi_ret"]
        if (r1 < KOSPI_DROP_THRESHOLD) or (r2 < KOSPI_DROP_THRESHOLD):
            base_gen += 1
        if (r1 <= KOSPI_CRASH_THRESHOLD) or (r2 <= KOSPI_CRASH_THRESHOLD):
            base_crash += 1
    eval_n = eval_limit_idx + 1
    print(f">> [비교: 전체 65개월 기준 자연 발생률 (Base Rate)]")
    print(f"   - 일반 하락 자연 발생률: {base_gen}/{eval_n} = {base_gen/eval_n*100:.1f}%")
    print(f"   - 급락 사건 자연 발생률: {base_crash}/{eval_n} = {base_crash/eval_n*100:.1f}%\n")

    # (2) 코스피 급락 사전 경고 재현율 (Recall) 전수 조사
    crashes = df[df["kospi_ret"] <= KOSPI_CRASH_THRESHOLD].copy()
    n_crashes = len(crashes)
    
    print("-" * 70)
    print(f"[코스피 급락 사건 (kospi_ret <= {KOSPI_CRASH_THRESHOLD}%) 전수 조사 (총 {n_crashes}개월)]")
    
    k_hits = 0
    hit_list = []
    miss_list = []
    
    for idx, row in crashes.iterrows():
        pos = row.name
        z_m1 = df.loc[pos - 1, "z_macro"] if pos >= 1 else 0
        z_m2 = df.loc[pos - 2, "z_macro"] if pos >= 2 else 0
        z_h1 = df.loc[pos - 1, "z_hhdebt"] if pos >= 1 else 0
        z_h2 = df.loc[pos - 2, "z_hhdebt"] if pos >= 2 else 0
        
        warned = (z_m1 >= 0.5) or (z_m2 >= 0.5) or (z_h1 >= 0.5) or (z_h2 >= 0.5)
        m_str = row["month"]
        ret_val = row["kospi_ret"]
        
        if warned:
            k_hits += 1
            hit_list.append(m_str)
            status = "★ 적중 (사전경고 점등)"
        else:
            miss_list.append(m_str)
            status = "미탐지"
            
        print(f"급락월: {m_str} ({ret_val:+.2f}%) | 직전 1달전(물가 z={z_m1:+.2f}, 대출 z={z_h1:+.2f}), "
              f"2달전(물가 z={z_m2:+.2f}, 대출 z={z_h2:+.2f}) -> {status}")
              
    print("-" * 70)
    print(f">> 실제 코스피 급락월 수: {n_crashes}개월")
    print(f">> 사전 경고 적중 급락월 수: {k_hits}개월")
    print(f">> 급락 사전 경고 재현율 (Recall): {k_hits}/{n_crashes} = {k_hits/n_crashes*100:.1f}%")
    print(f">> 적중 급락월 목록 ({len(hit_list)}개): {hit_list}")
    print(f">> 미탐지 급락월 목록 ({len(miss_list)}개): {miss_list}\n")


def verify_lead_lag(df: pd.DataFrame) -> None:
    print("=" * 70)
    print("3. 핵심 대표 4대 지표 시차 선행성 교차상관 (Lead-Lag Matrix)")
    print("=" * 70)
    
    pairs = [
        ("소비자심리지수 (CCSI)", "CCSI", "share_macro", "금리·물가"),
        ("한국은행 기준금리", "BASE_RATE", "share_macro", "금리·물가"),
        ("코스피 주가지수", "KOSPI", "share_hhdebt", "가계대출"),
        ("원/달러 환율", "USD_KRW", "share_trade", "대외통상"),
    ]
    
    lags = [-2, -1, 0, 1, 2]
    for label, ind_col, sh_col, reg_name in pairs:
        r_vals = []
        for h in lags:
            if h >= 0:
                s1 = df[sh_col].iloc[:len(df) - h] if h > 0 else df[sh_col]
                s2 = df[ind_col].iloc[h:].reset_index(drop=True) if h > 0 else df[ind_col]
            else:
                s1 = df[sh_col].iloc[-h:].reset_index(drop=True)
                s2 = df[ind_col].iloc[:len(df) + h]
            r = s1.corr(s2)
            r_vals.append(r)
        
        peak_idx = int(np.argmax(np.abs(r_vals)))
        peak_h = lags[peak_idx]
        formatted = " | ".join([f"h={h:+d}: {r:+.3f}" for h, r in zip(lags, r_vals)])
        print(f"[{label} ↔ {reg_name}]")
        print(f"   {formatted}")
        print(f"   >> 피크: h = {peak_h:+d} (상관계수 r = {r_vals[peak_idx]:+.3f})\n")


def verify_hac_regression(df: pd.DataFrame) -> None:
    print("=" * 70)
    print("4. HAC OLS 다중 회귀분석 모형 성과 (maxlags=3)")
    print("=" * 70)
    
    slugs = ["macro", "realestate", "hhdebt", "trade", "aichip", "market", "earnings", "capital"]
    share_cols = [f"share_{s}" for s in slugs]
    Z = df[share_cols].apply(lambda s: (s - s.mean()) / s.std(ddof=1))
    X = sm.add_constant(Z)
    
    # 1) 과거 12개월 표준편차로 표준화한 코스피 월간 수익률 (kospi_ret_std)
    y_std = df["kospi_ret_std"]
    m_std = sm.OLS(y_std, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    w_std = m_std.fvalue * 8.0
    
    # 2) 코스피 월간 로그수익률 (kospi_ret)
    y_ret = df["kospi_ret"]
    m_ret = sm.OLS(y_ret, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    
    print(f"[과거 12개월 표준편차로 표준화한 코스피 월간 수익률 (kospi_ret_std)]")
    print(f"   R² = {m_std.rsquared*100:.2f}%, F-통계량 = {m_std.fvalue:.3f} (Wald={w_std:.2f}), p-value = {m_std.f_pvalue:.6f}")
    print(f"[코스피 월간 로그수익률 (kospi_ret)]")
    print(f"   R² = {m_ret.rsquared*100:.2f}%, F-통계량 = {m_ret.fvalue:.3f}, p-value = {m_ret.f_pvalue:.6f}")
    print("=" * 70)


def main() -> None:
    df = load_data()
    verify_bok_hikes(df)
    verify_stock_drop_warning(df)
    verify_lead_lag(df)
    verify_hac_regression(df)


if __name__ == "__main__":
    main()
