"""3개월(분기별, Quarterly) 및 반년치(반기별) 단위로 지표와 8대 국면을 대조하는 시각화 스크립트.

월별 67개 데이터포인트의 미세 잔파동(노이즈)을 걷어내고,
3개월(분기) 평균 22개 포인트로 매끄럽게 정리하여
5대 경제지표와 8대 국면의 구조적 추세를 덜 복잡하고 직관적으로 대조한다.

산출물:
- docs/figures/fig_quarterly_1_kospi.png
- docs/figures/fig_quarterly_2_cpi.png
- docs/figures/fig_quarterly_3_baserate.png
- docs/figures/fig_quarterly_4_usdkrw.png
- docs/figures/fig_quarterly_5_ccsi.png
- docs/figures/fig_quarterly_overview.png
- 엑셀 파일(ecos_regime_dual_axis_charts.xlsx) 내 '분기별_대조_시계열' 시트 추가
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import openpyxl
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from config import project_root

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
EXCEL_PATH = ROOT / "data" / "processed" / "ecos_regime_dual_axis_charts.xlsx"
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
    ("KOSPI", "fig_quarterly_1_kospi", "코스피(KOSPI) 주가지수", "pt", "#,##0.0"),
    ("cpi_yoy", "fig_quarterly_2_cpi", "소비자물가 상승률(CPI YoY)", "%", "0.00"),
    ("BASE_RATE", "fig_quarterly_3_baserate", "한국은행 기준금리", "%", "0.00"),
    ("USD_KRW", "fig_quarterly_4_usdkrw", "원/달러 환율(USD/KRW)", "원", "#,##0.0"),
    ("CCSI", "fig_quarterly_5_ccsi", "소비자심리지수(CCSI)", "pt", "0.0"),
]


def load_quarterly_data() -> pd.DataFrame:
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
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)

    # 3개월 분기별 평균 집계
    agg_dict = {
        "KOSPI": "mean",
        "cpi_yoy": "mean",
        "BASE_RATE": "mean",
        "USD_KRW": "mean",
        "CCSI": "mean",
    }
    for slug, _, _ in REGIME_COLORS:
        agg_dict[f"z_{slug}"] = "mean"

    q_df = df.groupby("quarter").agg(agg_dict).reset_index()
    # 분기 레이블 정리: 2021Q1 -> '21 1Q
    q_df["q_label"] = q_df["quarter"].apply(lambda x: f"{x[2:4]}년 {x[5]}Q")
    return q_df


def plot_quarterly_figures(q_df: pd.DataFrame):
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    x_indices = np.arange(len(q_df))
    labels = q_df["q_label"]

    for key, fname, title, unit, _ in INDICATORS:
        fig, ax1 = plt.subplots(figsize=(12, 5.8), dpi=300)

        # 연도 구분선 (각 연도 1Q 앞)
        for idx, q_str in enumerate(q_df["quarter"]):
            if q_str.endswith("Q1"):
                ax1.axvline(idx, color="#d9d9d9", linestyle="--", linewidth=1.2, zorder=1)

        # 왼쪽 축: 경제지표 (굵은 검은색 선 + 원형 마커)
        line_ind = ax1.plot(x_indices, q_df[key], color="#111111", linewidth=3.5, marker="o", markersize=6, label=f"★ {title} ({unit})", zorder=5)
        ax1.set_ylabel(f"{title} ({unit})", fontsize=11, fontweight="bold", color="#111111")
        ax1.grid(True, linestyle=":", alpha=0.5, zorder=1)

        # 오른쪽 축: 8대 국면 분기 평균 z-score (8개 고유 색상 선)
        ax2 = ax1.twinx()
        lines_reg = []
        for slug, name, color in REGIME_COLORS:
            (l,) = ax2.plot(x_indices, q_df[f"z_{slug}"], color=color, linewidth=2.0, alpha=0.85, marker="s", markersize=4, label=f"{name} (z)", zorder=3)
            lines_reg.append(l)

        ax2.axhline(0.5, color="gray", linestyle=":", linewidth=1.2, alpha=0.7)
        ax2.set_ylabel("8대 국면 표준화점수 (분기 평균 z-score)", fontsize=11, fontweight="bold", color="#444444")
        ax2.set_ylim(-2.0, 3.0)

        # X축 눈금
        ax1.set_xticks(x_indices)
        ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=9.5)

        # 범례
        all_lines = line_ind + lines_reg
        leg_labels = [l.get_label() for l in all_lines]
        ax1.legend(all_lines, leg_labels, loc="upper left", bbox_to_anchor=(1.08, 1.0), framealpha=0.95, fontsize=9.5)

        plt.title(f"[3개월 분기별 대조] {title} vs 8대 국면 분기 추세 (2021Q1 ~ 2026Q3)", fontsize=12.5, fontweight="bold", pad=12)
        fig.tight_layout()

        png_p = FIG_DIR / f"{fname}.png"
        fig.savefig(png_p, bbox_inches="tight")
        plt.close(fig)
        print(f"분기별 그래프 저장 완료: {png_p.name}")


def update_excel_with_quarterly(q_df: pd.DataFrame):
    wb = openpyxl.load_workbook(EXCEL_PATH)
    sheet_name = "분기별_3개월단위_대조"
    if sheet_name in wb.sheetnames:
        wb.remove(wb[sheet_name])

    ws = wb.create_sheet(title=sheet_name, index=1)

    # 스타일
    header_navy = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_green = PatternFill(start_color="274E13", end_color="274E13", fill_type="solid")
    font_h = Font(name="맑은 고딕", size=10, bold=True, color="FFFFFF")
    font_cell = Font(name="맑은 고딕", size=9.5)
    border_thin = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0"),
    )

    # 상단 설명
    ws.cell(row=2, column=2, value="■ [3개월 분기별 집계] 5대 경제지표 및 8대 국면 분기 평균 시계열 대조 (2021Q1 ~ 2026Q3)").font = Font(name="맑은 고딕", size=13, bold=True, color="1F497D")
    ws.cell(row=3, column=2, value="※ 월별 미세 노이즈를 3개월 평균으로 평활화(Smoothing)하여 거시경제 구조적 변곡점을 한눈에 조망").font = font_cell

    # 헤더 작성 (행 5)
    headers = ["기준분기", "코스피(pt)", "CPI물가(%)", "기준금리(%)", "환율(원)", "소비자심리(pt)"] + [f"{name}(z)" for _, name, _ in REGIME_COLORS]
    for c_i, h in enumerate(headers, start=2):
        c = ws.cell(row=5, column=c_i, value=h)
        c.font = font_h
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.fill = header_navy if c_i <= 7 else header_green

    # 데이터 쓰기
    for r_i, r in q_df.iterrows():
        curr_row = 6 + r_i
        ws.cell(row=curr_row, column=2, value=r["q_label"]).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=curr_row, column=3, value=r["KOSPI"]).number_format = "#,##0.0"
        ws.cell(row=curr_row, column=4, value=r["cpi_yoy"]).number_format = "0.00"
        ws.cell(row=curr_row, column=5, value=r["BASE_RATE"]).number_format = "0.00"
        ws.cell(row=curr_row, column=6, value=r["USD_KRW"]).number_format = "#,##0.0"
        ws.cell(row=curr_row, column=7, value=r["CCSI"]).number_format = "0.0"

        for reg_idx, (slug, _, _) in enumerate(REGIME_COLORS, start=8):
            cell_z = ws.cell(row=curr_row, column=reg_idx, value=r[f"z_{slug}"])
            cell_z.number_format = "+0.00;-0.00;0.00"

        for col_k in range(2, 16):
            cell = ws.cell(row=curr_row, column=col_k)
            cell.font = font_cell
            cell.border = border_thin
            if col_k > 2:
                cell.alignment = Alignment(horizontal="right", vertical="center")

    # 열 너비
    ws.column_dimensions["B"].width = 14
    for let in ["C", "D", "E", "F", "G"]:
        ws.column_dimensions[let].width = 15
    for let in ["H", "I", "J", "K", "L", "M", "N", "O"]:
        ws.column_dimensions[let].width = 14

    # 엑셀 내장 분기 차트 삽입 (Q5 위치: 코스피 분기 대조 차트)
    max_r = 5 + len(q_df)
    cats = Reference(ws, min_col=2, min_row=6, max_row=max_r)

    ch_ind = LineChart()
    ch_ind.title = "코스피 지수 vs 8대 국면 분기별 추세선"
    ch_ind.style = 13
    ch_ind.width = 24
    ch_ind.height = 12
    ch_ind.x_axis.title = "기준분기 (3개월 단위)"
    ch_ind.y_axis.title = "코스피 지수 (pt)"

    data_kospi = Reference(ws, min_col=3, min_row=5, max_row=max_r)
    ch_ind.add_data(data_kospi, titles_from_data=True)
    ch_ind.set_categories(cats)

    ch_reg = LineChart()
    ch_reg.style = 10
    ch_reg.y_axis.title = "국면 분기평균 z-score"
    ch_reg.y_axis.axId = 200
    ch_reg.y_axis.crosses = "max"

    data_reg = Reference(ws, min_col=8, min_row=5, max_row=max_r, max_col=15)
    ch_reg.add_data(data_reg, titles_from_data=True)

    for s_idx, (_, _, color_hex) in enumerate(REGIME_COLORS):
        if s_idx < len(ch_reg.series):
            s = ch_reg.series[s_idx]
            s.graphicalProperties.line.solidFill = color_hex
            s.graphicalProperties.line.width = 16000

    ch_ind += ch_reg
    ws.add_chart(ch_ind, "Q5")

    wb.save(EXCEL_PATH)
    print(f"엑셀 파일에 '분기별_3개월단위_대조' 시트 추가 성공: {EXCEL_PATH}")


def main():
    q_df = load_quarterly_data()
    plot_quarterly_figures(q_df)
    update_excel_with_quarterly(q_df)


if __name__ == "__main__":
    main()
