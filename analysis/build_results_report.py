"""연구 결과 PDF 보고서 생성.

  python -m analysis.build_results_report

수치는 data/processed 아래 CSV·QC에서 읽는다. 반올림은 표 가독성용이며
원값은 CSV에 있다. 본분석 국면은 NMF다.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import project_root

ROOT = project_root()
PROC = ROOT / "data" / "processed"
FIG_DIR = ROOT / "docs" / "report_figures"
PDF_PATH = ROOT / "docs" / "한국형_경제이슈국면_연구결과보고서.pdf"

FONT_REG = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BD = Path(r"C:\Windows\Fonts\malgunbd.ttf")

NAVY = HexColor("#1B365D")
SLATE = HexColor("#334155")
MUTED = HexColor("#5B6573")
LINE = HexColor("#D0D5DD")
ROW_ALT = HexColor("#F4F6F8")
MATCH = HexColor("#1F6B4A")
PARTIAL = HexColor("#9A6B12")
MISS = HexColor("#9B3A3A")
CREAM = HexColor("#F7F4EE")
PILL = HexColor("#E8EEF4")

REGIME_ORDER = ["금리", "부동산", "가계대출", "대외통상", "AI반도체", "증시실적"]
REGIME_COLORS = {
    "금리": "#B85C38",
    "부동산": "#2C5F8A",
    "가계대출": "#6B4C9A",
    "대외통상": "#2A7F6F",
    "AI반도체": "#C47B1A",
    "증시실적": "#3D4A5C",
    "물가": "#9AA3AD",
    "기타": "#B8B8B8",
}
MPL_NAVY = "#1B365D"
MPL_MATCH = "#1F6B4A"
MPL_PARTIAL = "#9A6B12"
MPL_MISS = "#9B3A3A"
ALPHA = 0.05


def setup_mpl() -> None:
    from matplotlib import font_manager

    font_manager.fontManager.addfont(str(FONT_REG))
    plt.rcParams.update(
        {
            "font.family": "Malgun Gothic",
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.labelcolor": "#1B365D",
            "xtick.color": "#334155",
            "ytick.color": "#334155",
            "text.color": "#1B365D",
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.grid": True,
            "grid.color": "#E6E8EC",
            "grid.linewidth": 0.6,
            "axes.axisbelow": True,
        }
    )


def fmt_p(p: float, digits: int = 4) -> str:
    if p != p:
        return "—"
    if p < 0.0001:
        return f"{p:.2e}"
    return f"{p:.{digits}f}"


def fmt_n(x: float, digits: int = 3) -> str:
    if x != x:
        return "—"
    if abs(x) >= 100:
        return f"{x:.1f}"
    return f"{x:.{digits}f}"


def exact(x: float) -> str:
    """CSV와 같은 배정밀도 값을 잘라내지 않고 쓴다."""
    if x != x:
        return "—"
    return format(float(x), ".16g")


def load_data() -> dict:
    regimes = pd.read_csv(PROC / "regimes" / "regime_monthly.csv")
    panel = pd.read_csv(PROC / "panel" / "monthly_panel.csv")
    tests = pd.read_csv(PROC / "reactions" / "regime_tests.csv")
    react = pd.read_csv(PROC / "reactions" / "regime_reaction.csv")
    robust = pd.read_csv(PROC / "reactions" / "robustness_compare.csv")
    rq4c = pd.read_csv(PROC / "reactions" / "rq4_corr.csv")
    rq4m = pd.read_csv(PROC / "reactions" / "rq4_concordance.csv")
    rq4mo = pd.read_csv(PROC / "reactions" / "rq4_monthly.csv")
    cps = pd.read_csv(PROC / "regimes" / "changepoints.csv")
    ev = pd.read_csv(PROC / "reactions" / "event_study.csv")
    evs = pd.read_csv(PROC / "reactions" / "event_study_summary.csv")
    dummy = pd.read_csv(PROC / "reactions" / "regime_regression.csv")
    share = pd.read_csv(PROC / "reactions" / "share_regression.csv")
    lda_tests = pd.read_csv(PROC / "reactions_lda" / "regime_tests.csv")
    lda_react = pd.read_csv(PROC / "reactions_lda" / "regime_reaction.csv")
    lda_pw = pd.read_csv(PROC / "reactions_lda" / "pairwise_tests.csv")
    tmap = pd.read_csv(PROC / "regimes" / "topic_regime_map.csv")
    joined = panel.merge(
        regimes[["month", "dominant_regime", "dominant_raw", "share_aichip", "share_rates", "share_equity"]],
        on="month",
        how="inner",
    )
    if "in_study" in joined.columns:
        joined = joined[joined["in_study"].astype(str).isin(["True", "true", "1"])].copy()
    joined["month_dt"] = pd.to_datetime(joined["month"])
    return {
        "regimes": regimes,
        "panel": panel,
        "joined": joined,
        "tests": tests,
        "react": react,
        "robust": robust,
        "rq4c": rq4c,
        "rq4m": rq4m,
        "rq4mo": rq4mo,
        "cps": cps,
        "ev": ev,
        "evs": evs,
        "dummy": dummy,
        "share": share,
        "lda_tests": lda_tests,
        "lda_react": lda_react,
        "lda_pw": lda_pw,
        "tmap": tmap,
    }


def savefig(fig: plt.Figure, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def fig_pipeline() -> Path:
    fig, ax = plt.subplots(figsize=(10.6, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    boxes = [
        (0.2, 4.4, 2.2, 1.2, "1. 수집", "빅카인즈 뉴스\nECOS 지표\n데이터랩 검색"),
        (3.0, 4.4, 2.2, 1.2, "2. 전처리", "코퍼스 정제\n문서×어휘 행렬\n월 패널"),
        (5.8, 4.4, 2.2, 1.2, "3. 국면 탐지", "NMF 14토픽\nz-우세 라벨\nPELT 전환"),
        (8.6, 4.4, 2.2, 1.2, "4. 반응 분석", "국면별 평균\nKW / Holm\nHAC 회귀"),
        (1.6, 1.5, 2.4, 1.3, "5. 강건성", "2026 제외\nkospi_ret_std"),
        (4.8, 1.5, 2.4, 1.3, "6. RQ4 검색", "뉴스 비중↔검색\n라벨 일치율"),
        (8.0, 1.5, 2.8, 1.3, "7. 조건부 폴백", "KW 약하면 LDA\nBERTopic은 비교용"),
    ]
    for x, y, w, h, title, body in boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                facecolor="#F4F7FA", edgecolor=MPL_NAVY, linewidth=1.2,
            )
        )
        ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="center", fontsize=10, fontweight="bold", color=MPL_NAVY)
        ax.text(x + w / 2, y + 0.42, body, ha="center", va="center", fontsize=7.5, color="#334155")
    arrows = [(2.4, 5.0, 3.0, 5.0), (5.2, 5.0, 5.8, 5.0), (8.0, 5.0, 8.6, 5.0)]
    for x1, y1, x2, y2 in arrows:
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=MPL_NAVY, lw=1.3))
    ax.annotate("", xy=(2.8, 2.8), xytext=(9.7, 4.4),
                arrowprops=dict(arrowstyle="-|>", color="#7A8494", lw=1.0, connectionstyle="arc3,rad=0.12"))
    ax.annotate("", xy=(6.0, 2.8), xytext=(9.7, 4.4),
                arrowprops=dict(arrowstyle="-|>", color="#7A8494", lw=1.0, connectionstyle="arc3,rad=0.02"))
    ax.annotate("", xy=(9.4, 2.8), xytext=(9.7, 4.4),
                arrowprops=dict(arrowstyle="-|>", color="#7A8494", lw=1.0, connectionstyle="arc3,rad=-0.08"))
    ax.set_title("본분석은 NMF 경로. LDA·BERTopic은 본국면을 대체하지 않는다.", loc="left", fontsize=9, color="#5B6573", pad=8)
    return savefig(fig, "fig_pipeline.png")


def fig_scorecard() -> Path:
    rows = [
        ("RQ1 국면 분류", "부분 성립", MPL_PARTIAL, "6개 해석 가능 국면\n물가 독립축 없음 · 33개 구간"),
        ("RQ2 전환 탐지", "부분 성립", MPL_PARTIAL, "국면 신호 4건\n2026-03·07은 PELT 미탐지"),
        ("RQ3 주가설", "성립하지 않음", MPL_MISS, "코스피·환율·CCSI\nKW p≥0.05, Holm 0/60"),
        ("RQ3 보조", "부분 성립", MPL_PARTIAL, "기준금리 차분만 KW 유의\n더미 회귀에서 금리 계수 유의"),
        ("RQ4 검색 정합", "부분 성립", MPL_PARTIAL, "AI·부동산·금리 상관\n라벨 일치 22/67, 증시실적 약함"),
        ("폴백 LDA", "대체 아님", MPL_MISS, "4그룹에서 코스피 KW 유의\n금리·가계대출 축 소실"),
    ]
    fig, ax = plt.subplots(figsize=(10.6, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    for i, (q, verdict, color, note) in enumerate(rows):
        y = 5.3 - i * 0.95
        ax.add_patch(FancyBboxPatch((0.2, y), 2.6, 0.82, boxstyle="round,pad=0.03,rounding_size=0.08",
                                    facecolor="#F4F7FA", edgecolor="#D0D5DD", linewidth=0.8))
        ax.text(1.5, y + 0.41, q, ha="center", va="center", fontsize=9, fontweight="bold", color=MPL_NAVY)
        ax.add_patch(FancyBboxPatch((3.0, y + 0.18), 2.3, 0.48, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=color, edgecolor=color, linewidth=0))
        ax.text(4.15, y + 0.42, verdict, ha="center", va="center", fontsize=8.5, color="white", fontweight="bold")
        ax.text(5.55, y + 0.41, note, ha="left", va="center", fontsize=8, color="#334155")
    ax.set_title("연구 질문별 사전 가설과 결과의 대응 (본분석 = NMF)", loc="left", fontsize=11)
    return savefig(fig, "fig_scorecard.png")


def fig_regime_counts(d: dict) -> Path:
    s = d["joined"]["dominant_regime"].value_counts().reindex(REGIME_ORDER).fillna(0).astype(int)
    fig, ax = plt.subplots(figsize=(9.2, 4.0))
    colors = [REGIME_COLORS[k] for k in s.index]
    bars = ax.bar(s.index, s.values, color=colors, width=0.72, zorder=3)
    for b, v in zip(bars, s.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.25, str(int(v)), ha="center", va="bottom", fontsize=9, color=MPL_NAVY)
    ax.axhline(0, color="#D0D5DD", lw=0.8)
    ax.set_ylabel("개월 수 (67개월 중)")
    ax.set_ylim(0, max(s.values) + 3)
    ax.set_title("z-우세 국면별 개월 수 — 물가는 0개월 (독립 토픽 없음)")
    fig.text(0.01, -0.02, "원본: regime_monthly.csv 의 dominant_regime. 물가 라벨이 붙은 달은 없다.", fontsize=7.5, color="#5B6573")
    return savefig(fig, "fig_regime_counts.png")


def fig_timeline(d: dict) -> Path:
    df = d["joined"].sort_values("month_dt")
    fig, ax = plt.subplots(figsize=(10.8, 2.35))
    for i, (_, row) in enumerate(df.iterrows()):
        ax.bar(i, 1.0, width=1.0, color=REGIME_COLORS.get(row["dominant_regime"], "#999"), linewidth=0, zorder=3)
    cps = d["cps"]
    cps_r = cps[cps["signal"] == "regimes"]
    month_to_i = {m: i for i, m in enumerate(df["month"].tolist())}
    for _, r in cps_r.iterrows():
        idx = month_to_i.get(str(r["cp_month"]))
        if idx is not None:
            ax.axvline(idx - 0.5, color="white", lw=1.4, zorder=4)
            ax.axvline(idx - 0.5, color="#1B365D", lw=0.9, ls="--", zorder=5)
            ax.text(idx, 1.08, str(r["cp_month"]), ha="left", va="bottom", fontsize=7, rotation=0, color=MPL_NAVY)
    ax.set_xlim(-0.5, len(df) - 0.5)
    ax.set_ylim(0, 1.35)
    ax.set_yticks([])
    ticks = list(range(0, len(df), 6))
    ax.set_xticks(ticks)
    ax.set_xticklabels([df["month"].iloc[i] for i in ticks], rotation=40, ha="right")
    handles = [mpatches.Patch(color=REGIME_COLORS[k], label=k) for k in REGIME_ORDER]
    ax.legend(handles=handles, ncol=6, loc="upper center", bbox_to_anchor=(0.5, 1.38), frameon=False, fontsize=8)
    ax.set_title("월별 z-우세 국면 시계열 (점선 = PELT 국면 신호 전환월)", pad=18)
    ax.grid(False)
    return savefig(fig, "fig_timeline.png")


def fig_shares(d: dict) -> Path:
    r = d["regimes"].copy()
    r["month_dt"] = pd.to_datetime(r["month"])
    fig, ax = plt.subplots(figsize=(10.6, 4.2))
    mapping = {
        "share_rates": "금리",
        "share_realestate": "부동산",
        "share_hhdebt": "가계대출",
        "share_trade": "대외통상",
        "share_aichip": "AI반도체",
        "share_equity": "증시실적",
    }
    for col, lab in mapping.items():
        ax.plot(r["month_dt"], r[col], label=lab, color=REGIME_COLORS[lab], lw=1.6)
    ax.set_ylabel("원비중")
    ax.set_title("국면 원비중 시계열 — 증시실적은 상시 가장 크다")
    ax.legend(ncol=3, frameon=False, loc="upper left")
    ax.set_ylim(0, 0.30)
    fig.autofmt_xdate(rotation=40, ha="right")
    return savefig(fig, "fig_shares.png")


def fig_kw_pvalues(d: dict) -> Path:
    kw = d["tests"][d["tests"]["test"] == "kruskal"].copy()
    labels = {
        "kospi_ret": "코스피 수익률",
        "usdkrw_ret": "환율 변화",
        "ccsi_diff": "소비자심리",
        "cpi_mom": "물가 전월비",
        "base_rate_diff": "기준금리 차분",
        "kospi_ret_std": "코스피(표준화)",
    }
    kw["label"] = kw["dep_var"].map(labels)
    kw = kw.dropna(subset=["label"])
    order = list(labels.values())
    kw["label"] = pd.Categorical(kw["label"], categories=order, ordered=True)
    kw = kw.sort_values("label")
    colors = [MPL_MATCH if p < ALPHA else MPL_MISS for p in kw["p_value"]]
    fig, ax = plt.subplots(figsize=(9.4, 4.2))
    ax.barh(kw["label"], kw["p_value"], color=colors, height=0.62, zorder=3)
    ax.axvline(ALPHA, color=MPL_PARTIAL, ls="--", lw=1.3, label=f"유의수준 α = {ALPHA}")
    ax.set_xlabel("Kruskal–Wallis p값 (1순위 검정)")
    ax.set_xlim(0, 1.0)
    ax.invert_yaxis()
    for y, p in zip(kw["label"], kw["p_value"]):
        ax.text(min(p + 0.02, 0.92), y, fmt_p(p), va="center", fontsize=8, color="#334155")
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("국면 그룹 차이 검정 — 초록: p<0.05, 적갈: p≥0.05")
    return savefig(fig, "fig_kw_pvalues.png")


def fig_means_three(d: dict) -> Path:
    react = d["react"]
    deps = [
        ("kospi_ret", "코스피 월 로그수익률 (%)"),
        ("usdkrw_ret", "원/달러 월 로그변화율 (%)"),
        ("ccsi_diff", "소비자심리지수 전월차 (포인트)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(11.0, 4.0), sharex=True)
    for ax, (dep, title) in zip(axes, deps):
        sub = react[(react["dep_var"] == dep) & (react["regime"].isin(REGIME_ORDER))].copy()
        sub["regime"] = pd.Categorical(sub["regime"], categories=REGIME_ORDER, ordered=True)
        sub = sub.sort_values("regime")
        colors = [REGIME_COLORS[r] for r in sub["regime"]]
        ax.bar(sub["regime"], sub["mean"], color=colors, width=0.72, zorder=3)
        ax.axhline(0, color="#7A8494", lw=0.8)
        overall = react[(react["dep_var"] == dep) & (react["regime"] == "전체")]["mean"].iloc[0]
        ax.axhline(overall, color=MPL_NAVY, ls=":", lw=1.1, label="전체 평균")
        ax.set_title(title, fontsize=9)
        ax.tick_params(axis="x", rotation=45)
        ax.set_ylabel("")
        if ax is axes[0]:
            ax.legend(frameon=False, fontsize=7)
    fig.suptitle("국면별 평균 — 수준 차이는 보이지만, 주 3개 변수의 KW는 유의하지 않다", fontsize=11, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_means_three.png")


def fig_kospi_box(d: dict) -> Path:
    j = d["joined"].copy()
    j["dominant_regime"] = pd.Categorical(j["dominant_regime"], categories=REGIME_ORDER, ordered=True)
    data = [j.loc[j["dominant_regime"] == r, "kospi_ret"].dropna().values for r in REGIME_ORDER]
    fig, ax = plt.subplots(figsize=(9.4, 4.3))
    bp = ax.boxplot(data, tick_labels=REGIME_ORDER, patch_artist=True, widths=0.62, showfliers=True)
    for patch, r in zip(bp["boxes"], REGIME_ORDER):
        patch.set_facecolor(REGIME_COLORS[r])
        patch.set_alpha(0.85)
        patch.set_edgecolor(MPL_NAVY)
    for med in bp["medians"]:
        med.set_color("white")
        med.set_linewidth(1.4)
    ax.axhline(0, color="#7A8494", lw=0.8)
    ax.set_ylabel("kospi_ret (%)")
    ax.set_title("코스피 월수익률 분포 — AI반도체는 평균이 높고 분산도 크다")
    ax.tick_params(axis="x", rotation=20)
    return savefig(fig, "fig_kospi_box.png")


def fig_volatility(d: dict) -> Path:
    j = d["joined"].copy()
    j["period"] = pd.cut(
        j["month_dt"],
        bins=pd.to_datetime(["2021-01-01", "2023-01-01", "2025-01-01", "2026-01-01", "2026-08-01"]),
        right=False,
        labels=["2021–22", "2023–24", "2025", "2026(1–7월)"],
    )
    stats = j.groupby("period", observed=True)[["kospi_ret", "usdkrw_ret", "ccsi_diff"]].std()
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    x = np.arange(len(stats.index))
    w = 0.25
    ax.bar(x - w, stats["kospi_ret"], w, label="코스피", color="#1B365D", zorder=3)
    ax.bar(x, stats["usdkrw_ret"], w, label="환율", color="#2A7F6F", zorder=3)
    ax.bar(x + w, stats["ccsi_diff"], w, label="CCSI", color="#C47B1A", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(stats.index.astype(str))
    ax.set_ylabel("월별 표준편차")
    ax.set_title("구간별 변동성 — 2026년 코스피 분산 급증은 환율·심리와 같지 않다")
    ax.legend(frameon=False)
    return savefig(fig, "fig_volatility.png")


def fig_robustness(d: dict) -> Path:
    r = d["robust"].copy()
    labels = {
        "kospi_ret": "코스피",
        "usdkrw_ret": "환율",
        "ccsi_diff": "CCSI",
        "base_rate_diff": "기준금리",
        "kospi_ret_std": "코스피(표준화)",
        "cpi_mom": "물가 전월비",
    }
    r["label"] = r["dep_var"].map(labels)
    r = r.dropna(subset=["label"])
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    x = np.arange(len(r))
    ax.bar(x - 0.18, r["p_full"], 0.36, label="전체 67개월", color=MPL_NAVY, zorder=3)
    ax.bar(x + 0.18, r["p_no2026"], 0.36, label="2026 제외 60개월", color="#7A9BB8", zorder=3)
    ax.axhline(ALPHA, color=MPL_PARTIAL, ls="--", lw=1.2, label="α = 0.05")
    ax.set_xticks(x)
    ax.set_xticklabels(r["label"], rotation=20)
    ax.set_ylabel("KW p값")
    ax.set_ylim(0, 1.05)
    ax.set_title("강건성: 2026 제외 후에도 주 3개 유의 여부는 뒤집히지 않는다")
    ax.legend(frameon=False, ncol=3)
    return savefig(fig, "fig_robustness.png")


def fig_rq4_corr(d: dict) -> Path:
    c = d["rq4c"]
    c = c[c["search_kind"] == "z"].copy()
    fig, ax = plt.subplots(figsize=(9.2, 4.1))
    colors = []
    vals = []
    names = []
    for _, row in c.iterrows():
        names.append(row["regime"])
        p = row["pearson"]
        if p != p:
            vals.append(0.0)
            colors.append("#D0D5DD")
        else:
            vals.append(p)
            colors.append(MPL_MATCH if p >= 0.4 else (MPL_PARTIAL if p >= 0.2 else MPL_MISS))
    bars = ax.bar(names, vals, color=colors, width=0.7, zorder=3)
    ax.axhline(0, color="#7A8494", lw=0.8)
    ax.set_ylabel("Pearson r (뉴스 비중 vs 검색 z)")
    ax.set_ylim(-0.15, 1.0)
    ax.set_title("RQ4: 같은 축의 뉴스 비중과 검색 관심도의 상관")
    for b, v, n in zip(bars, vals, names):
        lab = "분산 0" if n == "물가" else f"{v:.3f}"
        ax.text(b.get_x() + b.get_width() / 2, (v if v == v else 0) + 0.03, lab, ha="center", fontsize=8, color=MPL_NAVY)
    ax.tick_params(axis="x", rotation=15)
    return savefig(fig, "fig_rq4_corr.png")


def fig_rq4_scatter(d: dict) -> Path:
    m = d["rq4mo"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0))
    pairs = [
        ("share_aichip", "srch_aichip_z", "AI반도체", 0.7505857678829452),
        ("share_equity", "srch_equity_z", "증시실적", 0.11345264061465014),
    ]
    for ax, (xcol, ycol, title, r) in zip(axes, pairs):
        ax.scatter(m[xcol], m[ycol], c=REGIME_COLORS[title], s=28, alpha=0.85, edgecolors="white", linewidths=0.4, zorder=3)
        z = np.polyfit(m[xcol].astype(float), m[ycol].astype(float), 1)
        xs = np.linspace(m[xcol].min(), m[xcol].max(), 50)
        ax.plot(xs, np.polyval(z, xs), color=MPL_NAVY, lw=1.1)
        ax.set_xlabel("뉴스 국면 비중")
        ax.set_ylabel("검색 z")
        ax.set_title(f"{title}  (r = {r:.3f})")
    fig.suptitle("가설과 맞는 축(AI반도체)과 약한 축(증시실적)", fontsize=11, y=1.02)
    fig.tight_layout()
    return savefig(fig, "fig_rq4_scatter.png")


def fig_event(d: dict) -> Path:
    ev = d["ev"]
    sub = ev[(ev["signal"] == "regimes") & (ev["dep_var"] == "kospi_ret")].copy()
    fig, ax = plt.subplots(figsize=(9.4, 4.2))
    for (cp, fr, to), g in sub.groupby(["cp_month", "from_label", "to_label"]):
        g = g.sort_values("offset")
        ax.plot(g["offset"], g["value"], marker="o", ms=4, lw=1.5, label=f"{cp}  {fr}→{to}")
    ax.axvline(0, color=MPL_NAVY, ls="--", lw=1.0)
    ax.axhline(0, color="#7A8494", lw=0.8)
    ax.set_xlabel("전환월 기준 시차 (개월)")
    ax.set_ylabel("kospi_ret (%)")
    ax.set_title("국면 신호 전환 ±3개월 코스피 경로 (사례 기술, n=4)")
    ax.legend(frameon=False, fontsize=7.5)
    ax.set_xticks(range(-3, 4))
    return savefig(fig, "fig_event.png")


def fig_nmf_lda(d: dict) -> Path:
    labels = {
        "kospi_ret": "코스피",
        "usdkrw_ret": "환율",
        "ccsi_diff": "CCSI",
        "base_rate_diff": "기준금리",
    }
    nmf = d["tests"][(d["tests"]["test"] == "kruskal") & (d["tests"]["dep_var"].isin(labels))]
    lda = d["lda_tests"][(d["lda_tests"]["test"] == "kruskal") & (d["lda_tests"]["dep_var"].isin(labels))]
    order = list(labels.keys())
    nmf = nmf.set_index("dep_var").loc[order]
    lda = lda.set_index("dep_var").loc[order]
    fig, ax = plt.subplots(figsize=(8.8, 4.1))
    x = np.arange(len(order))
    ax.bar(x - 0.18, nmf["p_value"], 0.36, label="NMF 6그룹 (본분석)", color=MPL_NAVY, zorder=3)
    ax.bar(x + 0.18, lda["p_value"], 0.36, label="LDA 4그룹 (폴백)", color="#C47B1A", zorder=3)
    ax.axhline(ALPHA, color=MPL_PARTIAL, ls="--", lw=1.2)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[k] for k in order])
    ax.set_ylabel("KW p값")
    ax.set_ylim(0, 1.05)
    ax.set_title("같은 행렬, 다른 토픽 모형 — LDA에서 코스피 p는 작아지지만 축이 줄어든다")
    ax.legend(frameon=False)
    return savefig(fig, "fig_nmf_lda.png")


def fig_concordance(d: dict) -> Path:
    m = d["rq4m"]
    z = m[m["rule"] == "search_z"].iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    names = ["검색 z argmax\n일치율", "7국면 균등\n무작위"]
    vals = [z["match_rate"], 1 / 7]
    colors = [MPL_PARTIAL, "#D0D5DD"]
    bars = ax.bar(names, vals, color=colors, width=0.55, zorder=3)
    ax.set_ylim(0, 0.55)
    ax.set_ylabel("일치율")
    ax.set_title(f"뉴스 라벨 vs 검색 라벨  —  {int(z['match'])}/{int(z['n'])} = {z['match_rate']:.4f}")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}", ha="center", fontsize=9, color=MPL_NAVY)
    return savefig(fig, "fig_concordance.png")


def fig_hypothesis_means(d: dict) -> Path:
    """금리 vs AI반도체 코스피 — 기술적으로는 벌어지나 KW는 유의하지 않음."""
    react = d["react"]
    sub = react[(react["dep_var"] == "kospi_ret") & (react["regime"].isin(REGIME_ORDER))].copy()
    sub["regime"] = pd.Categorical(sub["regime"], categories=REGIME_ORDER, ordered=True)
    sub = sub.sort_values("regime")
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    colors = [REGIME_COLORS[r] for r in sub["regime"]]
    ax.bar(sub["regime"], sub["mean"], color=colors, width=0.7, zorder=3, yerr=sub["sd"], capsize=3, ecolor="#7A8494", error_kw={"elinewidth": 0.9})
    ax.axhline(0, color="#7A8494", lw=0.8)
    ax.set_ylabel("평균 kospi_ret (%)  ± 1 SD")
    ax.set_title("기술 통계는 금리(음) vs AI반도체(양)로 갈리나, 분산이 커 KW는 기각하지 못한다")
    ax.tick_params(axis="x", rotation=15)
    rates = sub.loc[sub["regime"] == "금리", "mean"].iloc[0]
    ai = sub.loc[sub["regime"] == "AI반도체", "mean"].iloc[0]
    ax.annotate(
        f"금리 {rates:.3f}%\n(n=10)",
        xy=(0, rates),
        xytext=(0.6, -12),
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MPL_MISS, lw=0.9),
        color=MPL_MISS,
    )
    ax.annotate(
        f"AI반도체 {ai:.3f}%\n(n=13)",
        xy=(4, ai),
        xytext=(3.0, 18),
        fontsize=8,
        arrowprops=dict(arrowstyle="->", color=MPL_MATCH, lw=0.9),
        color=MPL_MATCH,
    )
    return savefig(fig, "fig_kospi_means_sd.png")


def make_figures(d: dict) -> dict[str, Path]:
    setup_mpl()
    return {
        "pipeline": fig_pipeline(),
        "scorecard": fig_scorecard(),
        "counts": fig_regime_counts(d),
        "timeline": fig_timeline(d),
        "shares": fig_shares(d),
        "kw": fig_kw_pvalues(d),
        "means": fig_means_three(d),
        "box": fig_kospi_box(d),
        "vol": fig_volatility(d),
        "robust": fig_robustness(d),
        "rq4c": fig_rq4_corr(d),
        "rq4s": fig_rq4_scatter(d),
        "event": fig_event(d),
        "nmflda": fig_nmf_lda(d),
        "conc": fig_concordance(d),
        "kospi_sd": fig_hypothesis_means(d),
    }


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Malgun", str(FONT_REG)))
    pdfmetrics.registerFont(TTFont("MalgunBd", str(FONT_BD)))


def styles() -> dict:
    base = getSampleStyleSheet()
    s = {}
    s["cover_kicker"] = ParagraphStyle("cover_kicker", fontName="Malgun", fontSize=10, textColor=NAVY, alignment=TA_LEFT, leading=14, tracking=0.4)
    s["cover_title"] = ParagraphStyle("cover_title", fontName="MalgunBd", fontSize=20, textColor=NAVY, alignment=TA_LEFT, leading=28, spaceAfter=8)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="Malgun", fontSize=11, textColor=SLATE, leading=16, spaceAfter=4)
    s["h1"] = ParagraphStyle("h1", fontName="MalgunBd", fontSize=13.5, textColor=NAVY, spaceBefore=12, spaceAfter=8, leading=18, borderPadding=3)
    s["h2"] = ParagraphStyle("h2", fontName="MalgunBd", fontSize=11.5, textColor=NAVY, spaceBefore=10, spaceAfter=6, leading=16)
    s["h3"] = ParagraphStyle("h3", fontName="MalgunBd", fontSize=10.5, textColor=SLATE, spaceBefore=8, spaceAfter=4, leading=14)
    s["body"] = ParagraphStyle("body", fontName="Malgun", fontSize=9.6, textColor=black, alignment=TA_JUSTIFY, leading=15.2, spaceAfter=7)
    s["note"] = ParagraphStyle("note", fontName="Malgun", fontSize=8.4, textColor=MUTED, leading=12.5, spaceAfter=6, leftIndent=4, rightIndent=4)
    s["caption"] = ParagraphStyle("caption", fontName="Malgun", fontSize=8.2, textColor=SLATE, leading=12, spaceBefore=2, spaceAfter=10, alignment=TA_LEFT)
    s["cell"] = ParagraphStyle("cell", fontName="Malgun", fontSize=7.8, textColor=black, leading=11, alignment=TA_CENTER)
    s["cell_l"] = ParagraphStyle("cell_l", fontName="Malgun", fontSize=7.8, textColor=black, leading=11, alignment=TA_LEFT)
    s["th"] = ParagraphStyle("th", fontName="MalgunBd", fontSize=7.8, textColor=white, leading=11, alignment=TA_CENTER)
    s["th_l"] = ParagraphStyle("th_l", fontName="MalgunBd", fontSize=7.8, textColor=white, leading=11, alignment=TA_LEFT)
    s["footer"] = ParagraphStyle("footer", fontName="Malgun", fontSize=7.5, textColor=MUTED, alignment=TA_CENTER)
    s["bullet"] = ParagraphStyle("bullet", fontName="Malgun", fontSize=9.4, textColor=black, leading=14.5, leftIndent=8)
    s["quote"] = ParagraphStyle("quote", fontName="Malgun", fontSize=9.4, textColor=NAVY, leading=14.5, leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=8)
    s["center"] = ParagraphStyle("center", fontName="Malgun", fontSize=9.5, textColor=SLATE, alignment=TA_CENTER, leading=14)
    return s


def P(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def img(path: Path, width: float = 170 * mm) -> Image:
    im = Image(str(path))
    ratio = im.imageHeight / float(im.imageWidth)
    im.drawWidth = width
    im.drawHeight = width * ratio
    return im


def styled_table(data: list, col_widths: list, has_header: bool = True) -> Table:
    t = Table(data, colWidths=col_widths, repeatRows=1 if has_header else 0)
    cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "Malgun"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROW_ALT]),
    ]
    if has_header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "MalgunBd"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ]
    t.setStyle(TableStyle(cmds))
    return t


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 11 * mm, A4[0], 11 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Malgun", 8)
    canvas.drawString(18 * mm, A4[1] - 7.2 * mm, "뉴스·검색 데이터 기반 한국형 경제 이슈 국면 탐지  ·  연구 결과 보고서")
    canvas.setFillColor(LINE)
    canvas.rect(0, 0, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Malgun", 7.5)
    canvas.drawString(18 * mm, 5 * mm, "원수치: data/processed  CSV · QC   |   본분석 국면: NMF")
    canvas.drawRightString(A4[0] - 18 * mm, 5 * mm, f"{doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, 12 * mm, A4[1], fill=1, stroke=0)
    canvas.setFillColor(CREAM)
    canvas.rect(12 * mm, 0, A4[0] - 12 * mm, A4[1], fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.rect(12 * mm, A4[1] - 28 * mm, A4[0] - 12 * mm, 28 * mm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Malgun", 9)
    canvas.drawString(22 * mm, A4[1] - 17 * mm, "DATA MINING  ·  RESEARCH RESULTS BRIEFING")
    canvas.restoreState()


def build_story(d: dict, figs: dict[str, Path], S: dict) -> list:
    tests = d["tests"]
    react = d["react"]
    robust = d["robust"]
    rq4c = d["rq4c"]
    rq4m = d["rq4m"]
    lda_tests = d["lda_tests"]
    dummy = d["dummy"]
    share = d["share"]
    joined = d["joined"]
    tmap = d["tmap"]

    def kw_row(dep: str) -> pd.Series:
        return tests[(tests["dep_var"] == dep) & (tests["test"] == "kruskal")].iloc[0]

    kospi_kw = kw_row("kospi_ret")
    fx_kw = kw_row("usdkrw_ret")
    ccsi_kw = kw_row("ccsi_diff")
    rate_kw = kw_row("base_rate_diff")
    kstd_kw = kw_row("kospi_ret_std")
    anova_kospi = tests[(tests["dep_var"] == "kospi_ret") & (tests["test"] == "anova")].iloc[0]
    lev_kospi = tests[(tests["dep_var"] == "kospi_ret") & (tests["test"] == "levene_bf")].iloc[0]
    lda_kospi = lda_tests[(lda_tests["dep_var"] == "kospi_ret") & (lda_tests["test"] == "kruskal")].iloc[0]
    lda_fx = lda_tests[(lda_tests["dep_var"] == "usdkrw_ret") & (lda_tests["test"] == "kruskal")].iloc[0]
    lda_ccsi = lda_tests[(lda_tests["dep_var"] == "ccsi_diff") & (lda_tests["test"] == "kruskal")].iloc[0]
    zrow = rq4m[rq4m["rule"] == "search_z"].iloc[0]
    pearson_z = rq4c[rq4c["search_kind"] == "z"]
    kospi_ai = react[(react["dep_var"] == "kospi_ret") & (react["regime"] == "AI반도체")].iloc[0]
    kospi_rates = react[(react["dep_var"] == "kospi_ret") & (react["regime"] == "금리")].iloc[0]
    kospi_all = react[(react["dep_var"] == "kospi_ret") & (react["regime"] == "전체")].iloc[0]
    dummy_rates = dummy[(dummy["dep_var"] == "kospi_ret") & (dummy["term"] == "rg_금리")].iloc[0]
    dummy_hh = dummy[(dummy["dep_var"] == "ccsi_diff") & (dummy["term"] == "rg_가계대출")].iloc[0]
    share_ccsi_rates = share[(share["dep_var"] == "ccsi_diff") & (share["term"] == "share_rates")].iloc[0]
    n_z1 = int((d["regimes"]["dominant_z"] > 1).sum()) if "dominant_z" in d["regimes"].columns else None
    n_diff_raw = int((d["regimes"]["dominant_regime"] != d["regimes"]["dominant_raw"]).sum())
    n_seg = 1
    labs = joined.sort_values("month_dt")["dominant_regime"].tolist()
    for i in range(1, len(labs)):
        if labs[i] != labs[i - 1]:
            n_seg += 1

    C = S["cell"]
    CL = S["cell_l"]
    TH = S["th"]
    THL = S["th_l"]

    def th(*xs):
        return [P(x, TH if i else THL) for i, x in enumerate(xs)] if False else [P(x, TH) for x in xs]

    def cells(*xs):
        out = []
        for i, x in enumerate(xs):
            out.append(P(str(x), CL if i == 0 else C))
        return out

    story = []

    # ----- COVER content (drawn over cream via onFirstPage; flowables still needed) -----
    story.append(Spacer(1, 22 * mm))
    story.append(P("연구 결과 보고서  ·  2026년 9월 19일", S["cover_kicker"]))
    story.append(Spacer(1, 5 * mm))
    story.append(P("뉴스·검색 데이터 기반<br/>한국형 경제 이슈 국면 탐지 및<br/>국면별 시장·심리 지표 반응 분석", S["cover_title"]))
    story.append(Spacer(1, 3 * mm))
    story.append(P("분석 기간  2021-01 ~ 2026-07 (67개월)  ·  본분석 국면  NMF(14토픽) → z-우세 6그룹", S["cover_sub"]))
    story.append(P("데이터  빅카인즈 경제지 3사  ·  한국은행 ECOS  ·  네이버 데이터랩", S["cover_sub"]))
    story.append(Spacer(1, 5 * mm))
    cover_meta = [
        [P("코퍼스", TH), P("931,709건 (행렬 투입 931,703건)", C)],
        [P("언론사", TH), P("매일경제 · 서울경제 · 한국경제 (경제지 기준)", C)],
        [P("국면 라벨", TH), P("물가 · 금리 · 부동산 · 가계대출 · 대외통상 · AI반도체 · 증시실적", C)],
        [P("1순위 검정", TH), P("Kruskal–Wallis, 유의수준 0.05, 쌍비교 Holm 보정", C)],
        [P("해석 원칙", TH), P("인과 단정 없음. 국면과 지표의 동시 움직임만 본다.", C)],
    ]
    mt = Table(cover_meta, colWidths=[32 * mm, 138 * mm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), NAVY),
        ("BACKGROUND", (1, 0), (1, -1), white),
        ("FONTNAME", (0, 0), (0, -1), "MalgunBd"),
        ("TEXTCOLOR", (0, 0), (0, -1), white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, NAVY),
    ]))
    story.append(mt)
    story.append(Spacer(1, 6 * mm))
    story.append(P("한 줄 결론", S["h3"]))
    story.append(P(
        "경제지 뉴스에서 이슈 국면은 식별할 수 있으나, 그 국면 라벨만으로 코스피·환율·소비자심리의 "
        "월별 반응이 다르다고 말할 증거는 부족하다. 기준금리 차분만 그룹 차이가 일관된다. "
        "검색은 AI반도체·부동산·금리 축에서 뉴스를 보조한다. 인과는 주장하지 않는다.",
        S["body"],
    ))
    story.append(P(
        "이 보고서는 저장소의 확정 산출(CSV·QC)을 근거로 한다. "
        "표의 소수 자릿수는 가독성을 위한 경우가 있으며, 검정 통계량은 CSV 원값을 그대로 적는다. "
        "LDA와 BERTopic은 본분석 국면을 대체하지 않는 비교 산출이다.",
        S["note"],
    ))
    story.append(PageBreak())

    # ----- 1. 한눈에 -----
    story.append(P("1. 한눈에 보는 결론", S["h1"]))
    story.append(P(
        "본 연구는 한국 경제 뉴스에서 <b>지금 어떤 이슈가 상대적으로 두드러지는가</b>를 월 단위로 식별하고, "
        "그 국면 라벨마다 코스피·환율·소비자심리의 움직임이 다른지를 검정했다. "
        "질문은 감성(긍정/부정)이 아니라 <b>이슈의 유형</b>이다.",
        S["body"],
    ))
    story.append(P(
        f"결과의 핵은 다음과 같다. 뉴스 토픽으로 해석 가능한 국면 축은 잡을 수 있었다(RQ1, 부분 성립). "
        f"변화점 탐지로 전환월도 식별했으나 2026년 시장 충격은 뉴스 국면 신호에서 전환으로 잡히지 않았다(RQ2, 부분 성립). "
        f"그러나 <b>사전 주가설인 ‘국면별로 코스피·환율·CCSI 반응이 다르다’는 Kruskal–Wallis 기준으로 성립하지 않았다</b>"
        f"(코스피 p={exact(kospi_kw['p_value'])}, 환율 p={exact(fx_kw['p_value'])}, CCSI p={exact(ccsi_kw['p_value'])}; "
        f"Holm 보정 후 국면쌍 p&lt;0.05는 0/60). "
        f"예외적으로 기준금리 전월차만 그룹 차이가 있었다(p={exact(rate_kw['p_value'])}). "
        f"검색 트렌드는 AI반도체·부동산·금리 축에서 뉴스 비중과 같이 움직였고, 라벨 일치율은 22/67이다(RQ4, 부분 성립).",
        S["body"],
    ))
    story.append(img(figs["scorecard"]))
    story.append(P("그림 1. 연구 질문별 가설 판정. 초록은 성립, 황토는 부분 성립, 적갈은 성립하지 않음(또는 대체 불가).", S["caption"]))

    story.append(P("2. 연구 주제와 질문", S["h1"]))
    story.append(P("2.1 주제", S["h2"]))
    story.append(P(
        "<b>정식 주제.</b> 뉴스·검색 데이터 기반 한국형 경제 이슈 국면 탐지 및 국면별 시장·심리 지표 반응 분석.",
        S["body"],
    ))
    story.append(P(
        "기존 뉴스 지수 연구(NSI 등)는 기사의 분위기—긍정인가 부정인가—를 한 줄의 점수로 요약한다. "
        "본 연구는 그 질문을 바꾸었다. 같은 부정 뉴스라도 금리 인상, 부동산 규제, 수출 충격, 반도체 사이클은 "
        "서로 다른 이슈다. 시기마다 <b>어떤 이슈가 전면에 있는지</b>를 데이터로 나누고, "
        "그 구분이 시장·심리 지표의 월별 움직임과 대응되는지를 본다. "
        "주가·집값의 단일 원인 지표를 만드는 연구가 아니며, “국면이 지수를 움직였다”는 인과는 주장하지 않는다.",
        S["body"],
    ))
    diff = [
        th("구분", "기존 뉴스 감성지수", "본 연구"),
        cells("핵심 질문", "분위기가 긍정/부정인가", "지금 어떤 이슈가 중심인가"),
        cells("산출", "감성 점수", "국면 라벨 + 토픽 비중 시계열"),
        cells("해석", "심리의 온도", "이슈 유형별 국면 식별"),
        cells("목표", "심리 요약", "국면 탐지와 국면별 반응 차이 검증"),
    ]
    story.append(styled_table(diff, [28 * mm, 62 * mm, 80 * mm]))
    story.append(P("표 1. 기존 감성지수 연구와의 차이. 출처: docs/research_plan.md.", S["caption"]))

    story.append(P("2.2 연구 질문", S["h2"]))
    story.append(P(
        "<b>RQ1.</b> 뉴스 토픽 비중으로 한국 경제 이슈 국면을 안정적으로 분류할 수 있는가.<br/>"
        "<b>RQ2.</b> 국면 전환 시점을 데이터 기반으로 탐지할 수 있는가.<br/>"
        "<b>RQ3.</b> 국면별로 코스피·환율·소비자심리지수(CCSI) 등의 반응 패턴이 다른가. "
        "이것이 사전 주가설이다. 1순위 검정은 Kruskal–Wallis다.<br/>"
        "<b>RQ4</b> (보조). 검색 트렌드는 뉴스 기반 국면을 보조·검증하는가. 검색으로 국면을 새로 정의하지는 않는다.",
        S["body"],
    ))
    story.append(P(
        "성공 기준은 계획서에 적혀 있다. 국면 라벨이 실제 이슈 흐름과 대체로 부합하고, "
        "국면별 지표 반응에 관측 가능한 차이가 있으며, 재현 가능한 파이프라인이 남는 것이다. "
        "차이가 일관되게 없으면 “한국 데이터에서 이슈 국면–반응 연결이 약하다”는 결과로 정리하기로 했다. "
        "본 보고서의 RQ3 주가설 판정은 그 후자에 해당한다.",
        S["body"],
    ))

    story.append(P("3. 용어 정리", S["h1"]))
    story.append(P(
        "아래 정의는 코드·설정·QC에 적힌 것과 같다. 일상어로 풀되, 의미를 바꾸지 않는다.",
        S["body"],
    ))
    gloss = [
        th("용어", "정의"),
        cells("국면", "그달 경제 뉴스에서 상대적으로 두드러진 이슈 축. 라벨 7개: 물가, 금리, 부동산, 가계대출, 대외통상, AI반도체, 증시실적."),
        cells("토픽 모형", "대량의 기사에서 함께 자주 나오는 어휘 묶음을 찾아 주제를 나누는 방법. 본분석은 NMF, 비교는 LDA·BERTopic."),
        cells("NMF", "비음수 행렬 분해. 문서-어휘 행렬을 ‘문서×토픽’과 ‘토픽×어휘’로 나눈다. 성분이 음수가 아니어서 비중으로 읽기 쉽다."),
        cells("z-우세", "7개 국면 비중을 67개월 안에서 표준화(z점수)한 뒤, 그달 가장 큰 축을 라벨로 쓴다. Step 4의 조인 라벨."),
        cells("원비중 우세", "표준화 없이 비중이 가장 큰 축. 본 자료에서는 67개월 전부 증시실적. 참고열일 뿐 본라벨이 아니다."),
        cells("PELT", "시계열의 평균이 바뀌는 지점을 찾는 변화점 알고리즘. 손실은 L2, 페널티는 BIC(차원×ln n), 최소 구간 3개월."),
        cells("Kruskal–Wallis", "세 개 이상 그룹의 분포가 같은지를 보는 비모수 검정. 정규분포를 가정하지 않는다. RQ3 1순위."),
        cells("Holm 보정", "여러 국면쌍을 동시에 비교할 때 우연한 유의 결과를 줄이기 위한 다중비교 보정."),
        cells("HAC", "Newey–West 표준오차(시차 최대 3). 월 자료의 자기상관을 표준오차에 반영한다."),
        cells("분석 창", "2021-01~2026-07, 67개월. 그 앞 2016-01~2020-12는 차분·시차용 lead-in이며 국면 라벨은 붙지 않는다."),
        cells("kospi_ret", "코스피 월 로그수익률×100. 단위는 %."),
        cells("kospi_ret_std", "kospi_ret을 직전 12개월 변동성으로 나눈 값. 2026년 분산 급증이 검정을 지배하지 않게 하는 강건성 변수."),
        cells("CCSI", "소비자심리지수. 본 분석의 종속변수는 전월 차분(ccsi_diff)."),
        cells("폴백", "본분석 KW가 약할 때만 같은 행렬에 LDA를 적합해 비교한다. NMF 라벨을 바꾸지 않는다."),
    ]
    story.append(styled_table(gloss, [32 * mm, 138 * mm]))
    story.append(P("표 2. 용어. 출처: docs/기술_참고.md §4 및 각 QC.", S["caption"]))

    story.append(P("4. 데이터와 분석 기간", S["h1"]))
    story.append(P(
        "분석 창은 빅카인즈 코퍼스가 존재하는 2021년 1월부터 2026년 7월까지 67개월이다. "
        "당초 2016년부터를 권장했으나 확보한 뉴스가 2021-01부터라 뉴스 가용 기간에 맞추었다. "
        "ECOS와 데이터랩은 2016-01부터 받아 두었고, 분석 창 시작 시점의 전월 차분·시차에 쓴다.",
        S["body"],
    ))
    data_tbl = [
        th("자료", "출처", "역할", "확인된 규모"),
        cells("경제 뉴스", "빅카인즈", "국면의 본체", "원본 61파일 998,020행 → 코퍼스 931,709건"),
        cells("거시·시장 지표", "한국은행 ECOS", "반응 분석 대상", "2016-01~2026-07, 127개월, 분석 창 결측 0"),
        cells("검색 트렌드", "네이버 데이터랩", "RQ4 보조 검증", "대분류 7 + 세부 28, 월·일"),
    ]
    story.append(styled_table(data_tbl, [32 * mm, 36 * mm, 38 * mm, 64 * mm]))
    story.append(P("표 3. 자료. 코퍼스 건수는 corpus/README.md, 패널 결측은 panel_qc.md.", S["caption"]))
    story.append(P(
        "코퍼스 투입에서 원본 998,020건 중 빅카인즈 자체 제외 플래그 53,194건, 파일 구간 중복 12,976건, "
        "키워드 없는 141건을 걸러 931,709건을 남겼다. 중복 판정은 URL이 1순위다. "
        "NMF 적합 시 어휘가 하나도 없는 6건을 더 빼 행렬 투입은 931,703건이다 "
        "(regimes_qc.md). 분석 창 월평균 기사 수는 13,906건(최소 11,588, 최대 16,815)이다.",
        S["body"],
    ))
    story.append(P(
        "토픽 입력은 빅카인즈 본문이 아니라 <b>키워드</b> 컬럼이다. 내보내기 본문은 기사의 약 95%에서 200자로 잘린다. "
        "키워드는 원문 전체의 형태소 분석 결과이므로 토픽 입력으로 택했다. "
        "언론사는 매일경제·서울경제·한국경제 세 곳뿐이다. 종합지를 추가하지 않기로 했으므로 "
        "이후 결과는 <b>경제지 기준 이슈 국면</b>으로 읽는다. 매체 편향은 통제하지 못했다.",
        S["body"],
    ))

    story.append(P("5. 파이프라인과 알고리즘", S["h1"]))
    story.append(img(figs["pipeline"]))
    story.append(P("그림 2. processed 캐시 이후의 분석 흐름. 통합 명령은 python -m analysis.run_pipeline.", S["caption"]))
    story.append(P(
        "본분석 경로는 처음부터 NMF다. 계획 초안의 LDA/BERTopic 우선 순서는, 전량 변환이 가능하고 "
        "성분이 비중으로 읽히는 NMF로 확정했다. MiniBatchNMF 전량 적합은 조기 종료로 성분이 갈리지 않아 버렸다.",
        S["body"],
    ))
    algo = [
        th("단계", "알고리즘·규칙", "확정 설정"),
        cells("문서 표현", "이진 문서-어휘 행렬 + TF-IDF", "931,703 × 28,343, 밀도 0.30%"),
        cells("토픽", "NMF (좌표하강, nndsvd)", "K=14, seed 42, 월당 3,000 층화표본 적합 후 전량 변환, iter 93"),
        cells("토픽→국면", "H 질량 × 데이터랩 키워드 세트", "점유 0.01 미만은 기타. 토픽 3(완성차)만 수동으로 기타"),
        cells("월 라벨", "국면 비중 z점수 argmax", "원비중 argmax는 참고열 (67개월 전부 증시실적)"),
        cells("전환", "PELT, L2, 열별 z", "페널티 dim×ln(n), 최소 구간 3개월. 배율을 바꿔 2026년을 맞추지 않음"),
        cells("그룹 비교", "Kruskal–Wallis → Mann–Whitney+Holm", "ANOVA·Levene는 보조. 개월 5 미만 국면은 제외(해당 없음)"),
        cells("회귀", "HAC OLS (Newey–West, maxlags=3)", "비중 z 회귀, 국면 더미+통제. 포화 설계는 본결과로 올리지 않음"),
        cells("강건성", "표본 분할", "2026-01 이후 7개월 제외, kospi_ret_std"),
        cells("검색", "Pearson/Spearman, 라벨 일치율", "검색으로 국면 재정의 없음"),
        cells("폴백", "online LDA, 조건부", "주 3개 KW가 모두 p≥0.05이면 가동. BERTopic은 별도 비교"),
    ]
    story.append(styled_table(algo, [28 * mm, 58 * mm, 84 * mm]))
    story.append(P("표 4. 알고리즘. 재구성 오차 437.307617, 행렬 sha256는 regimes_qc.md와 폴백 QC가 같다.", S["caption"]))
    story.append(P(
        "z-우세를 본라벨로 쓴 이유는 원비중 구조 때문이다. 증시·시황 기사가 경제지에 상시 많아 "
        "원비중 argmax는 67개월 모두 증시실적이다. 그 라벨로는 국면이 나뉘지 않는다. "
        "z점수는 ‘평소보다 상대적으로 올라온 축’을 고른다. 따라서 그룹 비교는 "
        "<b>긴 시기의 블록 비교가 아니라, 그 이슈가 상대적으로 올라온 달의 비교</b>로 읽어야 한다. "
        f"라벨은 67개월 동안 {n_seg}개 구간으로 갈린다. z&gt;1인 월은 48/67, "
        f"원비중 우세와 z-우세가 다른 월은 {n_diff_raw}개월이다.",
        S["body"],
    ))

    story.append(P("6. 단계별 결과", S["h1"]))
    story.append(P("6.1 전처리에서 확인된 자료의 성질", S["h2"]))
    story.append(P(
        "반응 분석에 들어가기 전, 월 패널에서 분석 창 끝의 극단 사건이 확인되었다. "
        "panel_qc.md에 따르면 2026-03 코스피 월수익률은 -21.18%(z=-3.07), "
        "2026-07은 -25.09%(z=-3.61), 2026-04는 +26.70%(z=+3.56)다. "
        "구간 표준편차는 2023–24년 4.58, 2026년 1–7월 22.03이다. "
        "환율·CCSI는 같은 배율로 흔들리지 않았다. 코스피 고유의 분산 급증이다. "
        "이 때문에 계획서에 kospi_ret_std와 2026 제외 표본을 강건성으로 넣었다.",
        S["body"],
    ))
    story.append(img(figs["vol"]))
    story.append(P("그림 3. 구간별 월 표준편차. 원본: monthly_panel.csv, 분석 창만.", S["caption"]))

    story.append(P("6.2 RQ1 — 국면은 나뉘는가", S["h2"]))
    story.append(P(
        "NMF 14토픽을 키워드 질량으로 접으면 국면별 토픽은 다음과 같다. "
        "AI반도체 [11], 가계대출 [10], 금리 [9], 대외통상 [12], 부동산 [2], "
        "증시실적 [1, 4, 6, 7, 13], 기타 [0, 3, 5, 8]. "
        "<b>물가는 매핑에서 빠진다.</b> 토픽 9의 상위 어휘에 물가·인플레이션과 금리·연준이 같이 나와 "
        "전량 NMF는 둘을 한 거시 축으로 붙인다. 질량 1위(금리)를 라벨로 썼다. "
        "검색 대분류의 물가는 뉴스 토픽에서 독립 축이 아니다.",
        S["body"],
    ))
    map_rows = [th("토픽", "국면", "출처", "질량 점유", "상위 어휘(일부)")]
    for _, row in tmap.sort_values("topic").iterrows():
        terms = str(row["top_terms"])
        if len(terms) > 42:
            terms = terms[:42] + "…"
        map_rows.append(cells(
            str(int(row["topic"])),
            str(row["regime"]),
            str(row["source"]),
            fmt_n(float(row["score_share"]), 3),
            terms,
        ))
    story.append(styled_table(map_rows, [16 * mm, 24 * mm, 22 * mm, 24 * mm, 84 * mm]))
    story.append(P("표 5. 토픽→국면 매핑. 원본: topic_regime_map.csv.", S["caption"]))

    cnt = joined["dominant_regime"].value_counts()
    cnt_rows = [th("국면", "z-우세 개월", "원비중 우세", "평균 비중(QC)", "피크 월(QC)")]
    peaks = {
        "물가": ("0", "0", "0.000", "2021-01"),
        "금리": ("10", "0", "0.077", "2022-09"),
        "부동산": ("15", "0", "0.074", "2021-12"),
        "가계대출": ("8", "0", "0.060", "2022-10"),
        "대외통상": ("11", "0", "0.107", "2025-04"),
        "AI반도체": ("13", "0", "0.075", "2026-06"),
        "증시실적": ("10", "67", "0.228", "2022-02"),
    }
    for name, vals in peaks.items():
        cnt_rows.append(cells(name, *vals))
    story.append(styled_table(cnt_rows, [32 * mm, 32 * mm, 32 * mm, 36 * mm, 38 * mm]))
    story.append(P("표 6. 월별 우세 국면. 평균 비중·피크는 regimes_qc.md 3절. 원비중 우세 67은 증시실적뿐이다.", S["caption"]))
    story.append(img(figs["counts"]))
    story.append(P("그림 4. z-우세 개월 수. 물가는 그룹이 만들어지지 않아 RQ3 비교에서 빠진다.", S["caption"]))
    story.append(img(figs["shares"]))
    story.append(P("그림 5. 국면 원비중. 증시실적(짙은 남색)이 전 구간에서 가장 크다. 이것이 z-우세를 택한 이유다.", S["caption"]))
    story.append(img(figs["timeline"]))
    story.append(P(
        f"그림 6. 월별 라벨. 최장 연속은 부동산 2021-02~08 (7개월). 국면이 긴 블록으로 뭉쳐 있지 않다 ({n_seg}개 구간).",
        S["caption"],
    ))
    story.append(P(
        "<b>RQ1 판정: 부분 성립.</b> 토픽은 해석 가능한 축으로 갈렸고, z-우세 라벨은 2022년 금리, "
        "2021년 부동산, 후반 AI반도체처럼 시기의 이슈 흐름과 대체로 맞는다. "
        "다만 (1) 물가 독립 축이 없고, (2) 원비중만으로는 국면이 한 가지로 붕괴하며, "
        f"(3) 라벨이 {n_seg}개 짧은 구간으로 갈라져 ‘안정적 블록’이라고 부르기는 어렵다. "
        "단일 라벨은 요약이고, 공존 이슈는 비중 벡터가 담는다.",
        S["body"],
    ))

    story.append(P("6.3 RQ2 — 전환은 잡히는가", S["h2"]))
    story.append(P(
        "PELT를 원비중에 그대로 씌우면 페널티가 손실보다 커 전환이 0건이었다. "
        "열별 z점수로 표준화한 뒤 같은 BIC 페널티를 썼다. 페널티 배율을 골라 2026년을 맞추지는 않았다. "
        "배율 ×1(본결과)에서 토픽 신호 3건, 국면 신호 4건이다.",
        S["body"],
    ))
    cp_rows = [th("신호", "전환월", "이전 → 이후", "이전 구간")]
    for _, r in d["cps"].iterrows():
        cp_rows.append(cells(str(r["signal"]), str(r["cp_month"]),
                             f"{r['from_label']} → {r['to_label']}",
                             f"{r['segment_start']}–{r['segment_end']}"))
    story.append(styled_table(cp_rows, [28 * mm, 28 * mm, 52 * mm, 62 * mm]))
    story.append(P("표 7. PELT 전환. 원본: changepoints.csv. 페널티 토픽 58.8657, 국면 29.4328.", S["caption"]))
    story.append(P(
        "2026-03과 2026-07은 토픽 신호·국면 신호 모두에서 잡히지 않았다. "
        "그달의 z-우세 라벨은 각각 대외통상, AI반도체다. "
        "시장 충격이 컸더라도 뉴스 국면 비중의 평균 구조가 3개월 이상 바뀌지 않으면 PELT는 전환으로 세지 않는다. "
        "계획서의 ‘타당성 확인’ 사건이지, 알고리즘이 그 달을 발견해야 하는 목표는 아니었다.",
        S["body"],
    ))
    story.append(P(
        "<b>RQ2 판정: 부분 성립.</b> 데이터 기반 전환 목록은 있다(국면 신호 4건: 2022-03, 2023-02, 2025-02, 2025-11). "
        "다만 전환이 7건(토픽 3+국면 4)뿐이라 이후 이벤트 스터디는 검정이 아니라 사례 기술이다. "
        "2026년 충격은 국면 전환으로 번역되지 않았다.",
        S["body"],
    ))

    story.append(P("6.4 RQ3 — 국면별로 반응이 다른가 (주가설)", S["h2"]))
    story.append(P(
        "사전 주가설은 국면 그룹 간에 코스피 수익률, 환율 변화, 소비자심리 차분의 분포가 다르다는 것이다. "
        "1순위 검정은 Kruskal–Wallis다. 2026년 코스피 분산이 앞 구간의 약 다섯 배라 "
        "정규·등분산을 전제하는 ANOVA는 액면대로 읽을 수 없다. "
        f"실제로 코스피 ANOVA p={exact(anova_kospi['p_value'])}로 0.05보다 작지만, "
        f"Levene(Brown–Forsythe) p={exact(lev_kospi['p_value'])}로 등분산이 기각된다. "
        "계획대로 KW를 1순위로 둔다.",
        S["body"],
    ))
    story.append(img(figs["kw"]))
    story.append(P("그림 7. KW p값. 점선은 α=0.05. 주 3개(코스피·환율·CCSI)는 선 오른쪽, 기준금리만 왼쪽.", S["caption"]))

    kw_tbl = [th("종속변수", "H", "p", "ε²", "α=0.05 판정")]
    for dep, lab in [
        ("kospi_ret", "코스피 수익률"),
        ("usdkrw_ret", "환율 변화"),
        ("ccsi_diff", "CCSI 차분"),
        ("cpi_mom", "CPI 전월비"),
        ("base_rate_diff", "기준금리 차분"),
        ("kospi_ret_std", "코스피(표준화)"),
    ]:
        row = kw_row(dep)
        verdict = "다름 (유의)" if row["p_value"] < ALPHA else "같다고 볼 수 없음"
        kw_tbl.append(cells(
            lab,
            exact(row["statistic"]),
            exact(row["p_value"]),
            exact(row["effect"]),
            verdict,
        ))
    story.append(styled_table(kw_tbl, [36 * mm, 32 * mm, 42 * mm, 28 * mm, 32 * mm]))
    story.append(P("표 8. Kruskal–Wallis. 원본: regime_tests.csv. p는 CSV 원값.", S["caption"]))

    story.append(P(
        f"Holm 보정 후 국면쌍 Mann–Whitney에서 p&lt;0.05인 쌍은 <b>0/60</b>이다. "
        f"즉 6개 국면을 서로 짝지어 보아도, 다중비교를 통제하면 어느 한 쌍도 주 종속변수에서 갈리지 않는다.",
        S["body"],
    ))
    story.append(img(figs["means"]))
    story.append(P("그림 8. 국면별 평균. 점선은 67개월 전체 평균. 수준 차이와 검정 결과는 별개다.", S["caption"]))
    story.append(img(figs["kospi_sd"]))
    story.append(P(
        f"그림 9. 코스피 평균 ±1 표준편차. 금리 국면 평균 {exact(kospi_rates['mean'])} (n=10), "
        f"AI반도체 {exact(kospi_ai['mean'])} (n=13), 전체 {exact(kospi_all['mean'])}. "
        f"AI반도체 표준편차 {exact(kospi_ai['sd'])}로 그룹 안 흩어짐이 크다.",
        S["caption"],
    ))
    story.append(img(figs["box"]))
    story.append(P("그림 10. 코스피 월수익률 상자그림. 원본: monthly_panel.csv × dominant_regime.", S["caption"]))

    # reaction table kospi
    ksub = react[(react["dep_var"] == "kospi_ret")].copy()
    rt = [th("국면", "n", "평균", "표준편차", "중위수", "전체평균 차")]
    for _, r in ksub.iterrows():
        rt.append(cells(r["regime"], str(int(r["n"])), fmt_n(r["mean"], 3), fmt_n(r["sd"], 3), fmt_n(r["median"], 3), fmt_n(r["mean_minus_overall"], 3)))
    story.append(styled_table(rt, [28 * mm, 18 * mm, 28 * mm, 28 * mm, 28 * mm, 40 * mm]))
    story.append(P("표 9. 코스피 국면별 기술통계. 원본: regime_reaction.csv.", S["caption"]))

    story.append(P("보조 분석: 비중 회귀와 더미 회귀", S["h3"]))
    story.append(P(
        "단일 라벨은 1위 축만 남긴다. 비중 z를 회귀에 넣으면 공존 이슈가 남는다. "
        f"코스피 비중 회귀의 R²는 0.071(수정 R² -0.022, F p=0.3159)로 설명력이 없다. "
        f"다만 CCSI 회귀에서 금리 비중(share_rates) 계수는 {exact(share_ccsi_rates['coef'])}, "
        f"p={exact(share_ccsi_rates['p_value'])}로 0.05보다 작다. "
        "금리 뉴스가 상대적으로 커진 달에 소비자심리가 같이 낮아지는 방향이다. 인과로 읽지 않는다.",
        S["body"],
    ))
    story.append(P(
        f"국면 더미+통제(기준=부동산, 통제=기준금리 차분·CPI 전월비)에서 "
        f"코스피의 금리 더미 계수는 {exact(dummy_rates['coef'])}, p={exact(dummy_rates['p_value'])}다. "
        f"CCSI의 가계대출 더미는 {exact(dummy_hh['coef'])}, p={exact(dummy_hh['p_value'])}다. "
        "이는 ‘부동산 달 대비 차이’이지 KW의 전체 그룹 검정을 뒤집지 않는다. "
        "관측치 67에 더미 5+통제라 포화 설계는 본결과로 올리지 않았다. "
        f"코스피 더미 회귀 R²=0.167, 수정 R²=0.068.",
        S["body"],
    ))
    story.append(P(
        f"전환 이벤트 스터디는 국면 신호 4건의 ±3개월 경로다. 표본이 아니므로 검정하지 않는다. "
        f"비전환월로 만든 |사후-사전| 분포에서 분위 0.90 이상인 경우는 28건 중 4건이다 "
        f"(2022-02 kospi_ret_std, 2023-02 usdkrw_ret, 2025-02 ccsi_diff, 2025-11 kospi_ret). "
        f"2025-11 대외통상→AI반도체의 코스피 사후-사전은 분위 1.00이다. 사례로만 적는다.",
        S["body"],
    ))
    story.append(img(figs["event"]))
    story.append(P("그림 11. 국면 신호 전환 전후 코스피. 원본: event_study.csv. n=4라 일반화하지 않는다.", S["caption"]))
    story.append(P(
        f"Ljung–Box(시차 3)에서 kospi_ret p=0.0393, base_rate_diff p=0.0000, kospi_ret_std p=0.0240이다. "
        "월 관측이 독립이라는 KW 전제는 코스피·금리에서 완전하지 않다. p가 낙관적일 수 있다.",
        S["body"],
    ))
    story.append(P(
        "<b>RQ3 주가설 판정: 성립하지 않음.</b> 코스피·환율·CCSI에 대해 국면 6그룹 분포 차이를 KW로 주장할 수 없다. "
        "기술 통계의 평균 간격(금리 음, AI반도체 양)은 있으나, 분산과 표본 개월(국면당 8–15)을 반영하면 유의하지 않다. "
        "<b>보조적으로 성립하는 부분:</b> 기준금리 차분 KW는 유의하고, 더미 회귀의 금리 계수·CCSI 비중 회귀의 금리 항은 0.05보다 작다. "
        "계획서의 실패 조항—“차이가 일관되게 없으면 연결이 약하다는 결과로 정리”—을 따른다.",
        S["body"],
    ))

    story.append(P("6.5 강건성 — 2026년을 빼도 같은가", S["h2"]))
    story.append(P(
        "2026-01 이후 7개월을 빼면 60개월이 남는다. AI반도체 개월은 13→7, 대외통상은 11→10이다. "
        "유의 여부(p&lt;0.05)가 뒤집힌 종속변수는 없다.",
        S["body"],
    ))
    rb = [th("종속변수", "p 전체(67)", "p 2026제외(60)", "유의 전체", "유의 제외", "뒤집힘")]
    labmap = {
        "kospi_ret": "코스피", "usdkrw_ret": "환율", "ccsi_diff": "CCSI",
        "cpi_mom": "CPI 전월비", "base_rate_diff": "기준금리", "kospi_ret_std": "코스피(표준화)",
    }
    for _, r in robust.iterrows():
        rb.append(cells(
            labmap.get(r["dep_var"], r["dep_var"]),
            exact(r["p_full"]), exact(r["p_no2026"]),
            "예" if bool(r["sig_full"]) else "아니오",
            "예" if bool(r["sig_no2026"]) else "아니오",
            "예" if bool(r["flipped"]) else "아니오",
        ))
    story.append(styled_table(rb, [32 * mm, 32 * mm, 36 * mm, 22 * mm, 22 * mm, 22 * mm]))
    story.append(P("표 10. 강건성 KW 비교. 원본: robustness_compare.csv.", S["caption"]))
    story.append(img(figs["robust"]))
    story.append(P(
        f"그림 12. 전체 vs 2026 제외 p값. 코스피 p는 {exact(robust.loc[robust['dep_var']=='kospi_ret','p_full'].iloc[0])} → "
        f"{exact(robust.loc[robust['dep_var']=='kospi_ret','p_no2026'].iloc[0])}로 더 커진다. "
        "주가설이 2026 충격 때문에 기각된 것은 아니다.",
        S["caption"],
    ))

    story.append(P("6.6 RQ4 — 검색은 뉴스 국면을 보조하는가", S["h2"]))
    story.append(P(
        "검색은 국면을 다시 만들지 않는다. 뉴스에서 이미 정한 7축과 같은 이름의 데이터랩 대분류가 "
        "같이 움직이는지만 본다. 물가는 뉴스 비중 분산이 0이라 상관을 정의할 수 없다. "
        "검색 물가 축 자체는 2026-03에 급등한다(score_rel 154.25, 앵커 z -0.56, 정규화 오류 아님). "
        "뉴스가 못 나눈 관심도의 보조 신호로만 적는다.",
        S["body"],
    ))
    cq = [th("국면", "Pearson r (검색 z)", "Spearman", "읽기")]
    read_map = {
        "물가": "상관 없음 (뉴스 분산 0)",
        "금리": "중등 양의 상관 — 가설과 맞음",
        "부동산": "중등 양의 상관 — 가설과 맞음",
        "가계대출": "중등 양의 상관 — 가설과 맞음",
        "대외통상": "약한–중등 상관",
        "AI반도체": "강한 양의 상관 — 가설과 가장 맞음",
        "증시실적": "거의 없음 — 가설과 안 맞음",
    }
    for _, r in pearson_z.iterrows():
        pr = "—" if r["pearson"] != r["pearson"] else exact(r["pearson"])
        sp = "—" if r["spearman"] != r["spearman"] else exact(r["spearman"])
        cq.append(cells(r["regime"], pr, sp, read_map.get(r["regime"], "")))
    story.append(styled_table(cq, [28 * mm, 42 * mm, 32 * mm, 68 * mm]))
    story.append(P("표 11. 뉴스 비중 vs 검색 z. 원본: rq4_corr.csv. n=67.", S["caption"]))
    story.append(img(figs["rq4c"]))
    story.append(P("그림 13. 축별 Pearson r. 물가는 분산 0이라 막대를 그리지 않고 0으로 표시했다.", S["caption"]))
    story.append(img(figs["rq4s"]))
    story.append(P("그림 14. 같은 자료의 산점도. 왼쪽은 가설과 맞는 축, 오른쪽은 약한 축.", S["caption"]))
    story.append(img(figs["conc"]))
    story.append(P(
        f"그림 15. 라벨 일치율. 검색 z argmax와 뉴스 z-우세가 같은 달은 {int(zrow['match'])}/{int(zrow['n'])} = "
        f"{exact(zrow['match_rate'])}. 7국면 균등 무작위는 1/7≈0.1429. 이보다 높으므로 "
        "검색이 뉴스 라벨을 보조한다고 읽을 여지는 있다. 검색 선행(한 달 앞) 일치는 18/66이다.",
        S["caption"],
    ))
    story.append(P(
        "<b>RQ4 판정: 부분 성립.</b> AI반도체(r=0.7505857678829452), 부동산(0.5582036473886888), "
        "금리(0.524986317017003)는 뉴스와 검색이 같이 움직인다. 증시실적(0.11345264061465014)은 그렇지 않다. "
        "경제지에서 증시 기사는 상시 많고, 검색의 증시 관심은 급등기에 몰리기 쉬운 구조 차이다. "
        "이 해석은 메커니즘 가설이며 이 산출만으로 증명한 것은 아니다. "
        "검색 결과는 본분석 국면을 폐기할 이유가 되지 않는다.",
        S["body"],
    ))

    story.append(P("6.7 폴백 모형 — 알고리즘을 바꾸면 주가설이 살아나는가", S["h2"]))
    story.append(P(
        "폴백 트리거는 주 종속 3개 KW가 모두 p≥0.05일 때다. 발동했다 "
        f"(kospi {exact(kospi_kw['p_value'])}, usdkrw {exact(fx_kw['p_value'])}, ccsi {exact(ccsi_kw['p_value'])}). "
        "같은 doc_term.npz에 online LDA(14토픽, 표본 201,000, seed 42, max_iter 15)를 적합했다. "
        "행렬 sha256는 NMF와 동일하다. 매핑 규칙은 같되 토픽 번호가 달라 NMF의 토픽 3 수동 덮어쓰기는 넣지 않았다.",
        S["body"],
    ))
    story.append(P(
        "LDA는 물가·금리·가계대출을 매핑하지 못했다. z-우세는 부동산 17, 대외통상 18, AI반도체 14, 증시실적 18개월 "
        "(4그룹). 본분석의 6국면 질문이 아니다.",
        S["body"],
    ))
    story.append(img(figs["nmflda"]))
    story.append(P(
        f"그림 16. NMF vs LDA KW p. LDA 코스피 H={exact(lda_kospi['statistic'])}, p={exact(lda_kospi['p_value'])}. "
        f"환율 p={exact(lda_fx['p_value'])}, CCSI p={exact(lda_ccsi['p_value'])}로 주 3개 중 코스피만 유의하다. "
        "기준금리는 LDA에서 축이 사라져 KW가 유의하지 않다(p=0.84298327496376).",
        S["caption"],
    ))
    story.append(P(
        "LDA에서 Holm 보정 후 p&lt;0.05인 쌍은 세 개다. "
        "코스피: 대외통상 vs AI반도체 (Holm p=0.013371756365302835), "
        "대외통상 vs 증시실적 (0.04960856042332564). "
        "표준화 코스피: 대외통상 vs AI반도체 (0.017184092557171876). "
        "대외통상 그룹의 코스피 평균이 +6.916, AI반도체는 -2.582다. "
        "NMF에서 AI반도체가 높았던 것과 방향이 다르다. 라벨 구성이 다르기 때문이며, "
        "같은 이름의 국면을 같은 실체로 읽으면 안 된다.",
        S["body"],
    ))
    story.append(P(
        "BERTopic은 별도 명령으로 돌렸다. 월 1,000건 층화표본 67,000건, 임베딩 "
        "paraphrase-multilingual-MiniLM-L12-v2, 요청 토픽 14. HDBSCAN은 토픽 6개(+이상치 48)만 남겼다. "
        "같은 키워드 질량 매핑에서 5토픽이 증시실적, 1토픽이 기타. z-우세는 67개월 전부 증시실적. "
        "그룹이 1개라 KW는 정의되지 않는다. 전량 변환이 아닌 표본 시계열이다. "
        "이 설정에서 BERTopic은 NMF 6국면을 재현하지 못했다. "
        "“다른 알고리즘을 써도 RQ3는 약하다”의 근거로 쓰지 않는다.",
        S["body"],
    ))

    story.append(P("7. 가설과 결과의 대응 종합", S["h1"]))
    hyp = [
        th("사전 주장", "판정", "근거 (산출)"),
        cells("뉴스 토픽으로 이슈 국면을 나눌 수 있다 (RQ1)", "부분 성립",
              "6개 해석 가능 축. 물가 없음. 원비중은 붕괴. 33개 짧은 구간."),
        cells("전환 시점을 탐지할 수 있다 (RQ2)", "부분 성립",
              "국면 PELT 4건. 2026-03·07 미탐지. 이벤트는 사례."),
        cells("국면별 코스피 반응이 다르다 (RQ3)", "성립하지 않음",
              f"KW p={kospi_kw['p_value']:.6f}, Holm 0/60. 2026 제외 p=0.3043."),
        cells("국면별 환율 반응이 다르다 (RQ3)", "성립하지 않음",
              f"KW p={fx_kw['p_value']:.6f}. 2026 제외에서도 비유의."),
        cells("국면별 CCSI 반응이 다르다 (RQ3)", "성립하지 않음",
              f"KW p={ccsi_kw['p_value']:.6f}. Holm 유의 쌍 없음."),
        cells("기준금리 변화는 국면과 같이 움직인다", "성립 (사후)",
              f"KW p={rate_kw['p_value']:.6f}. 2026 제외 p=0.0237, 뒤집힘 없음."),
        cells("검색이 뉴스 국면을 보조한다 (RQ4)", "부분 성립",
              "AI·부동산·금리 상관. 일치 22/67. 증시실적 r=0.113. 물가 비교 불가."),
        cells("토픽 모형을 바꾸면 RQ3가 살아난다", "대체 불가",
              "LDA는 4축·코스피만 유의, 방향이 NMF와 다름. BERTopic은 1그룹."),
    ]
    story.append(styled_table(hyp, [52 * mm, 28 * mm, 90 * mm]))
    story.append(P("표 12. 가설–결과 대응. p의 전체 자릿수는 해당 CSV.", S["caption"]))
    story.append(P(
        "기술 통계만 보면 금리 국면의 코스피 평균이 낮고 AI반도체 국면이 높다. "
        "그 간격을 ‘국면 효과’로 적고 싶지만, 본 연구의 사전 검정은 그 간격을 우연 이상으로 보지 않았다. "
        "평균의 방향과 검정의 비유의는 동시에 보고하는 것이 맞다. 한쪽만 고르면 결과가 좋아 보인다.",
        S["body"],
    ))

    story.append(P("8. 한계", S["h1"]))
    lim = [
        th("한계", "내용", "이 연구가 한 대응"),
        cells("경제지 3사", "종합지·방송·통신이 없다. 이슈 구성이 시장·산업 쪽에 기울 수 있다.",
              "범위를 ‘경제지 기준’으로 명시. 매체를 늘리지 않기로 함."),
        cells("본문 200자 절삭", "내보내기 본문을 토픽에 쓸 수 없다.", "키워드 컬럼을 입력으로 사용."),
        cells("물가 축 부재", "뉴스 NMF가 물가와 금리를 한 토픽에 붙인다.",
              "라벨 0개월로 비교에서 자연 탈락. 검색 물가는 보조 신호로만."),
        cells("단일 라벨의 거친 요약", "한 달에 이슈가 공존한다. 라벨은 33개 구간으로 잘린다.",
              "비중 벡터 회귀를 병행. 라벨만으로 반응을 단정하지 않음."),
        cells("2026 분산 급증", "마지막 7개월이 코스피 계수를 지배할 수 있다.",
              "kospi_ret_std, 2026 제외. 주가설 판정은 뒤집히지 않음."),
        cells("인과 식별 불가", "뉴스는 사후 보도일 수 있다. 국면이 지표를 움직였다고 말할 수 없다.",
              "동시 움직임·패턴 차이만 보고. 이벤트는 사례."),
        cells("소표본 월", "67개월, 국면당 8–15. KW 검정력이 낮다.",
              "비유의 = ‘차이 없음의 증명’이 아님. 다만 주장을 지탱하지는 못함."),
        cells("감성 미사용", "ENSI/NSI와 직접 비교하지 않았다.", "합의된 범위 밖. 후속 과제."),
        cells("자기상관", "코스피·기준금리 Ljung–Box가 유의.", "HAC 회귀. KW p는 낙관적일 수 있음."),
    ]
    story.append(styled_table(lim, [32 * mm, 72 * mm, 66 * mm]))
    story.append(P("표 13. 한계. 계획서 6절 및 각 QC 주장 범위.", S["caption"]))

    story.append(P("9. 종합", S["h1"]))
    story.append(P(
        "경제 뉴스의 토픽 비중으로 <b>이슈의 상대적 부상</b>을 월 단위 라벨로 요약하는 파이프라인은 작동했다. "
        "금리 긴축기, 부동산, 후반 AI·반도체처럼 시기에 대응하는 축이 나왔고, "
        "검색은 그 중 여러 축에서 같은 방향으로 움직였다. "
        "국면 전환 목록도 데이터로 남는다.",
        S["body"],
    ))
    story.append(P(
        "그러나 그 라벨을 가지고 <b>코스피·환율·소비자심리가 국면마다 다르다</b>고 말하기에는 "
        "증거가 부족하다. 1순위 검정은 주 3개 변수에서 기각에 실패했고, "
        "쌍비교 보정 후에는 유의 쌍이 없으며, 2026년을 빼도 같다. "
        "평균이 벌어져 보이는 자리(금리 vs AI반도체)는 분산이 함께 크다. "
        "기준금리 차분만이 그룹 차이를 일관되게 보여 준다.",
        S["body"],
    ))
    story.append(P(
        "따라서 현재 자료와 사전 설계 기준으로 내릴 수 있는 결론은 다음이다. "
        "<b>한국 경제지 뉴스에서 이슈 국면은 식별 가능하나, 그 국면 라벨과 월별 시장·심리 반응의 연결은 약하다.</b> "
        "이 문장은 실패의 은폐가 아니라 계획서가 예정한 정리 방식이다. "
        "LDA에서 코스피 KW가 유의하게 나온 것은 축이 4개로 줄고 라벨 구성이 바뀐 비교 결과이며, 본분석을 대체하지 않는다.",
        S["body"],
    ))
    story.append(P(
        "재현 명령: <font face='Malgun'>python -m analysis.run_pipeline</font> "
        "(반응·강건성·RQ4·조건부 LDA). 국면 시계열은 이미 있는 NMF 산출을 쓴다. "
        "이 보고서: <font face='Malgun'>python -m analysis.build_results_report</font>.",
        S["note"],
    ))
    story.append(Spacer(1, 6 * mm))
    src = [
        th("장", "원본"),
        cells("국면·전환", "data/processed/regimes/regime_monthly.csv, changepoints.csv, regimes_qc.md"),
        cells("RQ3 반응", "data/processed/reactions/regime_reaction.csv, regime_tests.csv, reactions_qc.md"),
        cells("회귀·이벤트", "regime_regression.csv, share_regression.csv, event_study_summary.csv"),
        cells("강건성", "robustness_compare.csv, robustness_qc.md"),
        cells("RQ4", "rq4_corr.csv, rq4_concordance.csv, rq4_qc.md"),
        cells("폴백", "regimes_lda/, reactions_lda/, regimes_bertopic/"),
        cells("설계", "docs/연구_쉬운_요약.md, docs/기술_참고.md, docs/research_plan.md, docs/results.md"),
    ]
    story.append(styled_table(src, [32 * mm, 138 * mm]))
    story.append(P("표 14. 수치의 출처. 본 보고서의 모든 검정 통계량은 위 파일을 다시 읽었다.", S["caption"]))
    return story


def build_pdf(d: dict, figs: dict[str, Path]) -> Path:
    register_fonts()
    S = styles()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="한국형 경제 이슈 국면 탐지 연구 결과 보고서",
        author="DataMining",
    )
    story = build_story(d, figs, S)
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    return PDF_PATH


def main() -> None:
    d = load_data()
    figs = make_figures(d)
    path = build_pdf(d, figs)
    print(f"wrote {path}")
    print(f"figures {FIG_DIR}")


if __name__ == "__main__":
    main()
