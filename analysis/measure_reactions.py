"""월별 국면 라벨 × 월 패널 → 국면별 지표 반응표·전환 이벤트 스터디.

  python -m analysis.measure_reactions

Step 3의 `regime_monthly.csv`를 `month` 키로 월 패널에 붙이고, 국면별로 코스피·환율·
심리 지표의 변화가 다른지 본다. 연구 질문은 RQ3이다.

세 가지 방식을 나란히 둔다. 하나만으로는 답이 한쪽으로 기울기 때문이다.

  (1) 단일 라벨 그룹 비교 — 그달의 z-우세 국면으로 월을 묶어 평균·분산을 비교한다.
      해석이 쉽지만 공존 이슈를 버린다.
  (2) 비중 벡터 회귀 — 국면 비중을 연속 설명변수로 넣는다. 라벨을 버리지 않아도
      되지만 비중은 합이 1에 가까운 구성 자료라 다중공선성이 있다(VIF를 함께 보고).
  (3) 전환 이벤트 스터디 — PELT가 찾은 전환월 전후 ±3개월 경로. 전환이 4건뿐이라
      검정이 아니라 기술 통계이고, 플라시보 분포에서의 분위로만 강약을 읽는다.

검정은 Kruskal-Wallis를 1순위로 쓴다. 2026년 코스피 분산이 앞 구간의 다섯 배라
(`panel_qc.md` 5절) 정규·등분산을 전제하는 ANOVA는 참고로만 둔다. 등분산 자체가
관심사이므로 Levene도 함께 본다.

`물가`는 z-우세 개월이 0이다. 전량 NMF에서 물가가 금리와 한 축으로 묶여 독립
토픽이 없기 때문이며(`regimes_qc.md` 2절), 여기서 뺀 것이 아니라 라벨이 붙은 달이
없어서 그룹이 만들어지지 않는다. 그룹 수는 데이터가 정한다.

인과는 주장하지 않는다. 뉴스가 지표를 움직였는지, 지표가 뉴스를 불렀는지 이
설계로는 가르지 못한다. 보고하는 것은 국면별 반응 패턴의 차이 여부다.

산출:
  data/processed/reactions/regime_reaction.csv        국면 × 지표 기술통계
  data/processed/reactions/regime_tests.csv           그룹 차이 검정
  data/processed/reactions/pairwise_tests.csv         국면쌍 Mann-Whitney (Holm 보정)
  data/processed/reactions/share_regression.csv       비중 벡터 회귀 (HAC)
  data/processed/reactions/regime_regression.csv      국면 더미 + 통제 회귀 (HAC)
  data/processed/reactions/event_study.csv            전환 ±3개월 경로
  data/processed/reactions/event_study_summary.csv    전환별 누적 변화 + 플라시보 분위
  data/processed/reactions/reactions_qc.md            점검 리포트
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from config import load_config, project_root

ROOT = project_root()
REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
CP_PATH = ROOT / "data" / "processed" / "regimes" / "changepoints.csv"
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
OUT_DIR = ROOT / "data" / "processed" / "reactions"

REACTION_PATH = OUT_DIR / "regime_reaction.csv"
TESTS_PATH = OUT_DIR / "regime_tests.csv"
PAIRWISE_PATH = OUT_DIR / "pairwise_tests.csv"
SHARE_REG_PATH = OUT_DIR / "share_regression.csv"
DUMMY_REG_PATH = OUT_DIR / "regime_regression.csv"
EVENT_PATH = OUT_DIR / "event_study.csv"
EVENT_SUM_PATH = OUT_DIR / "event_study_summary.csv"
QC_PATH = OUT_DIR / "reactions_qc.md"

# 1순위 종속변수. 연구계획서 5.2가 말하는 시장·심리 반응이다.
PRIMARY_DEPS = ["kospi_ret", "usdkrw_ret", "ccsi_diff"]
# 보조: 물가·정책금리는 국면 라벨보다 느리게 움직이므로 참고로만 본다.
SECONDARY_DEPS = ["cpi_mom", "base_rate_diff"]
# 강건성용. 2026년 분산 급증을 직전 12개월 변동성으로 눌러 둔 계열.
ROBUST_DEPS = ["kospi_ret_std"]

ALL_DEPS = PRIMARY_DEPS + SECONDARY_DEPS + ROBUST_DEPS

# 통제 변수. 국면 더미와 같이 넣어 국면 계수가 거시 여건만 반복하는 것이 아닌지 본다.
CONTROLS = ["base_rate_diff", "cpi_mom"]

# 전환 전후 창. config.analysis.event_window_months 기본값과 같다.
EVENT_WINDOW = 3
# HAC(Newey-West) 시차. 월 자료에서 3개월 자기상관까지 흡수한다.
HAC_LAGS = 3
# 그룹 비교에서 이 개월 수 미만인 국면은 검정에 넣지 않는다(추정이 한두 달에 좌우됨).
MIN_GROUP_MONTHS = 5


def load_joined(labels: list[str], slugs: dict[str, str]) -> pd.DataFrame:
    """국면 라벨과 월 패널을 month 로 붙인다. 분석 창(in_study) 안만 남긴다."""
    regimes = pd.read_csv(REGIME_PATH, dtype={"month": str})
    panel = pd.read_csv(PANEL_PATH, dtype={"month": str})
    panel = panel[panel["in_study"]].copy()

    only_regime = set(regimes["month"]) - set(panel["month"])
    only_panel = set(panel["month"]) - set(regimes["month"])
    if only_regime or only_panel:
        raise ValueError(
            f"월 격자 불일치 — 국면에만 {sorted(only_regime)}, 패널에만 {sorted(only_panel)}"
        )

    df = regimes.merge(panel, on="month", how="inner", validate="one_to_one")
    unknown = set(df["dominant_regime"]) - set(labels)
    if unknown:
        raise ValueError(f"config 에 없는 국면 라벨: {sorted(unknown)}")
    missing = [c for c in ALL_DEPS if df[c].isna().any()]
    if missing:
        raise ValueError(f"분석 창 안에서 결측인 종속변수: {missing}")
    return df


def present_regimes(df: pd.DataFrame, labels: list[str]) -> list[str]:
    """라벨이 실제로 붙은 국면만, config 순서로. 0개월 국면은 그룹이 되지 않는다."""
    counts = df["dominant_regime"].value_counts()
    return [r for r in labels if counts.get(r, 0) > 0]


def reaction_table(df: pd.DataFrame, regimes: list[str]) -> pd.DataFrame:
    """국면 × 종속변수 기술통계. 전체 행(regime='전체')을 기준선으로 같이 둔다."""
    rows = []
    for dep in ALL_DEPS:
        overall = df[dep]
        rows.append({
            "dep_var": dep, "regime": "전체", "n": int(overall.size),
            "mean": overall.mean(), "sd": overall.std(ddof=1),
            "median": overall.median(), "min": overall.min(), "max": overall.max(),
            "mean_minus_overall": 0.0,
        })
        for r in regimes:
            s = df.loc[df["dominant_regime"] == r, dep]
            rows.append({
                "dep_var": dep, "regime": r, "n": int(s.size),
                "mean": s.mean(), "sd": s.std(ddof=1),
                "median": s.median(), "min": s.min(), "max": s.max(),
                "mean_minus_overall": s.mean() - overall.mean(),
            })
    return pd.DataFrame(rows)


def epsilon_squared(h: float, n: int, k: int) -> float:
    """Kruskal-Wallis 효과크기. H는 표본이 커지면 자동으로 커지므로 크기를 따로 본다."""
    if n - k <= 0:
        return float("nan")
    return (h - k + 1) / (n - k)


def eta_squared_from_f(f: float, k: int, n: int) -> float:
    num = f * (k - 1)
    den = num + (n - k)
    return num / den if den > 0 else float("nan")


def group_tests(df: pd.DataFrame, regimes: list[str]) -> pd.DataFrame:
    """국면 그룹 간 차이 검정. KW가 1순위, ANOVA는 참고, Levene은 분산 자체의 질문."""
    kept = [r for r in regimes if (df["dominant_regime"] == r).sum() >= MIN_GROUP_MONTHS]
    rows = []
    for dep in ALL_DEPS:
        groups = [df.loc[df["dominant_regime"] == r, dep].to_numpy() for r in kept]
        n = int(sum(g.size for g in groups))
        k = len(groups)
        if k < 2:
            for test, ename in (
                ("kruskal", "epsilon_squared"),
                ("anova", "eta_squared"),
                ("levene_bf", ""),
            ):
                rows.append({
                    "dep_var": dep, "test": test, "k_groups": k, "n": n,
                    "statistic": float("nan"), "p_value": float("nan"),
                    "effect": float("nan"), "effect_name": ename,
                })
            continue

        h, p_kw = stats.kruskal(*groups)
        rows.append({
            "dep_var": dep, "test": "kruskal", "k_groups": k, "n": n,
            "statistic": float(h), "p_value": float(p_kw),
            "effect": epsilon_squared(float(h), n, k), "effect_name": "epsilon_squared",
        })

        f, p_a = stats.f_oneway(*groups)
        rows.append({
            "dep_var": dep, "test": "anova", "k_groups": k, "n": n,
            "statistic": float(f), "p_value": float(p_a),
            "effect": eta_squared_from_f(float(f), k, n), "effect_name": "eta_squared",
        })

        # center='median' (Brown-Forsythe). 꼬리가 두꺼운 수익률에서 mean 기준보다 안전하다.
        w, p_l = stats.levene(*groups, center="median")
        rows.append({
            "dep_var": dep, "test": "levene_bf", "k_groups": k, "n": n,
            "statistic": float(w), "p_value": float(p_l),
            "effect": float("nan"), "effect_name": "",
        })
    return pd.DataFrame(rows)


def pairwise_tests(df: pd.DataFrame, regimes: list[str]) -> pd.DataFrame:
    """국면쌍 Mann-Whitney. 쌍이 15개라 Holm으로 보정하지 않으면 우연이 섞인다."""
    from statsmodels.stats.multitest import multipletests

    kept = [r for r in regimes if (df["dominant_regime"] == r).sum() >= MIN_GROUP_MONTHS]
    rows = []
    for dep in PRIMARY_DEPS + ROBUST_DEPS:
        raw = []
        for i, a in enumerate(kept):
            for b in kept[i + 1:]:
                sa = df.loc[df["dominant_regime"] == a, dep].to_numpy()
                sb = df.loc[df["dominant_regime"] == b, dep].to_numpy()
                u, p = stats.mannwhitneyu(sa, sb, alternative="two-sided")
                # rank-biserial: U를 [-1,1] 효과크기로. 0이면 두 분포가 겹친다.
                rbc = 2 * u / (sa.size * sb.size) - 1
                raw.append({
                    "dep_var": dep, "a": a, "b": b, "n_a": sa.size, "n_b": sb.size,
                    "mean_a": sa.mean(), "mean_b": sb.mean(),
                    "u": float(u), "p_raw": float(p), "rank_biserial": float(rbc),
                })
        if not raw:
            continue
        block = pd.DataFrame(raw)
        block["p_holm"] = multipletests(block["p_raw"], method="holm")[1]
        rows.append(block)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _hac_ols(y: pd.Series, X: pd.DataFrame) -> pd.DataFrame:
    """OLS + Newey-West. 월 자료의 잔차 자기상관·이분산을 표준오차에서 흡수한다."""
    import statsmodels.api as sm

    Xc = sm.add_constant(X, has_constant="add")
    model = sm.OLS(y.to_numpy(), Xc.to_numpy()).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS}
    )
    out = pd.DataFrame({
        "term": ["const"] + list(X.columns),
        "coef": model.params,
        "se_hac": model.bse,
        "t": model.tvalues,
        "p_value": model.pvalues,
    })
    out.attrs["r2"] = float(model.rsquared)
    out.attrs["r2_adj"] = float(model.rsquared_adj)
    out.attrs["nobs"] = int(model.nobs)
    out.attrs["f_pvalue"] = float(model.f_pvalue)
    return out


def _vif(X: pd.DataFrame) -> pd.Series:
    """구성 자료(비중 합≈1)를 설명변수로 쓰면 공선성이 생긴다. 숨기지 않고 보고한다."""
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    import statsmodels.api as sm

    Xc = sm.add_constant(X, has_constant="add")
    arr = Xc.to_numpy(dtype=float)
    return pd.Series(
        [variance_inflation_factor(arr, i) for i in range(1, arr.shape[1])],
        index=X.columns,
    )


def share_regression(df: pd.DataFrame, share_cols: list[str]) -> pd.DataFrame:
    """단일 라벨이 버리는 공존 이슈를 살리는 쪽. 비중을 z점수로 넣어 계수를 비교 가능하게."""
    Z = df[share_cols].apply(lambda s: (s - s.mean()) / s.std(ddof=1))
    vif = _vif(Z)
    blocks = []
    for dep in PRIMARY_DEPS + ROBUST_DEPS:
        res = _hac_ols(df[dep], Z)
        res.insert(0, "dep_var", dep)
        res["vif"] = res["term"].map(vif)
        res["r2"] = res.attrs["r2"]
        res["r2_adj"] = res.attrs["r2_adj"]
        res["nobs"] = res.attrs["nobs"]
        res["f_pvalue"] = res.attrs["f_pvalue"]
        blocks.append(res)
    return pd.concat(blocks, ignore_index=True)


def dummy_regression(
    df: pd.DataFrame, regimes: list[str], base: str
) -> pd.DataFrame:
    """국면 더미 + 통제. 계수는 기준 국면과의 차이다. n=67이라 포화 설계는 쓰지 않는다."""
    dummies = pd.get_dummies(df["dominant_regime"], prefix="rg", dtype=float)
    drop_col = f"rg_{base}"
    if drop_col not in dummies.columns:
        raise ValueError(f"기준 국면 더미가 없다: {drop_col}")
    dummies = dummies.drop(columns=[drop_col])

    blocks = []
    for dep in PRIMARY_DEPS + ROBUST_DEPS:
        # 종속변수가 통제변수에 들어가면 자기 자신을 설명하게 되므로 뺀다.
        controls = [c for c in CONTROLS if c != dep]
        X = pd.concat([dummies, df[controls]], axis=1)
        res = _hac_ols(df[dep], X)
        res.insert(0, "dep_var", dep)
        res["base_regime"] = base
        res["r2"] = res.attrs["r2"]
        res["r2_adj"] = res.attrs["r2_adj"]
        res["nobs"] = res.attrs["nobs"]
        res["f_pvalue"] = res.attrs["f_pvalue"]
        blocks.append(res)
    return pd.concat(blocks, ignore_index=True)


def event_paths(df: pd.DataFrame, cps: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """전환월 t 기준 t-3..t+3 경로와 누적 변화. 창이 잘리는 전환은 제외한다."""
    idx = {m: i for i, m in enumerate(df["month"])}
    offsets = list(range(-EVENT_WINDOW, EVENT_WINDOW + 1))

    rows, summary = [], []
    for _, cp in cps.iterrows():
        cm = str(cp["cp_month"])
        if cm not in idx:
            continue
        c = idx[cm]
        if c - EVENT_WINDOW < 0 or c + EVENT_WINDOW >= len(df):
            continue
        for dep in PRIMARY_DEPS + ROBUST_DEPS:
            vals = {o: float(df.loc[c + o, dep]) for o in offsets}
            cum = 0.0
            for o in offsets:
                cum += vals[o]
                rows.append({
                    "signal": cp["signal"], "cp_month": cm,
                    "from_label": cp["from_label"], "to_label": cp["to_label"],
                    "dep_var": dep, "offset": o,
                    "month": df.loc[c + o, "month"], "value": vals[o], "cum": cum,
                })
            pre = sum(vals[o] for o in offsets if o < 0)
            post = sum(vals[o] for o in offsets if o > 0)
            summary.append({
                "signal": cp["signal"], "cp_month": cm,
                "from_label": cp["from_label"], "to_label": cp["to_label"],
                "dep_var": dep, "pre_sum": pre, "at": vals[0], "post_sum": post,
                "post_minus_pre": post - pre,
            })
    return pd.DataFrame(rows), pd.DataFrame(summary)


def placebo_percentile(df: pd.DataFrame, summary: pd.DataFrame, cps: pd.DataFrame) -> pd.DataFrame:
    """전환이 아닌 모든 달로 같은 통계를 만들어, 실제 전환이 그 분포의 어디인지 본다.

    전환이 4건뿐이라 검정은 못 한다. 다만 '전환월의 변화가 아무 달과 다르지 않다'는
    반대 주장은 이 분위로 반박하거나 수긍할 수 있다.
    """
    if summary.empty:
        return summary
    cp_months = set(cps["cp_month"].astype(str))
    offsets = list(range(-EVENT_WINDOW, EVENT_WINDOW + 1))

    out = summary.copy()
    pct, n_pl = [], []
    for _, row in summary.iterrows():
        dep = row["dep_var"]
        draws = []
        for c in range(EVENT_WINDOW, len(df) - EVENT_WINDOW):
            if df.loc[c, "month"] in cp_months:
                continue
            vals = {o: float(df.loc[c + o, dep]) for o in offsets}
            pre = sum(vals[o] for o in offsets if o < 0)
            post = sum(vals[o] for o in offsets if o > 0)
            draws.append(abs(post - pre))
        arr = np.asarray(draws)
        pct.append(float((arr <= abs(row["post_minus_pre"])).mean()))
        n_pl.append(int(arr.size))
    out["placebo_pctile_abs"] = pct
    out["placebo_n"] = n_pl
    return out


def write_qc(
    *,
    df: pd.DataFrame,
    regimes: list[str],
    absent: list[str],
    reaction: pd.DataFrame,
    tests: pd.DataFrame,
    pairwise: pd.DataFrame,
    share_reg: pd.DataFrame,
    dummy_reg: pd.DataFrame,
    events: pd.DataFrame,
    esum: pd.DataFrame,
    base: str,
    share_cols: list[str],
) -> None:
    lines: list[str] = []
    add = lines.append

    add("# 국면별 반응 분석 점검")
    add("")
    add(f"생성: `analysis.measure_reactions` · {pd.Timestamp.now():%Y-%m-%d %H:%M}")
    add("")

    add("## 1. 표본")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 기간 | {df['month'].iloc[0]} ~ {df['month'].iloc[-1]} ({len(df)}개월) |")
    add(f"| 국면 그룹 | {len(regimes)}개 — {', '.join(regimes)} |")
    add(f"| 라벨 0개월 | {', '.join(absent) if absent else '없음'} |")
    add(f"| 종속변수 | 주 {len(PRIMARY_DEPS)} · 보조 {len(SECONDARY_DEPS)} · 강건성 {len(ROBUST_DEPS)} |")
    add(f"| 결측 | {int(df[ALL_DEPS].isna().sum().sum())} |")
    add("")
    add("| 국면 | 개월 | 월 목록 |")
    add("|------|------|---------|")
    for r in regimes:
        ms = df.loc[df["dominant_regime"] == r, "month"].tolist()
        add(f"| {r} | {len(ms)} | {', '.join(ms)} |")
    add("")
    if absent:
        add(f"`{', '.join(absent)}`는 z-우세 개월이 0이라 그룹이 만들어지지 않는다. "
            "전량 NMF에서 물가 어휘가 금리·연준과 한 토픽에 묶여 독립 축이 없기 때문이다"
            "(`regimes_qc.md` 2절). 분석에서 뺀 것이 아니라 라벨이 붙은 달이 없다.")
        add("")
    runs = int((df["dominant_regime"] != df["dominant_regime"].shift()).sum())
    add(f"라벨은 {len(df)}개월 동안 {runs}개 구간으로 갈린다(최장 연속 "
        f"{int(df.groupby((df['dominant_regime'] != df['dominant_regime'].shift()).cumsum()).size().max())}개월). "
        "국면이 긴 블록으로 뭉쳐 있지 않으므로, 그룹 비교는 시간 구간 비교가 아니라 "
        "'그 이슈가 상대적으로 올라온 달'의 비교로 읽어야 한다.")
    add("")

    add("## 2. 국면별 반응 (주 종속변수)")
    add("")
    for dep in PRIMARY_DEPS:
        sub = reaction[reaction["dep_var"] == dep]
        add(f"### `{dep}`")
        add("")
        add("| 국면 | n | 평균 | 표준편차 | 중위수 | 최소 | 최대 | 전체평균 차 |")
        add("|------|---|------|----------|--------|------|------|-------------|")
        for _, r in sub.iterrows():
            add(f"| {r['regime']} | {int(r['n'])} | {r['mean']:+.3f} | {r['sd']:.3f} | "
                f"{r['median']:+.3f} | {r['min']:+.3f} | {r['max']:+.3f} | "
                f"{r['mean_minus_overall']:+.3f} |")
        add("")

    add("## 3. 그룹 차이 검정")
    add("")
    add("Kruskal-Wallis가 1순위다. 2026년 코스피 분산이 앞 구간의 다섯 배라 정규·등분산을")
    add("전제하는 ANOVA는 액면대로 읽을 수 없다. Levene(Brown-Forsythe)은 '국면별로 변동성이")
    add(f"다른가'라는 별개의 질문이다. 개월 {MIN_GROUP_MONTHS} 미만 국면은 검정에서 뺀다(해당 없음이면 전부 포함).")
    add("")
    add("| 종속변수 | 검정 | k | n | 통계량 | p | 효과크기 |")
    add("|----------|------|---|---|--------|---|----------|")
    for _, r in tests.iterrows():
        eff = "—" if pd.isna(r["effect"]) else f"{r['effect']:+.3f} ({r['effect_name']})"
        add(f"| `{r['dep_var']}` | {r['test']} | {int(r['k_groups'])} | {int(r['n'])} | "
            f"{r['statistic']:.3f} | {r['p_value']:.4f} | {eff} |")
    add("")
    sig = tests[(tests["test"] == "kruskal") & (tests["p_value"] < 0.05)]["dep_var"].tolist()
    add(f"KW p<0.05: {', '.join(f'`{d}`' for d in sig) if sig else '없음'}")
    add("")

    if not pairwise.empty:
        add("## 4. 국면쌍 비교 (Mann-Whitney, Holm 보정)")
        add("")
        add("쌍이 많아 보정 없이 읽으면 우연이 섞인다. Holm 보정 후 p<0.05만 적는다.")
        add("전체 쌍은 `pairwise_tests.csv`에 있다.")
        add("")
        hit = pairwise[pairwise["p_holm"] < 0.05]
        if hit.empty:
            add("Holm 보정 후 p<0.05인 쌍: 없음.")
        else:
            add("| 종속변수 | 국면 A | 국면 B | 평균 A | 평균 B | p(raw) | p(Holm) | rank-biserial |")
            add("|----------|--------|--------|--------|--------|--------|---------|---------------|")
            for _, r in hit.iterrows():
                add(f"| `{r['dep_var']}` | {r['a']} | {r['b']} | {r['mean_a']:+.3f} | "
                    f"{r['mean_b']:+.3f} | {r['p_raw']:.4f} | {r['p_holm']:.4f} | "
                    f"{r['rank_biserial']:+.3f} |")
        add("")

    add("## 5. 비중 벡터 회귀 (HAC)")
    add("")
    add("단일 라벨은 그달의 1위 축만 남긴다. 비중을 z점수로 넣으면 공존 이슈가 살아 있다.")
    add(f"대신 비중은 합이 1에 가까운 구성 자료라 공선성이 생긴다. VIF를 같이 적는다.")
    add(f"표준오차는 Newey-West(maxlags={HAC_LAGS}).")
    add("")
    add("| 종속변수 | 항 | 계수 | HAC SE | t | p | VIF |")
    add("|----------|-----|------|--------|---|---|-----|")
    for _, r in share_reg.iterrows():
        vif = "—" if pd.isna(r["vif"]) else f"{r['vif']:.1f}"
        add(f"| `{r['dep_var']}` | {r['term']} | {r['coef']:+.3f} | {r['se_hac']:.3f} | "
            f"{r['t']:+.2f} | {r['p_value']:.4f} | {vif} |")
    add("")
    fit = share_reg.groupby("dep_var", sort=False)[["r2", "r2_adj", "nobs", "f_pvalue"]].first()
    add("| 종속변수 | R² | 수정 R² | n | F p |")
    add("|----------|----|---------|---|-----|")
    for dep, r in fit.iterrows():
        add(f"| `{dep}` | {r['r2']:.3f} | {r['r2_adj']:.3f} | {int(r['nobs'])} | {r['f_pvalue']:.4f} |")
    add("")

    add("## 6. 국면 더미 + 통제 회귀 (HAC)")
    add("")
    add(f"기준 국면은 `{base}`(개월 수 최다)다. 계수는 기준과의 차이다. 통제는 "
        f"{', '.join(f'`{c}`' for c in CONTROLS)}이고, 종속변수와 같은 열은 그 회귀에서 뺀다.")
    add(f"관측치 {len(df)}개월에 더미 {len(regimes) - 1}개 + 통제라 포화 설계는 쓰지 않는다.")
    add("")
    add("| 종속변수 | 항 | 계수 | HAC SE | t | p |")
    add("|----------|-----|------|--------|---|---|")
    for _, r in dummy_reg.iterrows():
        add(f"| `{r['dep_var']}` | {r['term']} | {r['coef']:+.3f} | {r['se_hac']:.3f} | "
            f"{r['t']:+.2f} | {r['p_value']:.4f} |")
    add("")
    fit2 = dummy_reg.groupby("dep_var", sort=False)[["r2", "r2_adj", "nobs", "f_pvalue"]].first()
    add("| 종속변수 | R² | 수정 R² | n | F p |")
    add("|----------|----|---------|---|-----|")
    for dep, r in fit2.iterrows():
        add(f"| `{dep}` | {r['r2']:.3f} | {r['r2_adj']:.3f} | {int(r['nobs'])} | {r['f_pvalue']:.4f} |")
    add("")

    add("## 7. 전환 이벤트 스터디")
    add("")
    if esum.empty:
        add("창(±3개월)이 확보되는 전환이 없다.")
        add("")
    else:
        add(f"전환월 t 기준 t-{EVENT_WINDOW}..t+{EVENT_WINDOW}. 전환이 "
            f"{esum['cp_month'].nunique()}건뿐이라 검정이 아니라 기술 통계다.")
        add("`placebo_pctile_abs`는 전환이 아닌 모든 달로 같은 |사후-사전| 통계를 만들어")
        add("실제 전환이 그 분포의 어느 분위인지 본 값이다. 1에 가까우면 아무 달보다 크다.")
        add("")
        add("| 신호 | 전환월 | 이전→이후 | 종속변수 | 사전합 | 당월 | 사후합 | 사후-사전 | 플라시보 분위 |")
        add("|------|--------|-----------|----------|--------|------|--------|-----------|---------------|")
        for _, r in esum.iterrows():
            add(f"| {r['signal']} | {r['cp_month']} | {r['from_label']}→{r['to_label']} | "
                f"`{r['dep_var']}` | {r['pre_sum']:+.2f} | {r['at']:+.2f} | {r['post_sum']:+.2f} | "
                f"{r['post_minus_pre']:+.2f} | {r['placebo_pctile_abs']:.2f} |")
        add("")
        strong = esum[esum["placebo_pctile_abs"] >= 0.9]
        add(f"플라시보 분위 0.90 이상: {len(strong)} / {len(esum)}건"
            + ("" if strong.empty else " — "
               + ", ".join(f"{r['cp_month']} `{r['dep_var']}`" for _, r in strong.iterrows())))
        add("")

    add("## 8. 잔차 자기상관")
    add("")
    add("그룹 비교는 관측치 독립을 전제한다. 월 수익률이 자기상관을 가지면 p가 낙관적으로")
    add("나온다. 종속변수 자체의 Ljung-Box(시차 3)를 확인한다.")
    add("")
    try:
        from statsmodels.stats.diagnostic import acorr_ljungbox

        add("| 종속변수 | LB(3) 통계량 | p |")
        add("|----------|--------------|---|")
        for dep in ALL_DEPS:
            lb = acorr_ljungbox(df[dep], lags=[3], return_df=True)
            add(f"| `{dep}` | {lb['lb_stat'].iloc[0]:.3f} | {lb['lb_pvalue'].iloc[0]:.4f} |")
        add("")
    except ImportError:
        add("statsmodels 미설치 — 건너뜀.")
        add("")

    add("## 9. 주장 범위")
    add("")
    add("- 인과를 주장하지 않는다. 국면과 지표의 동시 움직임이 국면별로 다른지만 본다.")
    add("- 코퍼스가 경제지 3곳이라 결과는 경제지 기준 이슈 국면의 반응이다.")
    add("- 전환 4건은 표본이 아니다. 이벤트 스터디는 사례 기술로만 읽는다.")
    add(f"- `{', '.join(absent)}`는 라벨 0개월이라 비교에 등장하지 않는다."
        if absent else "- 라벨 0개월 국면은 없다.")
    add("")

    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def join_regime_panel(regime_path: Path, labels: list[str]) -> pd.DataFrame:
    """임의의 국면 시계열을 월 패널에 붙인다. 폴백 LDA 산출에도 쓴다."""
    regimes = pd.read_csv(regime_path, dtype={"month": str})
    panel = pd.read_csv(PANEL_PATH, dtype={"month": str})
    panel = panel[panel["in_study"]].copy()
    only_regime = set(regimes["month"]) - set(panel["month"])
    only_panel = set(panel["month"]) - set(regimes["month"])
    if only_regime or only_panel:
        raise ValueError(
            f"월 격자 불일치 — 국면에만 {sorted(only_regime)}, 패널에만 {sorted(only_panel)}"
        )
    df = regimes.merge(panel, on="month", how="inner", validate="one_to_one")
    unknown = set(df["dominant_regime"]) - set(labels)
    if unknown:
        raise ValueError(f"config 에 없는 국면 라벨: {sorted(unknown)}")
    missing = [c for c in ALL_DEPS if df[c].isna().any()]
    if missing:
        raise ValueError(f"분석 창 안에서 결측인 종속변수: {missing}")
    return df


def analyze(
    df: pd.DataFrame,
    cps: pd.DataFrame,
    labels: list[str],
    slugs: dict[str, str],
    dest: Path,
    qc_title: str = "국면별 반응 분석 점검",
) -> dict:
    """조인된 패널에서 반응표·검정·회귀·이벤트를 dest 에 쓴다."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    regimes = present_regimes(df, labels)
    absent = [r for r in labels if r not in regimes]
    print(f"표본 {len(df)}개월 · 국면 그룹 {len(regimes)}개 "
          f"({', '.join(regimes)})" + (f" · 라벨 0개월 {absent}" if absent else ""))

    share_cols = [f"share_{slugs[r]}" for r in regimes]
    zero_var = [c for c in share_cols if df[c].std(ddof=1) == 0]
    if zero_var:
        share_cols = [c for c in share_cols if c not in zero_var]
        print(f"  분산 0 비중 열 제외: {zero_var}", flush=True)

    reaction = reaction_table(df, regimes)
    tests = group_tests(df, regimes)
    pairwise = pairwise_tests(df, regimes)
    share_reg = share_regression(df, share_cols)
    base = df["dominant_regime"].value_counts().idxmax()
    dummy_reg = dummy_regression(df, regimes, base)
    events, esum = event_paths(df, cps)
    esum = placebo_percentile(df, esum, cps)

    paths = {
        "reaction": dest / "regime_reaction.csv",
        "tests": dest / "regime_tests.csv",
        "pairwise": dest / "pairwise_tests.csv",
        "share_reg": dest / "share_regression.csv",
        "dummy_reg": dest / "regime_regression.csv",
        "events": dest / "event_study.csv",
        "esum": dest / "event_study_summary.csv",
        "qc": dest / "reactions_qc.md",
    }
    reaction.to_csv(paths["reaction"], index=False, encoding="utf-8-sig")
    tests.to_csv(paths["tests"], index=False, encoding="utf-8-sig")
    pairwise.to_csv(paths["pairwise"], index=False, encoding="utf-8-sig")
    share_reg.to_csv(paths["share_reg"], index=False, encoding="utf-8-sig")
    dummy_reg.to_csv(paths["dummy_reg"], index=False, encoding="utf-8-sig")
    events.to_csv(paths["events"], index=False, encoding="utf-8-sig")
    esum.to_csv(paths["esum"], index=False, encoding="utf-8-sig")

    orig_qc = QC_PATH
    try:
        globals()["QC_PATH"] = paths["qc"]
        write_qc(
            df=df, regimes=regimes, absent=absent, reaction=reaction, tests=tests,
            pairwise=pairwise, share_reg=share_reg, dummy_reg=dummy_reg,
            events=events, esum=esum, base=base, share_cols=share_cols,
        )
    finally:
        globals()["QC_PATH"] = orig_qc
    if qc_title != "국면별 반응 분석 점검":
        text = paths["qc"].read_text(encoding="utf-8")
        paths["qc"].write_text(
            text.replace("# 국면별 반응 분석 점검", f"# {qc_title}", 1),
            encoding="utf-8",
        )

    print("\n=== KW 검정 (국면 그룹 차이) ===")
    kw = tests[tests["test"] == "kruskal"]
    for _, r in kw.iterrows():
        print(f"  {r['dep_var']:<14} H={r['statistic']:7.3f}  p={r['p_value']:.4f}  "
              f"eps2={r['effect']:+.3f}")
    if not pairwise.empty:
        print(f"\nHolm 보정 후 p<0.05 쌍: {int((pairwise['p_holm'] < 0.05).sum())} / {len(pairwise)}")
    if not esum.empty:
        print(f"이벤트 {esum['cp_month'].nunique()}건 · 플라시보 분위 0.9+ "
              f"{int((esum['placebo_pctile_abs'] >= 0.9).sum())} / {len(esum)}")
    print(f"\n반응표   → {paths['reaction']}")
    print(f"검정     → {paths['tests']}")
    print(f"QC       → {paths['qc']}")
    return {
        "df": df, "regimes": regimes, "absent": absent, "reaction": reaction,
        "tests": tests, "pairwise": pairwise, "share_reg": share_reg,
        "dummy_reg": dummy_reg, "events": events, "esum": esum,
        "base": base, "paths": paths,
    }


def main() -> None:
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_joined(labels, slugs)
    cps = pd.read_csv(CP_PATH, dtype={"cp_month": str})
    analyze(df, cps, labels, slugs, OUT_DIR)


if __name__ == "__main__":
    main()
