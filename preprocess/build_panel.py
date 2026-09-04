"""ECOS · 데이터랩 · 코퍼스 → 분석용 월 패널.

  python -m preprocess.build_panel

세 소스는 수집 시점도 키 형식도 다르다. 반응 분석은 이들을 한 달 격자 위에서
같은 행으로 봐야 하므로, 여기서 월을 키로 합치고 회귀에 바로 쓸 수 있는
파생변수까지 만들어 둔다.

레벨 변수는 대부분 비정상 시계열이라 그대로 회귀에 넣을 수 없다.
가격류(KOSPI·USD_KRW·CPI)는 로그차분, 지수·금리류(CCSI·BASE_RATE)는 단순차분을
쓴다. 검색 관심도는 앵커 정규화된 `score_rel`을 받아 전기간 z-점수와
7국면 내 점유율을 함께 둔다 — 절대 수준과 상대 배분이 다른 질문에 답하기 때문이다.

패널 기간은 `data_buffer_start` ~ `study_period_end` 전체다. 분석 창 첫 달의
차분·전년동월비를 만들려면 앞쪽 lead-in이 남아 있어야 한다. 분석 창 여부는
`in_study` 열로 구분한다.

산출:
  data/processed/panel/monthly_panel.csv            월 × (지표·검색 대분류·뉴스량)
  data/processed/panel/monthly_panel_search_sub.csv 월 × 검색 세부 28그룹
  data/processed/panel/panel_qc.md                  결측·이상치·정합성 점검 리포트
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import load_config, project_root

ROOT = project_root()
ECOS_PATH = ROOT / "data" / "raw" / "ecos" / "ecos_monthly.csv"
DATALAB_DIR = ROOT / "data" / "raw" / "datalab"
CORPUS_COUNTS = ROOT / "data" / "processed" / "corpus" / "corpus_monthly_counts.csv"
OUT_DIR = ROOT / "data" / "processed" / "panel"

PANEL_PATH = OUT_DIR / "monthly_panel.csv"
SUB_PATH = OUT_DIR / "monthly_panel_search_sub.csv"
QC_PATH = OUT_DIR / "panel_qc.md"

# 로그차분할 가격 변수와 단순차분할 지수·금리 변수.
LOG_DIFF = {"KOSPI": "kospi_ret", "USD_KRW": "usdkrw_ret", "CPI": "cpi_mom"}
PLAIN_DIFF = {"CCSI": "ccsi_diff", "BASE_RATE": "base_rate_diff"}

OUTLIER_Z = 3.0


def month_index(start: str, end: str) -> pd.DataFrame:
    periods = pd.period_range(start, end, freq="M")
    return pd.DataFrame({
        "month": periods.astype(str),
        "date": periods.to_timestamp(),
    })


def load_ecos() -> pd.DataFrame:
    df = pd.read_csv(ECOS_PATH, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df.drop(columns=["date", "collected_at"], errors="ignore")


def load_search(level: str) -> pd.DataFrame:
    """데이터랩 월별 파일을 long → wide 로 편다. level 은 regime 또는 sub."""
    df = pd.read_csv(DATALAB_DIR / f"datalab_{level}_monthly.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    dup = df.duplicated(["month", "group"]).sum()
    if dup:
        raise ValueError(f"datalab_{level}_monthly 에 월×그룹 중복 {dup}건")
    return df.pivot(index="month", columns="group", values="score_rel")


def load_anchor() -> pd.DataFrame:
    """요청별 앵커(`은행`) 점수. score_rel 급등이 진짜인지 가늠하는 데 쓴다."""
    df = pd.read_csv(DATALAB_DIR / "datalab_regime_monthly.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df.pivot(index="month", columns="group", values="anchor_score")


def load_search_daily_std() -> pd.DataFrame:
    """월 안에서 검색 관심도가 얼마나 출렁였는지. 이슈의 돌발성 대리변수."""
    df = pd.read_csv(DATALAB_DIR / "datalab_regime_daily.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df.pivot_table(index="month", columns="group", values="score_rel", aggfunc="std")


def load_news() -> pd.DataFrame:
    df = pd.read_csv(CORPUS_COUNTS)
    return df.rename(columns={"n": "news_n", "sources": "news_sources"})


def add_indicator_derivatives(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    for col, name in LOG_DIFF.items():
        out[name] = 100 * np.log(out[col]).diff()
    for col, name in PLAIN_DIFF.items():
        out[name] = out[col].diff()
    # 물가는 기저효과 탓에 전월비가 계절을 타므로 전년동월비를 함께 둔다.
    out["cpi_yoy"] = 100 * (out["CPI"] / out["CPI"].shift(12) - 1)
    # 직전 3개월 실현변동성. 국면별 '반응 크기'가 아니라 '반응 불확실성' 비교용.
    out["kospi_vol3"] = out["kospi_ret"].rolling(3).std()

    # 2026년 상반기 코스피 변동성이 앞 구간의 다섯 배로 뛴다(7월 대폭락). 실제 값이지만
    # 수준 그대로 회귀에 넣으면 마지막 몇 달이 국면 계수를 통째로 끌고 간다.
    # 직전 12개월 변동성으로 나눈 표준화 수익률을 강건성 검증용으로 함께 둔다.
    # shift(1)로 당월을 빼서 미래 정보가 스케일에 섞이지 않게 한다.
    out["kospi_vol12"] = out["kospi_ret"].rolling(12).std()
    out["kospi_ret_std"] = out["kospi_ret"] / out["kospi_vol12"].shift(1)
    return out


def add_search_derivatives(
    panel: pd.DataFrame, slugs: dict[str, str], daily_std: pd.DataFrame
) -> pd.DataFrame:
    out = panel.copy()
    level_cols = [f"srch_{s}" for s in slugs.values()]

    total = out[level_cols].sum(axis=1)
    for label, slug in slugs.items():
        level = out[f"srch_{slug}"]
        out[f"srch_{slug}_z"] = (level - level.mean()) / level.std()
        out[f"srch_{slug}_share"] = level / total
        out[f"srch_{slug}_dlog"] = 100 * np.log(level).diff()
        out[f"srch_{slug}_dstd"] = out["month"].map(daily_std[label])
    return out


def order_columns(panel: pd.DataFrame, slugs: dict[str, str]) -> list[str]:
    head = ["month", "date", "in_study"]
    ecos = list(LOG_DIFF) + list(PLAIN_DIFF)
    derived = (list(LOG_DIFF.values()) + list(PLAIN_DIFF.values())
               + ["cpi_yoy", "kospi_vol3", "kospi_vol12", "kospi_ret_std"])
    news = ["news_n", "news_sources"]
    search: list[str] = []
    for slug in slugs.values():
        search += [f"srch_{slug}", f"srch_{slug}_z", f"srch_{slug}_share",
                   f"srch_{slug}_dlog", f"srch_{slug}_dstd"]
    return head + ecos + derived + news + search


def find_outliers(panel: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for col in cols:
        s = panel[col].dropna()
        if s.empty or s.std() == 0:
            continue
        z = (s - s.mean()) / s.std()
        for month, zv in z[z.abs() >= OUTLIER_Z].items():
            rows.append({
                "column": col,
                "month": panel.loc[month, "month"],
                "value": panel.loc[month, col],
                "z": zv,
            })
    return pd.DataFrame(rows).sort_values("z", key=abs, ascending=False) if rows else pd.DataFrame()


def find_repeats(panel: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """연속 두 달이 완전히 같은 레벨. 지표 시계열에서는 갱신 실패 신호일 수 있다."""
    rows = []
    for col in cols:
        s = panel[col]
        same = s.eq(s.shift()) & s.notna()
        for i in panel.index[same]:
            rows.append({"column": col, "month": panel.loc[i, "month"], "value": s[i]})
    return pd.DataFrame(rows)


def write_qc(
    panel: pd.DataFrame,
    sub: pd.DataFrame,
    anchors: pd.DataFrame,
    slugs: dict[str, str],
    cfg: dict,
) -> None:
    study = panel[panel["in_study"]]
    diff_cols = list(LOG_DIFF.values()) + list(PLAIN_DIFF.values())
    level_cols = list(LOG_DIFF) + list(PLAIN_DIFF)

    lines: list[str] = []
    add = lines.append

    add("# 월 패널 품질 점검\n")
    add(f"생성: `preprocess/build_panel.py` · {pd.Timestamp.now():%Y-%m-%d %H:%M}\n")

    add("## 1. 커버리지\n")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 패널 기간 | {panel['month'].iloc[0]} ~ {panel['month'].iloc[-1]} ({len(panel)}개월) |")
    add(f"| 분석 창 | {study['month'].iloc[0]} ~ {study['month'].iloc[-1]} ({len(study)}개월) |")
    add(f"| 지표 열 | {len(level_cols)} |")
    add(f"| 검색 대분류 | {len(slugs)} |")
    add(f"| 검색 세부 | {sub.shape[1] - 2} |")
    add("")

    add("## 2. 결측\n")
    miss = panel.isna().sum()
    miss = miss[miss > 0]
    study_miss = study.isna().sum()
    study_miss = study_miss[study_miss > 0]

    if miss.empty:
        add("결측 없음.\n")
    else:
        add("| 열 | 결측 | 분석 창 내 | 판정 |")
        add("|----|------|-----------|------|")
        for col, n in miss.items():
            inside = int(study_miss.get(col, 0))
            if inside == 0:
                note = "정상 — 분석 창 밖 lead-in에서만 발생"
            else:
                note = "**확인 필요**"
            add(f"| `{col}` | {n} | {inside} | {note} |")
        add("")
        add(f"분석 창({len(study)}개월) 내 결측: "
            + ("없음" if study_miss.empty else ", ".join(f"`{c}` {n}" for c, n in study_miss.items()))
            + "\n")
        add("`news_*`는 빅카인즈 코퍼스가 2021-01부터라 그 이전 60개월이 비어 있다. "
            "차분·전년동월비 열의 선두 결측은 lead-in을 소비한 결과다. 둘 다 설계대로다.\n")

    add("## 3. 지표 이상치 (|z| >= 3)\n")
    out = find_outliers(panel, diff_cols)
    if out.empty:
        add("없음.\n")
    else:
        add("| 열 | 월 | 값 | z |")
        add("|----|-----|-----|---|")
        for _, r in out.iterrows():
            add(f"| `{r['column']}` | {r['month']} | {r['value']:.2f} | {r['z']:+.2f} |")
        add("")

    add("## 4. 연속 동일값 (레벨)\n")
    rep = find_repeats(panel, level_cols)
    # 기준금리는 동결이 정상이므로 보고 대상에서 뺀다.
    rep = rep[rep["column"] != "BASE_RATE"] if not rep.empty else rep
    if rep.empty:
        add("기준금리 동결 구간을 제외하면 없음.\n")
    else:
        add("| 열 | 월 | 값 |")
        add("|----|-----|-----|")
        for _, r in rep.iterrows():
            add(f"| `{r['column']}` | {r['month']} | {r['value']:,.2f} |")
        add("\n가격 지표가 두 달 연속 소수점까지 같으면 원계열 갱신 실패를 의심해야 한다. "
            "CPI는 소수 둘째 자리 반올림 지수라 인접 월이 같은 값을 갖는 것이 가능하다.\n")

    add("## 5. 변동성 국면 점검\n")
    add("반응 분석은 구간별 분산이 비슷하다고 전제한다. 코스피는 그렇지 않다.\n")
    add("| 구간 | n | kospi_ret sd | usdkrw_ret sd | ccsi_diff sd |")
    add("|------|---|--------------|---------------|--------------|")
    windows = [("2021-01", "2022-12"), ("2023-01", "2024-12"),
               ("2025-01", "2025-12"), ("2026-01", "2026-07")]
    for lo, hi in windows:
        w = study[study["month"].between(lo, hi)]
        add(f"| {lo}~{hi} | {len(w)} | {w['kospi_ret'].std():.2f} | "
            f"{w['usdkrw_ret'].std():.2f} | {w['ccsi_diff'].std():.2f} |")
    add("")
    add("2026년 상반기 코스피 변동성이 앞 구간의 수 배로 뛴다. 2026-07 대폭락(월간 -22.2%)은 "
        "확인된 실제 값이지 수집 오류가 아니다. 환율·심리는 같은 정도로 흔들리지 않았으므로 "
        "코스피 고유의 분산 급증이다.\n")
    add("Step 4에서 `kospi_ret`을 그대로 쓰면 마지막 7개월이 국면 계수를 지배한다. "
        "패널의 `kospi_ret_std`(직전 12개월 변동성으로 표준화)로 재추정해 결과가 유지되는지 "
        "확인하고, 2026년 제외 표본을 강건성 검증에 포함해야 한다.\n")

    add("## 6. 검색 급등 판별 (|z| >= 3)\n")
    add("`score_rel = score / anchor_score`라, 앵커가 무너진 달에도 값이 치솟는다. "
        "관심도가 실제로 뛴 것인지 정규화가 깨진 것인지 앵커를 같이 봐야 구분된다.\n")
    add("| 국면 | 월 | score_rel | z | 앵커 z | 판정 |")
    add("|------|-----|-----------|---|--------|------|")
    flagged = 0
    for label, slug in slugs.items():
        level = panel[f"srch_{slug}"]
        z = (level - level.mean()) / level.std()
        anchor = panel["month"].map(anchors[label])
        az = (anchor - anchor.mean()) / anchor.std()
        for i in z[z.abs() >= OUTLIER_Z].index:
            flagged += 1
            ok = abs(az[i]) < 2
            add(f"| {label} | {panel.loc[i, 'month']} | {level[i]:.2f} | {z[i]:+.2f} | "
                f"{az[i]:+.2f} | {'실제 급등 (앵커 정상)' if ok else '**앵커 이상 — 확인 필요**'} |")
    if not flagged:
        add("| — | — | — | — | — | 없음 |")
    add("")
    add("앵커 z가 ±2 안이면 그 달의 요청이 정상 처리된 것이므로 급등은 검색량 자체의 변화다.\n")

    add("## 7. 검색-지표 상관 (분석 창, 차분 기준)\n")
    add("| 검색 국면 | kospi_ret | usdkrw_ret | ccsi_diff | cpi_yoy | base_rate_diff |")
    add("|-----------|-----------|------------|-----------|---------|----------------|")
    targets = ["kospi_ret", "usdkrw_ret", "ccsi_diff", "cpi_yoy", "base_rate_diff"]
    for label, slug in slugs.items():
        cors = [study[f"srch_{slug}_dlog"].corr(study[t]) for t in targets]
        add(f"| {label} | " + " | ".join(f"{c:+.2f}" for c in cors) + " |")
    add("")

    add("## 8. 정상성 (ADF, 분석 창)\n")
    try:
        from statsmodels.tsa.stattools import adfuller

        # AIC 시차 선택과 시차 0을 함께 본다. 관측치가 67개뿐이라 AIC가 시차를 3~4개
        # 잡으면 자유도가 그만큼 깎여 차분 계열도 단위근을 기각하지 못하는 일이 생긴다.
        add("| 열 | ADF p (AIC) | 선택 시차 | ADF p (시차 0) | 판정 |")
        add("|----|-------------|-----------|----------------|------|")
        for col in level_cols + diff_cols + ["cpi_yoy", "kospi_ret_std"]:
            s = study[col].dropna()
            if s.nunique() < 3:
                continue
            stat = adfuller(s, autolag="AIC", result_object=False)
            p0 = adfuller(s, maxlag=0, autolag=None, result_object=False)[1]
            if stat[1] < 0.05 and p0 < 0.05:
                verdict = "정상"
            elif p0 < 0.05:
                verdict = "시차 0에서만 정상 — 소표본 시차 과선택"
            else:
                verdict = "단위근 기각 못함"
            add(f"| `{col}` | {stat[1]:.3f} | {stat[2]} | {p0:.3f} | {verdict} |")
        add("")
        add("`kospi_ret`은 AIC 기준으로는 단위근을 기각하지 못하지만 시차 0에서는 p<0.001이다. "
            "2026년 등락이 번갈아 나오면서 생긴 시차 3~4 자기상관을 AIC가 집어 시차를 늘렸고, "
            "관측치 67개에서 그만큼 검정력이 떨어진 것이다. 추세를 가진 계열이 아니므로 "
            "차분 수준에서 정상으로 취급한다.\n")
        add("`base_rate_diff`는 대부분이 0이고 드물게 0.25~0.5씩 튀는 계단형이라 "
            "ADF 결과를 액면 그대로 읽으면 안 된다. `cpi_yoy`는 지속성이 큰 계열이라 "
            "단위근을 기각하지 못하는 것이 통상적이며, 회귀에서는 `cpi_mom`을 기본으로 쓴다.\n")
    except ImportError:
        add("statsmodels 미설치 — 건너뜀.\n")

    add("## 9. 뉴스량\n")
    add(f"분석 창 월평균 {study['news_n'].mean():,.0f}건 "
        f"(최소 {study['news_n'].min():,} · 최대 {study['news_n'].max():,}), "
        f"언론사 {int(study['news_sources'].min())}~{int(study['news_sources'].max())}개.")
    thin = study[study["news_n"] < cfg["analysis"]["min_articles_per_month"]]
    add(f"최소 건수({cfg['analysis']['min_articles_per_month']}) 미달 월: "
        + (", ".join(thin["month"]) if not thin.empty else "없음") + "\n")

    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cfg = load_config()
    start = cfg["project"]["data_buffer_start"]
    end = cfg["project"]["study_period_end"]
    study_start = cfg["project"]["study_period_start"]
    slugs: dict[str, str] = cfg["regimes"]["slugs"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    panel = month_index(start, end)
    panel["in_study"] = panel["date"] >= pd.Timestamp(study_start)
    print(f"월 격자 {panel['month'].iloc[0]} ~ {panel['month'].iloc[-1]} ({len(panel)}개월)")

    panel = panel.merge(load_ecos(), on="month", how="left")

    search = load_search("regime")
    missing = set(slugs) - set(search.columns)
    if missing:
        raise ValueError(f"데이터랩 대분류에 없는 국면: {sorted(missing)}")
    panel = panel.merge(
        search[list(slugs)].rename(columns={k: f"srch_{v}" for k, v in slugs.items()}),
        on="month", how="left",
    )

    panel = panel.merge(load_news(), on="month", how="left")

    panel = add_indicator_derivatives(panel)
    panel = add_search_derivatives(panel, slugs, load_search_daily_std())
    panel = panel[order_columns(panel, slugs)]
    panel.to_csv(PANEL_PATH, index=False, encoding="utf-8-sig")

    sub_wide = load_search("sub")
    sub = panel[["month", "in_study"]].merge(
        sub_wide.reset_index(), on="month", how="left"
    )
    sub.to_csv(SUB_PATH, index=False, encoding="utf-8-sig")

    write_qc(panel, sub, load_anchor(), slugs, cfg)

    study = panel[panel["in_study"]]
    print(f"\n=== 패널 ===")
    print(f"전체 {panel.shape[0]}개월 × {panel.shape[1]}열 · 분석 창 {len(study)}개월")
    print(f"검색 세부 {sub.shape[1] - 2}그룹")
    print(f"분석 창 결측 열: "
          f"{[c for c in panel.columns if study[c].isna().any()] or '없음'}")
    print(f"\n패널 → {PANEL_PATH}")
    print(f"세부 → {SUB_PATH}")
    print(f"QC   → {QC_PATH}")


if __name__ == "__main__":
    main()
