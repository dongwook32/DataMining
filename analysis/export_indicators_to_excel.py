"""한국은행 ECOS 5대 핵심 경제지표 엑셀 파일 및 네이티브 차트 생성 스크립트.

월별 패널 데이터에서 5대 지표를 추출하여:
1. '5대지표_종합데이터' 시트: 깔끔한 서식의 전체 시계열 테이블 (2021-01 ~ 2026-07)
2. '종합_차트모아보기' 시트: 5대 지표 네이티브 엑셀 꺾은선 차트 5종 배치
3. 각 지표별 전용 시트 (기준금리, 소비자물가, 코스피, 원달러환율, 소비자심리지수):
   - 해당 지표 월별 데이터 + 대형 엑셀 차트
사용자가 엑셀에서 클릭하여 마우스 호버로 값을 확인하거나 차트 서식을 자유롭게 편집할 수 있도록 제작.
"""

from pathlib import Path
import pandas as pd
import openpyxl
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

from config import project_root

ROOT = project_root()
PANEL_PATH = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
OUT_EXCEL_PATH = ROOT / "data" / "processed" / "ecos_5_indicators_charts.xlsx"


def create_excel_with_charts():
    # 1. 데이터 로드 및 정제
    panel = pd.read_csv(PANEL_PATH)
    df = panel[(panel["month"] >= "2021-01") & (panel["month"] <= "2026-07")].copy()
    df = df.sort_values("month").reset_index(drop=True)

    # 5대 지표 선택 및 컬럼명 정리
    cols_map = {
        "month": "기준월",
        "BASE_RATE": "한국은행 기준금리 (%)",
        "cpi_yoy": "소비자물가 상승률 (YoY, %)",
        "KOSPI": "코스피 지수 (KOSPI, pt)",
        "USD_KRW": "원/달러 환율 (USD/KRW, 원)",
        "CCSI": "소비자심리지수 (CCSI, pt)",
    }
    sub_df = df[list(cols_map.keys())].rename(columns=cols_map)

    # 2. openpyxl 워크북 생성
    wb = openpyxl.Workbook()
    # 기본 시트 이름 변경
    ws_all = wb.active
    ws_all.title = "5대지표_전체데이터"

    # 서식 정의
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="맑은 고딕", size=11, bold=True, color="FFFFFF")
    cell_font = Font(name="맑은 고딕", size=10)
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )
    align_center = Alignment(horizontal="center", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # 전체 데이터 시트 쓰기
    for r in dataframe_to_rows(sub_df, index=False, header=True):
        ws_all.append(r)

    # 전체 데이터 시트 서식 적용
    for col_idx, col_name in enumerate(sub_df.columns, start=1):
        cell = ws_all.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center

    for row_idx in range(2, len(sub_df) + 2):
        for col_idx in range(1, len(sub_df.columns) + 1):
            cell = ws_all.cell(row=row_idx, column=col_idx)
            cell.font = cell_font
            cell.border = thin_border
            if col_idx == 1:
                cell.alignment = align_center
            else:
                cell.alignment = align_right
                if col_idx in [2, 3]:  # 기준금리, 물가상승률
                    cell.number_format = "0.00"
                elif col_idx in [4, 5]:  # 코스피, 환율
                    cell.number_format = "#,##0.0"
                elif col_idx == 6:  # CCSI
                    cell.number_format = "0.0"

    # 열 너비 자동 조정
    for col in ws_all.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws_all.column_dimensions[col_letter].width = max(max_len + 5, 14)

    # 3. '차트모아보기' 시트 생성 및 5개 엑셀 차트 배치
    ws_charts = wb.create_sheet(title="지표별_차트모아보기")

    indicators = [
        {"col": 2, "name": "한국은행 기준금리 (%)", "title": "[지표 1] 한국은행 기준금리 추이 (2021~2026)", "cell": "B2"},
        {"col": 3, "name": "소비자물가 상승률 (%)", "title": "[지표 2] 소비자물가 상승률(CPI YoY) 추이 (2021~2026)", "cell": "B18"},
        {"col": 4, "name": "코스피 지수 (pt)", "title": "[지표 3] 코스피 주가지수(KOSPI) 추이 (2021~2026)", "cell": "B34"},
        {"col": 5, "name": "원/달러 환율 (원)", "title": "[지표 4] 원/달러 환율(USD/KRW) 추이 (2021~2026)", "cell": "B50"},
        {"col": 6, "name": "소비자심리지수 (pt)", "title": "[지표 5] 소비자심리지수(CCSI) 추이 (2021~2026)", "cell": "B66"},
    ]

    n_rows = len(sub_df) + 1  # 68행 (헤더 1 + 데이터 67)
    cats = Reference(ws_all, min_col=1, min_row=2, max_row=n_rows)  # 기준월 (X축)

    for item in indicators:
        chart = LineChart()
        chart.title = item["title"]
        chart.style = 13  # 깔끔한 모던 라인 스타일
        chart.y_axis.title = item["name"]
        chart.x_axis.title = "기준월"
        chart.width = 24  # 차트 너비 (cm)
        chart.height = 10  # 차트 높이 (cm)
        chart.legend = None  # 단일 지표이므로 범례 제거하여 차트 영역 넓힘

        data = Reference(ws_all, min_col=item["col"], min_row=1, max_row=n_rows)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)

        ws_charts.add_chart(chart, item["cell"])

    # 4. 각 지표별 전용 시트 생성 (데이터 표 + 대형 차트)
    indicator_sheets = [
        ("1_기준금리", 2, "한국은행 기준금리 (%)", "0.00"),
        ("2_소비자물가", 3, "소비자물가 상승률 (YoY, %)", "0.00"),
        ("3_코스피", 4, "코스피 지수 (KOSPI, pt)", "#,##0.0"),
        ("4_원달러환율", 5, "원/달러 환율 (USD/KRW, 원)", "#,##0.0"),
        ("5_소비자심리", 6, "소비자심리지수 (CCSI, pt)", "0.0"),
    ]

    for sheet_name, col_idx, ind_title, num_fmt in indicator_sheets:
        ws_ind = wb.create_sheet(title=sheet_name)

        # 데이터 쓰기: 기준월과 해당 지표만
        ws_ind.cell(row=1, column=1, value="기준월").fill = header_fill
        ws_ind.cell(row=1, column=1).font = header_font
        ws_ind.cell(row=1, column=1).alignment = align_center

        ws_ind.cell(row=1, column=2, value=ind_title).fill = header_fill
        ws_ind.cell(row=1, column=2).font = header_font
        ws_ind.cell(row=1, column=2).alignment = align_center

        for r_i, (_, row) in enumerate(sub_df.iterrows(), start=2):
            c1 = ws_ind.cell(row=r_i, column=1, value=row["기준월"])
            c1.font = cell_font
            c1.border = thin_border
            c1.alignment = align_center

            c2 = ws_ind.cell(row=r_i, column=2, value=row[ind_title])
            c2.font = cell_font
            c2.border = thin_border
            c2.alignment = align_right
            c2.number_format = num_fmt

        ws_ind.column_dimensions["A"].width = 14
        ws_ind.column_dimensions["B"].width = 24

        # 대형 엑셀 차트 추가 (D2 위치)
        ch = LineChart()
        ch.title = f"{ind_title} 연도별 시계열 추이 (2021~2026)"
        ch.style = 10
        ch.y_axis.title = ind_title
        ch.x_axis.title = "기준월 (YYYY-MM)"
        ch.width = 26
        ch.height = 14
        ch.legend = None

        ch_data = Reference(ws_ind, min_col=2, min_row=1, max_row=n_rows)
        ch_cats = Reference(ws_ind, min_col=1, min_row=2, max_row=n_rows)
        ch.add_data(ch_data, titles_from_data=True)
        ch.set_categories(ch_cats)

        ws_ind.add_chart(ch, "D2")

    OUT_EXCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_EXCEL_PATH)
    print(f"엑셀 파일 생성 성공: {OUT_EXCEL_PATH} ({OUT_EXCEL_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    create_excel_with_charts()
