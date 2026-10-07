"""5대 핵심 경제지표 단독 시계열 시각화 스크립트.

국면 음영 등 복잡한 요소를 배제하고, 지표 본연의 흐름을 연도별로 명확하게 파악할 수 있도록
5개 지표 각각의 단독 고해상도 그래프 및 5종 종합 정리 그래프를 생성한다.

지표 5종:
1. 한국은행 기준금리 (BASE_RATE, %)
2. 소비자물가 상승률 (CPI YoY, %) 및 CPI 지수
3. 코스피 지수 (KOSPI, pt)
4. 원/달러 환율 (USD/KRW, 원)
5. 소비자심리지수 (CCSI, pt - 기준선 100)

산출: docs/figures/ 내 PNG (300 DPI) 및 PDF
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from config import project_root

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
FIG_DIR = ROOT / "docs" / "figures"


def setup_matplotlib():
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 11
    plt.rcParams["figure.titlesize"] = 14
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.labelsize"] = 11


setup_matplotlib()


def load_data() -> pd.DataFrame:
    panel = pd.read_csv(PANEL_PATH)
    # 2021-01부터 2026-07까지 연구 분석 창 필터
    df = panel[(panel["month"] >= "2021-01") & (panel["month"] <= "2026-07")].copy()
    df["date"] = pd.to_datetime(df["month"] + "-01")
    df = df.sort_values("date").reset_index(drop=True)
    return df


def add_yearly_grid(ax, dates):
    """연도별 구분을 위한 1월 세로선 및 연도 레이블 추가."""
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    for y in years:
        d = pd.to_datetime(f"{y}-01-01")
        ax.axvline(d, color="lightgray", linestyle="--", linewidth=1.2, zorder=1)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y년"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%m월"))
    ax.tick_params(axis="x", which="major", pad=14, labelsize=11)
    ax.tick_params(axis="x", which="minor", labelsize=8.5, colors="gray")


# 1. 기준금리 단독 그래프
def plot_baserate(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dates = df["date"]
    add_yearly_grid(ax, dates)

    ax.plot(dates, df["BASE_RATE"], color="#1f77b4", linewidth=2.8, marker="o", markersize=5, label="한국은행 기준금리 (%)", zorder=3)
    ax.set_ylabel("기준금리 (%)", fontweight="bold", color="#1f77b4")
    ax.set_ylim(0, 4.0)
    ax.grid(True, linestyle=":", alpha=0.6, zorder=2)

    # 주요 시점 수치 텍스트 표시
    ax.annotate("0.50% (저금리)", (pd.to_datetime("2021-01-01"), 0.5), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, fontweight="bold")
    ax.annotate("3.50% (동결 정점)", (pd.to_datetime("2023-01-01"), 3.5), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, fontweight="bold", color="crimson")
    ax.annotate("2.75%", (pd.to_datetime("2026-07-01"), 2.75), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, fontweight="bold")

    ax.set_title("[지표 1] 한국은행 기준금리(BASE_RATE) 연도별 추이 (2021~2026)", pad=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_indicator_1_baserate.png")
    fig.savefig(FIG_DIR / "fig_indicator_1_baserate.pdf")
    plt.close(fig)


# 2. 소비자물가지수 (CPI YoY) 단독 그래프
def plot_cpi(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dates = df["date"]
    add_yearly_grid(ax, dates)

    ax.plot(dates, df["cpi_yoy"], color="#d62728", linewidth=2.8, marker="s", markersize=4.5, label="CPI 물가상승률 (전년동월대비, %)", zorder=3)
    ax.axhline(2.0, color="gray", linestyle=":", linewidth=1.5, label="한은 물가안정목표 (2.0%)", zorder=2)
    ax.set_ylabel("CPI 상승률 (YoY, %)", fontweight="bold", color="#d62728")
    ax.set_ylim(0.5, 7.0)
    ax.grid(True, linestyle=":", alpha=0.6, zorder=2)

    # 정점 텍스트
    peak_idx = df["cpi_yoy"].idxmax()
    peak_date = df.loc[peak_idx, "date"]
    peak_val = df.loc[peak_idx, "cpi_yoy"]
    ax.annotate(f"물가 정점 {peak_val:.1f}%\n(2022-07)", (peak_date, peak_val), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, fontweight="bold", color="crimson")

    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_title("[지표 2] 소비자물가 상승률(CPI YoY) 연도별 추이 (2021~2026)", pad=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_indicator_2_cpi.png")
    fig.savefig(FIG_DIR / "fig_indicator_2_cpi.pdf")
    plt.close(fig)


# 3. KOSPI 지수 단독 그래프
def plot_kospi(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dates = df["date"]
    add_yearly_grid(ax, dates)

    ax.plot(dates, df["KOSPI"], color="#2ca02c", linewidth=2.8, label="KOSPI 주가지수", zorder=3)
    ax.set_ylabel("KOSPI 지수", fontweight="bold", color="#2ca02c")
    ax.grid(True, linestyle=":", alpha=0.6, zorder=2)

    # 2021 고점, 2022 저점 텍스트
    ax.annotate("2021 고점 (3,296p)", (pd.to_datetime("2021-06-01"), df.loc[df["month"]=="2021-06", "KOSPI"].values[0]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9, fontweight="bold")
    low_2022 = df.loc[df["month"]=="2022-09", "KOSPI"].values[0]
    ax.annotate("2022 저점 (2,155p)", (pd.to_datetime("2022-09-01"), low_2022), textcoords="offset points", xytext=(0, -18), ha="center", fontsize=9, fontweight="bold", color="darkred")

    ax.set_title("[지표 3] 코스피(KOSPI) 주가지수 연도별 추이 (2021~2026)", pad=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_indicator_3_kospi.png")
    fig.savefig(FIG_DIR / "fig_indicator_3_kospi.pdf")
    plt.close(fig)


# 4. 원/달러 환율 단독 그래프
def plot_usdkrw(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dates = df["date"]
    add_yearly_grid(ax, dates)

    ax.plot(dates, df["USD_KRW"], color="#9467bd", linewidth=2.8, marker="^", markersize=4, label="원/달러 환율 (원)", zorder=3)
    ax.axhline(1300, color="orange", linestyle="--", linewidth=1.2, label="1,300원 기준선", zorder=2)
    ax.axhline(1400, color="crimson", linestyle="--", linewidth=1.2, label="1,400원 고환율선", zorder=2)
    ax.set_ylabel("USD/KRW 환율 (원)", fontweight="bold", color="#9467bd")
    ax.set_ylim(1050, 1600)
    ax.grid(True, linestyle=":", alpha=0.6, zorder=2)

    ax.legend(loc="upper left", framealpha=0.9)
    ax.set_title("[지표 4] 원/달러 환율(USD/KRW) 연도별 추이 (2021~2026)", pad=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_indicator_4_usdkrw.png")
    fig.savefig(FIG_DIR / "fig_indicator_4_usdkrw.pdf")
    plt.close(fig)


# 5. 소비자심리지수 (CCSI) 단독 그래프
def plot_ccsi(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    dates = df["date"]
    add_yearly_grid(ax, dates)

    ax.axhline(100, color="gray", linestyle="-", linewidth=1.8, label="기준선 100 (비관/낙관 분기점)", zorder=2)
    ax.plot(dates, df["CCSI"], color="#ff7f0e", linewidth=2.8, marker="o", markersize=4.5, label="소비자심리지수 (CCSI)", zorder=3)

    # 100 미만(비관 구간) 음영 옅게
    ax.fill_between(dates, df["CCSI"], 100, where=(df["CCSI"] < 100), color="crimson", alpha=0.12, label="소비심리 비관 구간 (<100)")
    ax.fill_between(dates, df["CCSI"], 100, where=(df["CCSI"] >= 100), color="forestgreen", alpha=0.12, label="소비심리 낙관 구간 (>=100)")

    ax.set_ylabel("소비자심리지수 (CCSI)", fontweight="bold", color="#ff7f0e")
    ax.set_ylim(75, 115)
    ax.grid(True, linestyle=":", alpha=0.6, zorder=2)

    ax.legend(loc="lower left", framealpha=0.9)
    ax.set_title("[지표 5] 소비자심리지수(CCSI) 연도별 추이 (2021~2026)", pad=15, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_indicator_5_ccsi.png")
    fig.savefig(FIG_DIR / "fig_indicator_5_ccsi.pdf")
    plt.close(fig)


# 6. 5대 지표 한눈에 보기 종합 패널
def plot_5panel_indicators(df: pd.DataFrame):
    fig, axes = plt.subplots(5, 1, figsize=(11, 14), sharex=True, dpi=300)
    dates = df["date"]

    # 1. BASE_RATE
    ax = axes[0]
    add_yearly_grid(ax, dates)
    ax.plot(dates, df["BASE_RATE"], color="#1f77b4", linewidth=2.2)
    ax.set_ylabel("기준금리 (%)")
    ax.set_title("1. 한국은행 기준금리 (0.5% -> 3.5% -> 2.75%)", fontsize=10.5, loc="left", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)

    # 2. CPI YoY
    ax = axes[1]
    add_yearly_grid(ax, dates)
    ax.plot(dates, df["cpi_yoy"], color="#d62728", linewidth=2.2)
    ax.axhline(2.0, color="gray", linestyle=":", linewidth=1.2)
    ax.set_ylabel("CPI YoY (%)")
    ax.set_title("2. 소비자물가 상승률 (전년동월대비, 2022년 정점 6.3%)", fontsize=10.5, loc="left", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)

    # 3. KOSPI
    ax = axes[2]
    add_yearly_grid(ax, dates)
    ax.plot(dates, df["KOSPI"], color="#2ca02c", linewidth=2.2)
    ax.set_ylabel("KOSPI (pt)")
    ax.set_title("3. 코스피 지수 (2021년 3,300 -> 2022년 2,150 -> 2026년 랠리)", fontsize=10.5, loc="left", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)

    # 4. USD/KRW
    ax = axes[3]
    add_yearly_grid(ax, dates)
    ax.plot(dates, df["USD_KRW"], color="#9467bd", linewidth=2.2)
    ax.axhline(1300, color="orange", linestyle="--", linewidth=1.0)
    ax.set_ylabel("환율 (원)")
    ax.set_title("4. 원/달러 환율 (1,100원대 -> 1,440원 돌파 고환율)", fontsize=10.5, loc="left", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)

    # 5. CCSI
    ax = axes[4]
    add_yearly_grid(ax, dates)
    ax.axhline(100, color="gray", linestyle="-", linewidth=1.2)
    ax.plot(dates, df["CCSI"], color="#ff7f0e", linewidth=2.2)
    ax.fill_between(dates, df["CCSI"], 100, where=(df["CCSI"] < 100), color="crimson", alpha=0.15)
    ax.set_ylabel("CCSI (pt)")
    ax.set_title("5. 소비자심리지수 (기준선 100 미만 비관 구간 음영)", fontsize=10.5, loc="left", fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)

    fig.suptitle("한국은행 ECOS 5대 거시경제 핵심 지표 연도별 종합 추이 (2021~2026)", fontsize=13, fontweight="bold", y=0.995)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_indicators_5_pure.png")
    fig.savefig(FIG_DIR / "fig_indicators_5_pure.pdf")
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()
    print("5대 지표 단독 그래프 생성 중...")
    plot_baserate(df)
    plot_cpi(df)
    plot_kospi(df)
    plot_usdkrw(df)
    plot_ccsi(df)
    plot_5panel_indicators(df)
    print("완료! 산출물:")
    for name in [
        "fig_indicator_1_baserate.png",
        "fig_indicator_2_cpi.png",
        "fig_indicator_3_kospi.png",
        "fig_indicator_4_usdkrw.png",
        "fig_indicator_5_ccsi.png",
        "fig_indicators_5_pure.png",
    ]:
        p = FIG_DIR / name
        print(f"  - {name} ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
