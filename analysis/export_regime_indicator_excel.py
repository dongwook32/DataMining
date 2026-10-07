"""5대 경제지표와 8대 국면 전체를 '오직 선형 그래프(Line Chart)'로만 대조하는 심플 엑셀 파일 생성 스크립트.

특징:
1. 복잡한 막대차트, 순위표, 히트맵 배제
2. 지표별로 시트 1개씩:
   - 맨 위에 가로 27cm x 세로 14cm 대형 이중축 선형 그래프 배치
   - 왼쪽 축: 경제지표 (굵은 검정 실선)
   - 오른쪽 축: 8대 국면 z-score (8가지 뚜렷한 색상의 선)
   - 그래프 아래에는 깔끔한 67개월 데이터 테이블만 배치
3. 시트 구성:
   - 1_코스피_선형비교
   - 2_소비자물가_선형비교
   - 3_기준금리_선형비교
   - 4_원달러환율_선형비교
   - 5_소비자심리_선형비교
   - 전체데이터_참조용
"""

from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from config import project_root

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
REGIME_PATH = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
OUT_EXCEL_PATH = ROOT / "data" / "processed" / "ecos_regime_dual_axis_charts.xlsx"

REGIME_INFO = [
    ("macro", "금리·물가", "E41A1C"),       # 선명한 빨강
    ("realestate", "부동산", "FF7F00"),      # 주황
    ("hhdebt", "가계대출", "A65628"),        # 갈색
    ("trade", "대외통상", "984EA3"),        # 보라
    ("aichip", "AI반도체", "377EB8"),       # 파랑
    ("market", "시황", "4DAF4A"),           # 초록
    ("earnings", "기업실적", "17BECF"),     # 청록
    ("capital", "자본거래", "F781BF"),      # 분홍
]

INDICATORS = [
    {
        "key": "KOSPI",
        "sheet": "1_코스피_선형비교",
        "title": "코스피(KOSPI) 주가지수",
        "unit": "pt",
        "num_fmt": "#,##0.0",
    },
    {
        "key": "cpi_yoy",
        "sheet": "2_소비자물가_선형비교",
        "title": "소비자물가 상승률(CPI YoY)",
        "unit": "%",
        "num_fmt": "0.00",
    },
    {
        "key": "BASE_RATE",
        "sheet": "3_기준금리_선형비교",
        "title": "한국은행 기준금리",
        "unit": "%",
        "num_fmt": "0.00",
    },
    {
        "key": "USD_KRW",
        "sheet": "4_원달러환율_선형비교",
        "title": "원/달러 환율(USD/KRW)",
        "unit": "원",
        "num_fmt": "#,##0.0",
    },
    {
        "key": "CCSI",
        "sheet": "5_소비자심리_선형비교",
        "title": "소비자심리지수(CCSI)",
        "unit": "pt",
        "num_fmt": "0.0",
    },
]


def prepare_data():
    panel = pd.read_csv(PANEL_PATH)
    regime = pd.read_csv(REGIME_PATH)

    df_p = panel[(panel["month"] >= "2021-01") & (panel["month"] <= "2026-07")].copy()
    df_r = regime[(regime["month"] >= "2021-01") & (regime["month"] <= "2026-07")].copy()

    for slug, _, _ in REGIME_INFO:
        sh = df_r[f"share_{slug}"]
        mean = sh.mean()
        std = sh.std(ddof=0)
        df_r[f"z_{slug}"] = (sh - mean) / std

    m = pd.merge(
        df_p[["month", "BASE_RATE", "cpi_yoy", "KOSPI", "USD_KRW", "CCSI"]],
        df_r[["month"] + [f"z_{slug}" for slug, _, _ in REGIME_INFO]],
        on="month",
        how="inner",
    ).sort_values("month").reset_index(drop=True)

    return m


