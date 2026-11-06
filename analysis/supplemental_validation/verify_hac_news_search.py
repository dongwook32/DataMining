"""연구 B 보강: 주별 뉴스-검색 상관분석에 대한 Newey-West HAC 검정 스크립트.

기존 news_search_lag_results.csv의 Pearson 상관계수에 더하여,
시계열 자기상관 및 이분산성을 고려한 Newey-West HAC 표준오차(maxlags=4) 기반 t-통계량 및 p-value를 계산하고
Holm 보정 p-value를 산출하여 data/processed/supplemental_validation/news_search_hac_results.csv 에 저장한다.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PANEL_PATH = ROOT / "data" / "processed" / "supplemental_validation" / "news_search_weekly_panel.csv"
OUT_DIR = ROOT / "data" / "processed" / "supplemental_validation"

PAIRS = [
    ("macro", "search_macro_combined", "금리·물가 뉴스 ↔ 금리+물가 검색"),
    ("macro", "search_macro_interest", "금리·물가 뉴스 ↔ 금리 검색"),
    ("macro", "search_macro_inflation", "금리·물가 뉴스 ↔ 물가 검색"),
    ("realestate", "search_realestate", "부동산 뉴스 ↔ 부동산 검색"),
    ("aichip", "search_aichip", "AI·반도체 뉴스 ↔ AI반도체 검색"),
    ("market", "search_market", "시황 뉴스 ↔ 국내증시 검색"),
    ("earnings", "search_earnings", "기업실적 뉴스 ↔ 기업실적 검색"),
    ("capital", "search_capital", "자본거래 뉴스 ↔ 공모주 검색"),
]

def run_hac_verification():
    panel = pd.read_csv(PANEL_PATH)
    
    results = []
    for split_name, mask in [
        ("Full", np.ones(len(panel), dtype=bool)),
        ("Train (2021~2024)", (panel["period"] == "train").to_numpy()),
        ("Eval OOS (2025~2026)", (panel["period"] == "eval").to_numpy())
    ]:
        sub = panel[mask].reset_index(drop=True)
        N_sub = len(sub)
        
        for reg, scol, label in PAIRS:
            dx = sub[f"news_share_{reg}"].diff().to_numpy()
            dy = sub[scol].diff().to_numpy()
            
            for h in [-1, 0, 1]:
                if h == 0:
                    xv = dx[1:]
                    yv = dy[1:]
                elif h == 1:
                    xv = dx[1:-1]
                    yv = dy[2:]
                elif h == -1:
                    xv = dx[2:]
                    yv = dy[1:-1]
                    
                valid = (~np.isnan(xv)) & (~np.isnan(yv))
                x_c = xv[valid]
                y_c = yv[valid]
                n_obs = len(x_c)
                
                if n_obs < 15:
                    results.append({
                        "split": split_name, "regime": reg, "search_group": scol, "pair_label": label,
                        "lag_h": h, "sample_n": n_obs, "pearson_r": np.nan, "hac_se": np.nan, "hac_t": np.nan, "hac_p_raw": np.nan
                    })
                    continue
                    
                zx = (x_c - x_c.mean()) / x_c.std(ddof=1)
                zy = (y_c - y_c.mean()) / y_c.std(ddof=1)
                
                # OLS zy = beta * zx + const with HAC
                X_mat = sm.add_constant(zx)
                res_hac = sm.OLS(zy, X_mat).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
                
                r = float(res_hac.params[1])
                se = float(res_hac.bse[1])
                t_stat = float(res_hac.tvalues[1])
                p_val = float(res_hac.pvalues[1])
                
                results.append({
                    "split": split_name, "regime": reg, "search_group": scol, "pair_label": label,
                    "lag_h": h, "sample_n": n_obs, "pearson_r": round(r, 4),
                    "hac_se": round(se, 4), "hac_t": round(t_stat, 4), "hac_p_raw": p_val
                })
                
    df_res = pd.DataFrame(results)
    
    # 구간별 24개 검정 Holm 보정
    adjusted_chunks = []
    for sp, sub in df_res.groupby("split", as_index=False):
        sub_c = sub.copy().reset_index(drop=True)
        p_vals = sub_c["hac_p_raw"].to_numpy()
        valid = ~np.isnan(p_vals)
        p_valid = p_vals[valid]
        order = np.argsort(p_valid)
        n_m = len(p_valid)
        
        adj = np.empty(n_m, dtype=np.float64)
        for i, idx in enumerate(order):
            adj[idx] = min(1.0, p_valid[idx] * (n_m - i))
        for i in range(1, n_m):
            prev_idx = order[i-1]
            curr_idx = order[i]
            adj[curr_idx] = max(adj[curr_idx], adj[prev_idx])
            
        full_adj = np.full(len(sub_c), np.nan)
        full_adj[valid] = adj
        sub_c["hac_p_holm"] = full_adj
        adjusted_chunks.append(sub_c)
        
    df_out = pd.concat(adjusted_chunks, ignore_index=True)
    df_out.to_csv(OUT_DIR / "news_search_hac_results.csv", index=False, encoding="utf-8-sig")
    print("Newey-West HAC 검정 완료: news_search_hac_results.csv 저장 완료.")

if __name__ == "__main__":
    run_hac_verification()

