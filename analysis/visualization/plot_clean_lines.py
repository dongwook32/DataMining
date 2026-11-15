"""5대 지표별 8대 국면 선형 그래프 고해상도 시각화 스크립트.

특징:
- 오직 선(Line)으로만 구성
- 경제지표는 굵은 검은색 실선으로 뚜렷하게 중심
- 8대 국면은 서로 명확히 구분되는 8가지 고유 색상 선
- 우측에 깔끔한 범례 표시
- docs/figures/fig_clean_line_1~5.png 생성
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from config import project_root

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
FIG_DIR = ROOT / "docs" / "figures"

REGIME_COLORS = [
    ("macro", "금리·물가", "#e41a1c"),      # 빨강
    ("realestate", "부동산", "#ff7f00"),     # 주황
    ("hhdebt", "가계대출", "#a65628"),       # 갈색
    ("trade", "대외통상", "#984ea3"),       # 보라
    ("aichip", "AI반도체", "#377eb8"),      # 파랑
    ("market", "시황", "#4daf4a"),          # 초록
    ("earnings", "기업실적", "#17becf"),    # 청록
    ("capital", "자본거래", "#f781bf"),     # 분홍
]

INDICATORS = [
    ("KOSPI", "fig_clean_line_1_kospi", "코스피(KOSPI) 주가지수", "pt"),
    ("cpi_yoy", "fig_clean_line_2_cpi", "소비자물가 상승률(CPI YoY)", "%"),
    ("BASE_RATE", "fig_clean_line_3_baserate", "한국은행 기준금리", "%"),
    ("USD_KRW", "fig_clean_line_4_usdkrw", "원/달러 환율(USD/KRW)", "원"),
    ("CCSI", "fig_clean_line_5_ccsi", "소비자심리지수(CCSI)", "pt"),
]


def setup_matplotlib():
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 10.5


def plot_clean():
    setup_matplotlib()
    panel = pd.read_csv(PANEL_PATH)
    regime = pd.read_csv(REGIME_PATH)

    df_p = panel[(panel["month"] >= "2021-01") & (panel["month"] <= "2026-07")].copy()
    df_r = regime[(regime["month"] >= "2021-01") & (regime["month"] <= "2026-07")].copy()

    for slug, _, _ in REGIME_COLORS:
        sh = df_r[f"share_{slug}"]
        mean = sh.mean()
        std = sh.std(ddof=0)
        df_r[f"z_{slug}"] = (sh - mean) / std

    df = pd.merge(df_p, df_r, on="month").sort_values("month").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["month"] + "-01")
    dates = df["date"]

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    for key, fname, title, unit in INDICATORS:
        fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)

        # 연도별 구분선
        for y in [2021, 2022, 2023, 2024, 2025, 2026]:
            ax1.axvline(pd.to_datetime(f"{y}-01-01"), color="#e0e0e0", linestyle="--", linewidth=1.0, zorder=1)

        # 왼쪽 축: 경제지표 (굵은 검정 실선)
        line_ind = ax1.plot(dates, df[key], color="#111111", linewidth=3.2, label=f"★ {title} ({unit})", zorder=5)
        ax1.set_ylabel(f"{title} ({unit})", fontsize=11, fontweight="bold", color="#111111")
        ax1.grid(True, linestyle=":", alpha=0.5, zorder=1)

        # 오른쪽 축: 8대 국면 z-score (8개 색상 선)
        ax2 = ax1.twinx()
        lines_reg = []
        for slug, name, color in REGIME_COLORS:
            (l,) = ax2.plot(dates, df[f"z_{slug}"], color=color, linewidth=1.7, alpha=0.85, label=f"{name} (z-score)", zorder=3)
            lines_reg.append(l)

        ax2.axhline(0.5, color="gray", linestyle=":", linewidth=1.0, alpha=0.7)  # 활성화 기준선 0.5
        ax2.set_ylabel("8대 국면 표준화점수 (z-score)", fontsize=11, fontweight="bold", color="#444444")
        ax2.set_ylim(-2.5, 4.0)

        # X축 날짜 포맷
        ax1.xaxis.set_major_locator(mdates.YearLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y년"))
        ax1.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
        ax1.xaxis.set_minor_formatter(mdates.DateFormatter("%m월"))
        ax1.tick_params(axis="x", which="major", pad=12, labelsize=10.5)
        ax1.tick_params(axis="x", which="minor", labelsize=8, colors="gray")

        # 범례 합치기
        all_lines = line_ind + lines_reg
        labels = [l.get_label() for l in all_lines]
        ax1.legend(all_lines, labels, loc="upper left", bbox_to_anchor=(1.08, 1.0), framealpha=0.95, fontsize=9.5)

        plt.title(f"{title} vs 8대 국면 전체 시계열 선형 비교 (2021~2026)", fontsize=13, fontweight="bold", pad=15)
        fig.tight_layout()

        png_p = FIG_DIR / f"{fname}.png"
        fig.savefig(png_p, bbox_inches="tight")
        plt.close(fig)
        print(f"생성 완료: {png_p.name}")


if __name__ == "__main__":
    plot_clean()