def main():
    df = prepare_data()
    n_rows = len(df) + 1  # 68행

    wb = openpyxl.Workbook()
    # 첫 시트 제거 준비
    ws_first = wb.active

    # 스타일
    header_navy = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_green = PatternFill(start_color="274E13", end_color="274E13", fill_type="solid")
    font_header = Font(name="맑은 고딕", size=10, bold=True, color="FFFFFF")
    font_cell = Font(name="맑은 고딕", size=9.5)
    border_thin = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0"),
    )
    align_center = Alignment(horizontal="center", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # 1~5 지표별 시트 생성
    for idx, ind in enumerate(INDICATORS):
        ws = wb.create_sheet(title=ind["sheet"])

        # 데이터 테이블 시작 행 (행 28부터 데이터 배치, 1~26행은 차트 영역)
        data_start_row = 28

        # 헤더 쓰기
        headers = ["기준월", f"{ind['title']} ({ind['unit']})"] + [f"{name} (z-score)" for _, name, _ in REGIME_INFO]
        for c_i, h in enumerate(headers, start=1):
            cell = ws.cell(row=data_start_row, column=c_i, value=h)
            cell.font = font_header
            cell.alignment = align_center
            cell.fill = header_navy if c_i <= 2 else header_green

        # 데이터 채우기
        for r_i, r in df.iterrows():
            curr_row = data_start_row + 1 + r_i
            ws.cell(row=curr_row, column=1, value=r["month"]).alignment = align_center

            c_ind = ws.cell(row=curr_row, column=2, value=r[ind["key"]])
            c_ind.alignment = align_right
            c_ind.number_format = ind["num_fmt"]

            for reg_idx, (slug, _, _) in enumerate(REGIME_INFO, start=3):
                c_z = ws.cell(row=curr_row, column=reg_idx, value=r[f"z_{slug}"])
                c_z.alignment = align_right
                c_z.number_format = "+0.00;-0.00;0.00"

            for col_i in range(1, 11):
                c = ws.cell(row=curr_row, column=col_i)
                c.font = font_cell
                c.border = border_thin

        # 열 너비
        ws.column_dimensions["A"].width = 12
        ws.column_dimensions["B"].width = 24
        for col_letter in ["C", "D", "E", "F", "G", "H", "I", "J"]:
            ws.column_dimensions[col_letter].width = 16

        # 이중축 선형 그래프 생성
        max_r = data_start_row + len(df)
        cats = Reference(ws, min_col=1, min_row=data_start_row + 1, max_row=max_r)

        # 1) 경제지표 선 차트 (기본 축, 왼쪽)
        chart_ind = LineChart()
        chart_ind.title = f"{ind['title']} vs 8대 국면 전체 시계열 선형 비교 (2021~2026)"
        chart_ind.style = 13
        chart_ind.width = 27
        chart_ind.height = 13.5
        chart_ind.x_axis.title = "기준월 (YYYY-MM)"
        chart_ind.y_axis.title = f"← {ind['title']} ({ind['unit']})"

        data_ind = Reference(ws, min_col=2, min_row=data_start_row, max_row=max_r)
        chart_ind.add_data(data_ind, titles_from_data=True)
        chart_ind.set_categories(cats)

        # 경제지표 선 스타일: 굵은 검은색 선
        if chart_ind.series:
            s_ind = chart_ind.series[0]
            s_ind.graphicalProperties.line.solidFill = "000000"
            s_ind.graphicalProperties.line.width = 30000  # 굵은 선 (약 3pt)

        # 2) 8대 국면 선 차트 (보조 축, 오른쪽)
        chart_reg = LineChart()
        chart_reg.style = 10
        chart_reg.y_axis.title = "8대 국면 표준화점수 (z-score) →"
        chart_reg.y_axis.axId = 200
        chart_reg.y_axis.crosses = "max"

        data_reg = Reference(ws, min_col=3, min_row=data_start_row, max_row=max_r, max_col=10)
        chart_reg.add_data(data_reg, titles_from_data=True)

        # 8개 국면 선별 고유 색상 적용
        for s_idx, (_, _, color_hex) in enumerate(REGIME_INFO):
            if s_idx < len(chart_reg.series):
                s = chart_reg.series[s_idx]
                s.graphicalProperties.line.solidFill = color_hex
                s.graphicalProperties.line.width = 15000  # 약 1.5pt

        # 결합
        chart_ind += chart_reg
        chart_ind.legend.legendPos = "r"  # 범례 오른쪽 배치

        # 차트를 상단 B2 위치에 삽입
        ws.add_chart(chart_ind, "B2")

    # 전체 데이터 시트 추가
    ws_all = wb.create_sheet(title="전체시계열데이터")
    ws_all.append(["기준월", "코스피(pt)", "소비자물가(%)", "기준금리(%)", "환율(원)", "소비자심리(CCSI)"] + [f"z_{name}" for _, name, _ in REGIME_INFO])
    for c_i in range(1, 15):
        ws_all.cell(row=1, column=c_i).fill = header_navy
        ws_all.cell(row=1, column=c_i).font = font_header
        ws_all.cell(row=1, column=c_i).alignment = align_center

    for _, r in df.iterrows():
        ws_all.append([
            r["month"], r["KOSPI"], r["cpi_yoy"], r["BASE_RATE"], r["USD_KRW"], r["CCSI"],
            r["z_macro"], r["z_realestate"], r["z_hhdebt"], r["z_trade"],
            r["z_aichip"], r["z_market"], r["z_earnings"], r["z_capital"]
        ])

    # 빈 기본 시트 삭제
    wb.remove(ws_first)

    OUT_EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_EXCEL_PATH)
    print(f"심플 선형 엑셀 파일 저장 성공: {OUT_EXCEL_PATH} ({OUT_EXCEL_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
