"""네이버 데이터랩 공통 분모(anchor_score = '은행') 민감도 및 왜곡 여부 검증 스크립트.

검증 내용:
1. 주간 1차 차분된 공통 앵커 지수(d_anchor_score, 키워드 '은행')와 6대 뉴스 국면 비중 1차 차분(d_news_share) 간의 상관관계 검정
2. 각 검색어 그룹의 원시 분자 점수(score: 단일 API 호출 내 고정 기간[2016-01-01~2026-07-31] 최대값 대비 상대 검색량으로, 시변 분모 anchor_score로 나누지 않은 순수 검색 지표)의 주간 1차 차분(d_raw_score)과 뉴스 국면 비중 1차 차분 간의 상관관계 및 Newey-West HAC(maxlags=4) 검정
3. 기존 상대지수(d_score_rel) 회귀모형에 공통 분모 변동(d_anchor_score)을 통제변수(공변량)로 추가한 부분 상관(Partial regression with HAC maxlags=4) 검정
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

from util.paths import ROOT
PANEL_PATH = ROOT / "data" / "processed" / "checks" / "search_weekly.csv"
REGIME_DAILY_PATH = ROOT / "data" / "raw" / "datalab" / "datalab_regime_daily.csv"
SUB_DAILY_PATH = ROOT / "data" / "raw" / "datalab" / "datalab_sub_daily.csv"
OUT_CSV = ROOT / "data" / "processed" / "checks" / "anchor_check.csv"

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


def holm_adjust(pvals: np.ndarray) -> np.ndarray:
    n = len(pvals)
    order = np.argsort(pvals)
    sorted_p = pvals[order]
    adj = np.zeros(n, dtype=float)
    running_max = 0.0
    for i, p in enumerate(sorted_p):
        val = min(1.0, p * (n - i))
        running_max = max(running_max, val)
        adj[i] = running_max
    out = np.zeros(n, dtype=float)
    out[order] = adj
    return out


def hac_standardized(x: np.ndarray, y: np.ndarray, maxlags: int = 4) -> tuple[float, float, float]:
    zx = (x - np.mean(x)) / np.std(x, ddof=1)
    zy = (y - np.mean(y)) / np.std(y, ddof=1)
    X = sm.add_constant(zx)
    res = sm.OLS(zy, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return float(res.params[1]), float(res.tvalues[1]), float(res.pvalues[1])


def hac_partial_standardized(x: np.ndarray, y: np.ndarray, z_ctrl: np.ndarray, maxlags: int = 4) -> tuple[float, float, float]:
    zx = (x - np.mean(x)) / np.std(x, ddof=1)
    zy = (y - np.mean(y)) / np.std(y, ddof=1)
    zc = (z_ctrl - np.mean(z_ctrl)) / np.std(z_ctrl, ddof=1)
    X = sm.add_constant(np.column_stack([zx, zc]))
    res = sm.OLS(zy, X).fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return float(res.params[1]), float(res.tvalues[1]), float(res.pvalues[1])


def build_raw_weekly_search() -> pd.DataFrame:
    df_sr = pd.read_csv(REGIME_DAILY_PATH)
    df_sr["date"] = pd.to_datetime(df_sr["date"])
    df_sr["iso_year"] = df_sr["date"].dt.isocalendar().year
    df_sr["iso_week"] = df_sr["date"].dt.isocalendar().week
    df_sr["iso_yw"] = df_sr["iso_year"].astype(str) + "-W" + df_sr["iso_week"].astype(str).str.zfill(2)

    df_ss = pd.read_csv(SUB_DAILY_PATH)
    df_ss["date"] = pd.to_datetime(df_ss["date"])
    df_ss["iso_year"] = df_ss["date"].dt.isocalendar().year
    df_ss["iso_week"] = df_ss["date"].dt.isocalendar().week
    df_ss["iso_yw"] = df_ss["iso_year"].astype(str) + "-W" + df_ss["iso_week"].astype(str).str.zfill(2)

    sr_raw_means = df_sr.groupby(["iso_yw", "group"])["score"].mean().unstack("group")
    ss_raw_means = df_ss.groupby(["iso_yw", "group"])["score"].mean().unstack("group")

    # 기준 앵커('은행') 원시 주간 평균 점수 (금리 그룹 내 anchor_score; 모든 그룹의 anchor_score와 r=1.000000 비례)
    anchor_weekly = (
        df_sr[df_sr["group"] == "금리"]
        .groupby("iso_yw")["anchor_score"]
        .mean()
    )

    raw_comb = pd.DataFrame(index=sr_raw_means.index)
    raw_comb["anchor_score_weekly"] = anchor_weekly
    raw_comb["raw_search_macro_interest"] = sr_raw_means.get("금리", np.nan)
    raw_comb["raw_search_macro_inflation"] = sr_raw_means.get("물가", np.nan)
    raw_comb["raw_search_macro_combined"] = (
        raw_comb["raw_search_macro_interest"] + raw_comb["raw_search_macro_inflation"]
    ) / 2.0
    raw_comb["raw_search_realestate"] = sr_raw_means.get("부동산", np.nan)
    raw_comb["raw_search_aichip"] = sr_raw_means.get("AI반도체", np.nan)
    raw_comb["raw_search_market"] = ss_raw_means.get("국내증시", np.nan)
    raw_comb["raw_search_earnings"] = ss_raw_means.get("기업실적", np.nan)
    raw_comb["raw_search_capital"] = ss_raw_means.get("공모주", np.nan)
    return raw_comb.reset_index()


def main() -> None:
    panel = pd.read_csv(PANEL_PATH)
    raw_w = build_raw_weekly_search()
    df = pd.merge(panel, raw_w, on="iso_yw", how="inner").sort_values("iso_yw").reset_index(drop=True)

    splits = [
        ("Full", np.ones(len(df), dtype=bool)),
        ("Train (2021~2024)", (df["period"] == "train").to_numpy()),
        ("Eval OOS (2025~2026)", (df["period"] == "eval").to_numpy()),
    ]

    rows = []
    for split_name, split_mask in splits:
        # verify_hac_news_search.py 및 run_study_b.py와 100% 동일하게 구간 분리 후 diff() 수행 (경계 누수 방지)
        sub = df[split_mask].reset_index(drop=True)
        d_anc = sub["anchor_score_weekly"].diff().to_numpy()

        for r, s_col, label in PAIRS:
            dx = sub[f"news_share_{r}"].diff().to_numpy()
            dy_rel = sub[s_col].diff().to_numpy()
            dy_raw = sub[f"raw_{s_col}"].diff().to_numpy()

            for h in [-1, 0, 1]:
                if h == 0:
                    x = dx[1:]
                    y_rel = dy_rel[1:]
                    y_raw = dy_raw[1:]
                    anc = d_anc[1:]
                elif h == 1:
                    x = dx[1:-1]
                    y_rel = dy_rel[2:]
                    y_raw = dy_raw[2:]
                    anc = d_anc[2:]
                else:  # h == -1
                    x = dx[2:]
                    y_rel = dy_rel[1:-1]
                    y_raw = dy_raw[1:-1]
                    anc = d_anc[1:-1]

                valid = (~np.isnan(x)) & (~np.isnan(y_rel)) & (~np.isnan(y_raw)) & (~np.isnan(anc))
                xv, y_rel_v, y_raw_v, anc_v = x[valid], y_rel[valid], y_raw[valid], anc[valid]

                r_rel, t_rel, p_rel = hac_standardized(xv, y_rel_v, maxlags=4)
                r_raw, t_raw, p_raw = hac_standardized(xv, y_raw_v, maxlags=4)
                b_part, t_part, p_part = hac_partial_standardized(xv, y_rel_v, anc_v, maxlags=4)
                r_anc, t_anc, p_anc = hac_standardized(xv, anc_v, maxlags=4)

                rows.append({
                    "split": split_name,
                    "pair_label": label,
                    "news_regime": r,
                    "search_col": s_col,
                    "lag_h": h,
                    "n_weeks": int(valid.sum()),
                    "r_score_rel": round(r_rel, 4),
                    "hac_t_rel": round(t_rel, 4),
                    "hac_p_raw_rel": p_rel,
                    "r_raw_score_no_anchor": round(r_raw, 4),
                    "hac_t_raw": round(t_raw, 4),
                    "hac_p_raw_no_anchor": p_raw,
                    "diff_r_rel_minus_raw": round(r_rel - r_raw, 4),
                    "beta_partial_ctrl_anchor": round(b_part, 4),
                    "hac_t_partial": round(t_part, 4),
                    "hac_p_raw_partial": p_part,
                    "r_news_vs_anchor": round(r_anc, 4),
                    "hac_t_news_vs_anchor": round(t_anc, 4),
                    "hac_p_raw_news_vs_anchor": p_anc,
                })

    res_df = pd.DataFrame(rows)
    for split_name in res_df["split"].unique():
        mask = res_df["split"] == split_name
        res_df.loc[mask, "hac_p_holm_rel"] = holm_adjust(res_df.loc[mask, "hac_p_raw_rel"].values)
        res_df.loc[mask, "hac_p_holm_no_anchor"] = holm_adjust(res_df.loc[mask, "hac_p_raw_no_anchor"].values)
        res_df.loc[mask, "hac_p_holm_partial"] = holm_adjust(res_df.loc[mask, "hac_p_raw_partial"].values)

    res_df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved sensitivity results to {OUT_CSV}")

    h0 = res_df[res_df["lag_h"] == 0]
    for split_name in ["Full", "Train (2021~2024)", "Eval OOS (2025~2026)"]:
        print(f"\n=== {split_name} (lag h=0) ===")
        sub = h0[h0["split"] == split_name]
        for _, r in sub.iterrows():
            print(
                f"{r['pair_label']:25s} (N={r['n_weeks']:3d}) | "
                f"rel r={r['r_score_rel']:+.4f} (p_h={r['hac_p_holm_rel']:.4g}) | "
                f"no_anc r={r['r_raw_score_no_anchor']:+.4f} (p_h={r['hac_p_holm_no_anchor']:.4g}) | "
                f"part b={r['beta_partial_ctrl_anchor']:+.4f} (p_h={r['hac_p_holm_partial']:.4g}) | "
                f"r(news,anc)={r['r_news_vs_anchor']:+.4f} (p={r['hac_p_raw_news_vs_anchor']:.3f})"
            )


if __name__ == "__main__":
    main()
