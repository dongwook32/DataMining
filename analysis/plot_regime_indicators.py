"""ECOS 거시경제 지표 5종과 국면 시계열의 구간 일치도 비교 시각화 스크립트.

지표 5종:
1. 기준금리 (BASE_RATE) & CPI vs [금리·물가], [가계대출]
2. 코스피 지수 (KOSPI) vs [시황], [AI반도체], [기업실적], [자본거래]
3. 원/달러 환율 (USD_KRW) vs [대외통상], [시황]
4. 소비자심리지수 (CCSI) vs [금리·물가], [가계대출], [부동산]
5. 소비자물가지수 (CPI YoY) vs [금리·물가]
+ 5개 패널 종합 비교 그래프 (fig_overview_5panel)

산출: docs/figures/ 내 PNG (300 DPI) 및 PDF
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from config import load_config, project_root

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
FIG_DIR = ROOT / "docs" / "figures"


def setup_matplotlib():
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 10
    plt.rcParams["figure.titlesize"] = 14
    plt.rcParams["axes.titlesize"] = 12
    plt.rcParams["axes.labelsize"] = 11


setup_matplotlib()


def load_merged_data() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_PATH)
    regimes = pd.read_csv(REGIME_PATH)
    df = regimes.merge(panel, on="month", how="inner")
    df["date"] = pd.to_datetime(df["month"] + "-01")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def highlight_active_regime(ax, dates, active_series, color, label=None, alpha=0.2):
    """활성화된 구간(1)에 반투명 수직 음영 추가."""
    in_block = False
    start_idx = 0
    plotted_label = False
    for i in range(len(dates)):
        if active_series.iloc[i] == 1 and not in_block:
            in_block = True
            start_idx = i
        elif active_series.iloc[i] == 0 and in_block:
            in_block = False
            lbl = label if not plotted_label else None
            ax.axvspan(
                dates.iloc[start_idx] - pd.Timedelta(days=15),
                dates.iloc[i - 1] + pd.Timedelta(days=15),
                color=color,
                alpha=alpha,
                label=lbl,
                zorder=1,
            )
            if lbl:
                plotted_label = True
    if in_block:
        lbl = label if not plotted_label else None
        ax.axvspan(
            dates.iloc[start_idx] - pd.Timedelta(days=15),
            dates.iloc[-1] + pd.Timedelta(days=15),
            color=color,
            alpha=alpha,
            label=lbl,
            zorder=1,
        )


def plot_fig1_baserate(df: pd.DataFrame):
    """1. 기준금리 vs [금리·물가] 및 [가계대출]."""
    fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)
    setup_matplotlib()

    dates = df["date"]
    highlight_active_regime(ax1, dates, df["active_macro"], color="crimson", label="[금리·물가] 활성 (z>=0.5)", alpha=0.18)
    highlight_active_regime(ax1, dates, df["active_hhdebt"], color="darkorange", label="[가계대출] 활성 (z>=0.5)", alpha=0.15)

    # 기준금리 선
    line1 = ax1.plot(dates, df["BASE_RATE"], color="black", linewidth=2.5, marker="o", markersize=4, label="한국은행 기준금리 (%)", zorder=4)
    ax1.set_ylabel("기준금리 (%)", color="black", fontweight="bold")
    ax1.set_ylim(0, 4.2)
    ax1.grid(True, linestyle="--", alpha=0.5, zorder=2)

    # 보조축: 금리·물가 비중
    ax2 = ax1.twinx()
    line2 = ax2.plot(dates, df["share_macro"] * 100, color="crimson", linestyle=":", linewidth=1.8, label="[금리·물가] 뉴스 비중 (%)", zorder=3)
    ax2.set_ylabel("[금리·물가] 기사 비중 (%)", color="crimson")
    ax2.set_ylim(4, 14)

    # 범례 합치기
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    h1, l1 = ax1.get_legend_handles_labels()
    ax1.legend(h1 + lines, l1 + labels, loc="upper left", framealpha=0.9)

    ax1.set_title("한국은행 기준금리 추이와 [금리·물가] 및 [가계대출] 국면 활성 구간 대조 (2021~2026)", pad=15)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=0)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_baserate_vs_macro.png")
    fig.savefig(FIG_DIR / "fig1_baserate_vs_macro.pdf")
    plt.close(fig)


def plot_fig2_kospi(df: pd.DataFrame):
    """2. 코스피 지수 vs 주식 관련 4대 국면."""
    fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)
    setup_matplotlib()

    dates = df["date"]
    highlight_active_regime(ax1, dates, df["active_market"], color="red", label="[시황] 활성", alpha=0.15)
    highlight_active_regime(ax1, dates, df["active_aichip"], color="blue", label="[AI반도체] 활성", alpha=0.18)
    highlight_active_regime(ax1, dates, df["active_capital"], color="purple", label="[자본거래] 활성", alpha=0.15)

    line1 = ax1.plot(dates, df["KOSPI"], color="black", linewidth=2.5, label="코스피 지수 (KOSPI)", zorder=4)
    ax1.set_ylabel("KOSPI 지수", color="black", fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5, zorder=2)

    ax1.legend(loc="upper left", framealpha=0.9)
    ax1.set_title("KOSPI 지수 추이와 주식·기술 국면 활성 구간 대조 (시황·AI반도체·자본거래)", pad=15)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_kospi_vs_equity_regimes.png")
    fig.savefig(FIG_DIR / "fig2_kospi_vs_equity_regimes.pdf")
    plt.close(fig)


def plot_fig3_usdkrw(df: pd.DataFrame):
    """3. 원/달러 환율 vs [대외통상]."""
    fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)
    setup_matplotlib()

    dates = df["date"]
    highlight_active_regime(ax1, dates, df["active_trade"], color="seagreen", label="[대외통상] 활성 (z>=0.5)", alpha=0.22)

    line1 = ax1.plot(dates, df["USD_KRW"], color="navy", linewidth=2.5, marker="s", markersize=3.5, label="원/달러 환율 (원)", zorder=4)
    ax1.set_ylabel("USD/KRW 환율 (원)", color="navy", fontweight="bold")
    ax1.set_ylim(1050, 1600)
    ax1.grid(True, linestyle="--", alpha=0.5, zorder=2)

    ax2 = ax1.twinx()
    line2 = ax2.plot(dates, df["share_trade"] * 100, color="seagreen", linestyle="--", linewidth=1.8, label="[대외통상] 뉴스 비중 (%)", zorder=3)
    ax2.set_ylabel("[대외통상] 기사 비중 (%)", color="seagreen")
    ax2.set_ylim(7, 15)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    h1, l1 = ax1.get_legend_handles_labels()
    ax1.legend(h1 + lines, l1 + labels, loc="upper left", framealpha=0.9)

    ax1.set_title("원/달러 환율 추이와 [대외통상] 국면 활성 구간 대조 (2021~2026)", pad=15)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_usdkrw_vs_trade.png")
    fig.savefig(FIG_DIR / "fig3_usdkrw_vs_trade.pdf")
    plt.close(fig)


def plot_fig4_ccsi(df: pd.DataFrame):
    """4. 소비자심리지수 (CCSI) vs [금리·물가] 및 [가계대출]."""
    fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)
    setup_matplotlib()

    dates = df["date"]
    highlight_active_regime(ax1, dates, df["active_macro"], color="crimson", label="[금리·물가] 활성", alpha=0.18)
    highlight_active_regime(ax1, dates, df["active_hhdebt"], color="darkorange", label="[가계대출] 활성", alpha=0.15)

    # CCSI 기준선 100 (낙관/비관 분기점)
    ax1.axhline(100, color="gray", linestyle="--", linewidth=1.5, label="기준선 100 (비관/낙관 분기점)", zorder=3)
    line1 = ax1.plot(dates, df["CCSI"], color="teal", linewidth=2.5, marker="^", markersize=4, label="소비자심리지수 (CCSI)", zorder=4)

    ax1.set_ylabel("소비자심리지수 (CCSI)", color="teal", fontweight="bold")
    ax1.set_ylim(75, 115)
    ax1.grid(True, linestyle="--", alpha=0.5, zorder=2)

    ax1.legend(loc="lower left", framealpha=0.9)
    ax1.set_title("소비자심리지수(CCSI) 추이와 거시·부채 국면 활성 구간 대조 (금리·물가 및 가계대출)", pad=15)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig4_ccsi_vs_living_regimes.png")
    fig.savefig(FIG_DIR / "fig4_ccsi_vs_living_regimes.pdf")
    plt.close(fig)


def plot_fig5_cpi(df: pd.DataFrame):
    """5. 소비자물가지수 (CPI YoY) vs [금리·물가]."""
    fig, ax1 = plt.subplots(figsize=(11, 5.5), dpi=300)
    setup_matplotlib()

    dates = df["date"]
    highlight_active_regime(ax1, dates, df["active_macro"], color="crimson", label="[금리·물가] 활성 (z>=0.5)", alpha=0.22)

    line1 = ax1.plot(dates, df["cpi_yoy"], color="firebrick", linewidth=2.5, marker="o", markersize=4, label="소비자물가 상승률 (CPI YoY, %)", zorder=4)
    ax1.set_ylabel("CPI 상승률 (전년동월대비, %)", color="firebrick", fontweight="bold")
    ax1.set_ylim(0, 7.0)
    ax1.grid(True, linestyle="--", alpha=0.5, zorder=2)

    ax2 = ax1.twinx()
    line2 = ax2.plot(dates, df["share_macro"] * 100, color="crimson", linestyle=":", linewidth=1.8, label="[금리·물가] 기사 비중 (%)", zorder=3)
    ax2.set_ylabel("[금리·물가] 기사 비중 (%)", color="crimson")
    ax2.set_ylim(4, 14)

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    h1, l1 = ax1.get_legend_handles_labels()
    ax1.legend(h1 + lines, l1 + labels, loc="upper left", framealpha=0.9)

    ax1.set_title("소비자물가 상승률(CPI YoY) 추이와 [금리·물가] 국면 활성 구간 대조 (2021~2026)", pad=15)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig5_cpi_vs_macro.png")
    fig.savefig(FIG_DIR / "fig5_cpi_vs_macro.pdf")
    plt.close(fig)


def plot_overview_5panel(df: pd.DataFrame):
    """5개 거시지표 종합 대조 대형 패널 차트."""
    fig, axes = plt.subplots(5, 1, figsize=(12, 16), sharex=True, dpi=300)
    setup_matplotlib()
    dates = df["date"]

    # 1. 기준금리 & 물가
    ax = axes[0]
    highlight_active_regime(ax, dates, df["active_macro"], color="crimson", label="[금리·물가] 활성", alpha=0.18)
    highlight_active_regime(ax, dates, df["active_hhdebt"], color="darkorange", label="[가계대출] 활성", alpha=0.15)
    ax.plot(dates, df["BASE_RATE"], color="black", linewidth=2.0, label="기준금리 (%)")
    ax.set_ylabel("기준금리 (%)")
    ax.legend(loc="upper left", framealpha=0.85)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_title("1. 한국은행 기준금리 추이 vs [금리·물가] 및 [가계대출] 활성 구간", fontsize=11, loc="left", fontweight="bold")

    # 2. CPI YoY
    ax = axes[1]
    highlight_active_regime(ax, dates, df["active_macro"], color="crimson", label="[금리·물가] 활성", alpha=0.18)
    ax.plot(dates, df["cpi_yoy"], color="firebrick", linewidth=2.0, label="CPI 물가상승률 (YoY, %)")
    ax.set_ylabel("CPI (%)")
    ax.legend(loc="upper left", framealpha=0.85)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_title("2. 소비자물가 상승률(CPI YoY) 추이 vs [금리·물가] 활성 구간", fontsize=11, loc="left", fontweight="bold")

    # 3. KOSPI
    ax = axes[2]
    highlight_active_regime(ax, dates, df["active_market"], color="red", label="[시황] 활성", alpha=0.15)
    highlight_active_regime(ax, dates, df["active_aichip"], color="blue", label="[AI반도체] 활성", alpha=0.18)
    highlight_active_regime(ax, dates, df["active_capital"], color="purple", label="[자본거래] 활성", alpha=0.15)
    ax.plot(dates, df["KOSPI"], color="black", linewidth=2.0, label="KOSPI 지수")
    ax.set_ylabel("KOSPI")
    ax.legend(loc="upper left", framealpha=0.85)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_title("3. KOSPI 주가지수 추이 vs 주식 관련 국면 (시황·AI반도체·자본거래)", fontsize=11, loc="left", fontweight="bold")

    # 4. USD/KRW
    ax = axes[3]
    highlight_active_regime(ax, dates, df["active_trade"], color="seagreen", label="[대외통상] 활성", alpha=0.22)
    ax.plot(dates, df["USD_KRW"], color="navy", linewidth=2.0, label="USD/KRW 환율 (원)")
    ax.set_ylabel("환율 (원)")
    ax.legend(loc="upper left", framealpha=0.85)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_title("4. 원/달러 환율 추이 vs [대외통상] 활성 구간", fontsize=11, loc="left", fontweight="bold")

    # 5. CCSI
    ax = axes[4]
    highlight_active_regime(ax, dates, df["active_macro"], color="crimson", label="[금리·물가] 활성", alpha=0.18)
    highlight_active_regime(ax, dates, df["active_hhdebt"], color="darkorange", label="[가계대출] 활성", alpha=0.15)
    ax.axhline(100, color="gray", linestyle="--", linewidth=1.2)
    ax.plot(dates, df["CCSI"], color="teal", linewidth=2.0, label="소비자심리지수 (CCSI)")
    ax.set_ylabel("CCSI")
    ax.legend(loc="lower left", framealpha=0.85)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_title("5. 소비자심리지수(CCSI) 추이 vs [금리·물가] 및 [가계대출] 활성 구간", fontsize=11, loc="left", fontweight="bold")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=0)

    fig.suptitle("한국형 경제 이슈 국면 탐지와 거시경제 지표 5종 시계열 종합 대조 (2021~2026)", fontsize=14, fontweight="bold", y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_overview_5panel.png")
    fig.savefig(FIG_DIR / "fig_overview_5panel.pdf")
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    print("데이터 로드 중...")
    df = load_merged_data()
    print(f"조인 완료: 총 {len(df)}개월 데이터 (2021-01 ~ 2026-07)")

    print("1. 기준금리 vs [금리·물가], [가계대출] 그래프 생성...")
    plot_fig1_baserate(df)

    print("2. 코스피 지수 vs 주식 관련 국면 그래프 생성...")
    plot_fig2_kospi(df)

    print("3. 원/달러 환율 vs [대외통상] 그래프 생성...")
    plot_fig3_usdkrw(df)

    print("4. 소비자심리지수(CCSI) vs 거시 국면 그래프 생성...")
    plot_fig4_ccsi(df)

    print("5. 소비자물가지수(CPI) vs [금리·물가] 그래프 생성...")
    plot_fig5_cpi(df)

    print("6. 5개 지표 종합 패널 차트(Overview) 생성...")
    plot_overview_5panel(df)

    print("\n모든 그래프 생성 완료! 저장 경로: docs/figures/")
    for ext in ["png", "pdf"]:
        for p in FIG_DIR.glob(f"*.{ext}"):
            print(f"  - {p.name} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
