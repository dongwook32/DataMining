"""JKIICE (한국정보통신학회논문지) 2026년 국문지 공식 투고양식 기반 최종 제출용 Word (.docx) 생성 스크립트.

공식 양식 기준 (https://kiice.org/board/proceedings/article/271327, 한국정보통신학회_국문지양식2026.zip):
- 원문파일 (`docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`):
  공식 양식의 ① 국문저자, ② 영문저자·직위·소속, ③ 교신저자 각주, ⑤ 저자 약력(사진·성명·학력·관심분야) 입력란을 모두 포함한 제출 원본 양식
- 심사용 파일 (`docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`):
  '★★★심사용 파일 편집양식★★★ 반드시 확인.pdf' 지침에 따라 ① 국문저자, ② 영문저자·소속, ③ 교신저자 각주, ④ 사사(Acknowledgements), ⑤ 저자 약력을 완전히 삭제한 블라인드 심사용 양식
"""

from pathlib import Path
import shutil
import docx
from docx.shared import Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(r"c:\Users\CDW\1_Project\DataMining")
DOCS_DIR = ROOT / "docs"
OUT_SUBMISSION_PATH = DOCS_DIR / "PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx"
OUT_BLIND_PATH = DOCS_DIR / "PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx"

FONT_GOTHIC = "맑은 고딕"
FONT_MYEONGJO = "바탕"
FONT_EN_SERIF = "Times New Roman"
FONT_EN_SANS = "Arial"


def set_run_font(run, kor_font=FONT_MYEONGJO, eng_font=FONT_EN_SERIF, size_pt=9.2, bold=False, italic=False, color_rgb=(0, 0, 0), char_spacing_pt=0):
    """한글(eastAsia)과 영문(ascii/hAnsi) 폰트를 동시에 지정하고 자간을 설정한다."""
    run.font.name = eng_font
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), eng_font)
    rFonts.set(qn("w:hAnsi"), eng_font)
    rFonts.set(qn("w:eastAsia"), kor_font)
    if char_spacing_pt != 0:
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:val"), str(int(char_spacing_pt * 20)))
        rPr.append(spacing)


def set_cell_margins(cell, top=60, bottom=60, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_jkiice_table_borders(table):
    """JKIICE 학술지 표준 삼선표 (상단/하단 1.0pt 검정 실선, 내부 가로 보조선 0.25pt 회색선, 세로선 없음)."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_horizontal_rule(doc, sz=6, color="000000", space_before=2, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="{sz}" w:space="1" w:color="{color}"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)
    return p


def build_jkiice_2026_docx(out_path: Path, blind_mode: bool = False):
    doc = docx.Document()

    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(24)
        section.bottom_margin = Mm(24)
        section.left_margin = Mm(20)
        section.right_margin = Mm(20)
        section.header_distance = Mm(10)
        section.footer_distance = Mm(10)

        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        mode_tag = "심사용 블라인드본" if blind_mode else "원문파일"
        hrun = hp.add_run(
            f"한국정보통신학회논문지 (JKIICE) 2026 ({mode_tag})  |  "
            "뉴스 빅데이터와 NMF 기반의 한국형 경제 이슈 다중 국면 탐지 및 다각적 실증 검증"
        )
        set_run_font(hrun, FONT_GOTHIC, FONT_EN_SANS, size_pt=7.5, color_rgb=(100, 100, 100))

    # =========================================================================
    # 제1면: 학회 상단 로고 헤더, 국·영문 제목, 저자란, 국·영문 요약, 키워드, 하단 서지란
    # =========================================================================
    p_banner_top = doc.add_paragraph()
    p_banner_top.paragraph_format.space_before = Pt(0)
    p_banner_top.paragraph_format.space_after = Pt(2)
    r_jkiice = p_banner_top.add_run("JKIICE   ")
    set_run_font(r_jkiice, FONT_GOTHIC, FONT_EN_SANS, size_pt=20, bold=True, color_rgb=(0, 0, 0))
    r_jname = p_banner_top.add_run("Journal of the Korea Institute of Information and Communication Engineering")
    set_run_font(r_jname, FONT_GOTHIC, FONT_EN_SANS, size_pt=9, bold=False, color_rgb=(40, 40, 40))

    add_horizontal_rule(doc, sz=8, color="000000", space_before=0, space_after=2)
    p_vol = doc.add_paragraph()
    p_vol.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_vol.paragraph_format.space_before = Pt(0)
    p_vol.paragraph_format.space_after = Pt(2)
    r_vol = p_vol.add_run("한국정보통신학회논문지 Vol. 30, No. X: XXX~XXX, 2026 (출판사에서 작성)")
    set_run_font(r_vol, FONT_GOTHIC, FONT_EN_SERIF, size_pt=8.5, color_rgb=(30, 30, 30))
    add_horizontal_rule(doc, sz=4, color="000000", space_before=0, space_after=8)

    # 국문 제목 (산돌고딕B/맑은 고딕 Bold, 17pt, 자간 -5, 줄간격 130%, 왼쪽정렬)
    p_title_ko = doc.add_paragraph()
    p_title_ko.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title_ko.paragraph_format.line_spacing = 1.30
    p_title_ko.paragraph_format.space_before = Pt(4)
    p_title_ko.paragraph_format.space_after = Pt(6)
    r_tko = p_title_ko.add_run("뉴스 빅데이터와 NMF 기반의 한국형 경제 이슈 다중 국면 탐지 및 다각적 실증 검증")
    set_run_font(r_tko, FONT_GOTHIC, FONT_EN_SANS, size_pt=17, bold=True, char_spacing_pt=-0.5)

    # ① 국문 저자란 (심사용 파일에서는 완전히 삭제)
    if not blind_mode:
        p_auth_ko = doc.add_paragraph()
        p_auth_ko.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_auth_ko.paragraph_format.line_spacing = 1.20
        p_auth_ko.paragraph_format.space_before = Pt(2)
        p_auth_ko.paragraph_format.space_after = Pt(6)
        r_ako = p_auth_ko.add_run("홍길동¹ · 홍동순²* (※ 제출 시 실제 저자 성명 기입 / 산돌명조B 12p, 왼쪽정렬)")
        set_run_font(r_ako, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=12.0, bold=True, char_spacing_pt=-0.5)

    # 영문 제목 (Arial, 12.5pt, 줄간격 120%, 왼쪽정렬, 'A Study on' 미사용)
    p_title_en = doc.add_paragraph()
    p_title_en.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title_en.paragraph_format.line_spacing = 1.20
    p_title_en.paragraph_format.space_before = Pt(2)
    p_title_en.paragraph_format.space_after = Pt(6)
    r_ten = p_title_en.add_run(
        "Multi-Regime Detection of Korean Economic Issues via News Big Data and Non-negative Matrix Factorization: "
        "Methodological and Empirical Validations"
    )
    set_run_font(r_ten, FONT_GOTHIC, FONT_EN_SANS, size_pt=12.5, bold=True)

    # ② 영문 저자 및 소속·직위란 (심사용 파일에서는 완전히 삭제)
    if not blind_mode:
        p_auth_en = doc.add_paragraph()
        p_auth_en.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_auth_en.paragraph_format.line_spacing = 1.20
        p_auth_en.paragraph_format.space_before = Pt(2)
        p_auth_en.paragraph_format.space_after = Pt(2)
        r_aen = p_auth_en.add_run("Kil-Dong Hong¹ · Dong-Soon Hong²* (※ 영문 저자명 기입 / Times New Roman 10.5p)")
        set_run_font(r_aen, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=10.5, bold=True)

        p_affil = doc.add_paragraph()
        p_affil.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_affil.paragraph_format.line_spacing = 1.20
        p_affil.paragraph_format.space_before = Pt(0)
        p_affil.paragraph_format.space_after = Pt(10)
        r_aff = p_affil.add_run(
            "¹[직위 기입: 예, Undergraduate Student / Professor], School of AI Convergence, Korean Bible University, Seoul, 01757 Korea\n"
            "²*[직위 기입: 예, Professor], School of AI Convergence, Korean Bible University, Seoul, 01757 Korea"
        )
        set_run_font(r_aff, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.0)

    # 국문 요약 헤더 (고딕B 10pt, 줄간격 160%, 왼쪽정렬)
    p_abs_ko_hdr = doc.add_paragraph()
    p_abs_ko_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_abs_ko_hdr.paragraph_format.line_spacing = 1.60
    p_abs_ko_hdr.paragraph_format.space_before = Pt(4)
    p_abs_ko_hdr.paragraph_format.space_after = Pt(2)
    r_akh = p_abs_ko_hdr.add_run("요  약")
    set_run_font(r_akh, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True, char_spacing_pt=-0.2)

    # 국문 요약 본문 (명조 9.2pt, 들여쓰기 10pt, 줄간격 130%, 양쪽정렬)
    abs_ko_paragraphs = [
        (
            "본 연구는 2021년 1월부터 2026년 7월까지(총 67개월) 국내 3대 주요 경제 일간지(매일경제, 서울경제, 한국경제)에서 수집한 "
            "931,709건의 경제 뉴스 기사 코퍼스를 대상으로 비지도 학습 기법인 비음수 행렬 분해(NMF)와 고정 표준화 체계를 구축하여 "
            "한국 경제의 잠재 이슈 국면을 탐지하고, 시장·거시 지표 및 대중 검색 빅데이터와의 관계를 실증 분석하였다. 특히 미래 정보 "
            "누수(Data Leakage)를 원천 차단하기 위해 학습 기간(2021.01~2024.12, 48개월) 전용 어휘 사전(22,193개 단어)과 IDF, NMF 기저 "
            "행렬(H, 14개 잠재 토픽)을 고정하여 테스트 기간(2025.01~2026.07, 19개월)으로 확장 투영하는 엄격한 표본 외(Strict Out-of-Sample) "
            "파이프라인을 확립하였다. 도출된 토픽 중 사전 정의된 매핑 규칙을 통과한 6대 유효 국면(금리·물가, 부동산, 첨단산업(전기차·배터리 중심), "
            "시황, 기업실적, 자본거래)을 체계화하였으며, 기존 선행연구의 단일 대표 국면(Single Dominant) 선택 방식과 학습 고정 z점수 기반의 "
            "다중 국면 활성화 체계(z ≥ 0.5)를 정량적으로 비교하였다."
        ),
        (
            "실증 분석 결과는 다음과 같다. 첫째, 한국 경제 뉴스는 전체 67개월의 58.21%(39개월; 학습 기간 66.67%, 테스트 기간 36.84%)에서 "
            "2개 이상의 경제 국면이 동시에 활성화되었다. 단일 대표 국면 방식으로 표현을 제한할 경우, 다중 국면 방식에서 관측된 활성 국면 "
            "신호 중 43.75%(112건 중 49건; 학습 47.19%, 테스트 30.43%)가 별도 국면으로 표현되지 않는다. 이는 표현상 정보 보존성에 관한 "
            "결과이며 예측 정확도의 개선을 의미하지는 않는다. 둘째, 67개월 전체 표본에서 6대 국면 표준화 점수와 코스피 과거 변동성 정규화 "
            "월간 수익률(kospi_ret_std) 간의 Newey-West HAC OLS 동행 회귀분석(maxlags=3) 결과, 모형 설명력 R² = 16.19% (Adj-R² = 7.81%, "
            "HAC F = 4.6833, p = 0.000573)를 기록하였으며, '금리·물가'(β = -0.7418, 원시 p = 0.0004, Holm p = 0.0024) 및 "
            "'자본거래'(β = -0.5299, 원시 p = 0.0026, Holm p = 0.0129) 국면이 당월 주가 수익률 충격과 유의한 음(-)의 동행 관계를 형성함을 "
            "확인하였다. 셋째, 292주간의 네이버 데이터랩(Datalab) 주별 상대 검색 지수와의 1차 차분 교차 검증(유효 291주) 및 Newey-West "
            "HAC(maxlags=4, 24개 검정 Holm 보정) 검정 결과, 전체 기간 동시점(h=0)에서 '금리·물가' ↔ 금리 검색(r = +0.5026, HAC p_holm = 1.29×10⁻¹³), "
            "'시황' ↔ 국내증시 검색(r = +0.4868, HAC p_holm = 9.06×10⁻⁵), '금리·물가' ↔ 금리+물가 검색(r = +0.3217, HAC p_holm = 5.07×10⁻⁶), "
            "'기업실적' ↔ 기업실적 검색(r = +0.2795, HAC p_holm = 3.48×10⁻⁵)의 양(+)의 동행 관계가 유의하였으며, 표본 외(Strict OOS) 테스트 "
            "기간(N=82주)에서는 24개 검정 HAC Holm 보정 후 '시황' ↔ 국내증시 검색(r = +0.4984, HAC p_holm = 0.0432)과 '기업실적' ↔ 기업실적 "
            "검색(r = +0.4718, HAC p_holm = 0.0011) 두 쌍에서 통계적 유의성이 재현되었다('금리·물가' ↔ 금리 검색은 테스트 기간 r = +0.3397, "
            "HAC 원시 p = 0.0170이나 HAC Holm 보정 후 p_holm = 0.3575로 유의수준을 충족하지 못함). 본 연구는 인과 추론이나 시장 예측력에 대한 "
            "과장된 주장을 배제하고, 다중 국면 표현의 정보 보존성과 이종 빅데이터 간 동시점 교차 동조성을 검증한 재현 가능한 텍스트 마이닝 "
            "프레임워크를 제시한다."
        ),
    ]
    for txt in abs_ko_paragraphs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.30
        p.paragraph_format.first_line_indent = Pt(10)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(txt)
        set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2, char_spacing_pt=-0.3)

    # 영문 ABSTRACT 헤더 (고딕B 10pt, 줄간격 160%, 왼쪽정렬)
    p_abs_en_hdr = doc.add_paragraph()
    p_abs_en_hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_abs_en_hdr.paragraph_format.line_spacing = 1.60
    p_abs_en_hdr.paragraph_format.space_before = Pt(6)
    p_abs_en_hdr.paragraph_format.space_after = Pt(2)
    r_aeh = p_abs_en_hdr.add_run("ABSTRACT")
    set_run_font(r_aeh, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True, char_spacing_pt=-0.2)

    # 영문 ABSTRACT 본문 (Times New Roman 8.5pt, 들여쓰기 10pt, 줄간격 130%, 양쪽정렬)
    abs_en_paragraphs = [
        (
            "This study establishes an unsupervised text-mining framework based on Non-negative Matrix Factorization (NMF) to detect "
            "latent economic issue regimes from 931,709 economic news articles collected from three major Korean business dailies "
            "(Maeil Business Newspaper, Seoul Economic Daily, and Korea Economic Daily) from January 2021 to July 2026 (67 months). "
            "To strictly prevent future information leakage, we constructed a deterministic Strict Out-of-Sample (OOS) pipeline where "
            "the vocabulary (22,193 terms), IDF weights, and NMF basis matrix (H, 14 latent topics) were fitted exclusively on the "
            "training period (2021.01–2024.12, 48 months) and projected onto the test period (2025.01–2026.07, 19 months). Six valid "
            "regimes passing pre-specified mapping rules—Interest Rate & Inflation, Real Estate, Advanced Industry (EV/Battery-centered), "
            "Stock Market, Corporate Earnings, and Capital Transactions—were established, and a multi-regime activation framework based "
            "on training-fixed standardized scores (z ≥ 0.5) was compared against single-dominant regime representations."
        ),
        (
            "Empirical findings are threefold: First, Korean economic news exhibited concurrent activation of two or more regimes in "
            "58.21% of the 67 months (39/67 months; 66.67% in training and 36.84% in out-of-sample testing). When representation is "
            "restricted to a single dominant regime per month, 43.75% (49 out of 112; 47.19% in training and 30.43% in testing) of the "
            "active regime signals observed under the multi-regime framework are not represented as separate regimes; this reflects "
            "representational information preservation rather than predictive accuracy. Second, in-sample Newey-West HAC OLS regression "
            "(maxlags=3) on volatility-standardized monthly KOSPI returns (kospi_ret_std, N=67) yielded R² = 16.19% (Adj-R² = 7.81%, "
            "HAC F = 4.6833, p = 0.000573), with 'Interest Rate & Inflation' (β = -0.7418, raw p = 0.0004, Holm p = 0.0024) and "
            "'Capital Transactions' (β = -0.5299, raw p = 0.0026, Holm p = 0.0129) showing statistically significant negative "
            "contemporaneous associations. Third, weekly first-differenced cross-validation across 291 differenced weeks against Naver "
            "Datalab relative search indices with Newey-West HAC standard errors (maxlags=4, 24-test Holm correction) confirmed "
            "significant contemporaneous (h=0) co-movement over the full period for Interest Rates (r = +0.5026, HAC p_holm = 1.29×10⁻¹³), "
            "Stock Market (r = +0.4868, HAC p_holm = 9.06×10⁻⁵), Combined Macro (r = +0.3217, HAC p_holm = 5.07×10⁻⁶), and Corporate "
            "Earnings (r = +0.2795, HAC p_holm = 3.48×10⁻⁵). In the Strict OOS test period (N=82 weeks), contemporaneous co-movement "
            "remained statistically significant after 24-test HAC Holm correction for two pairs: 'Stock Market' ↔ Domestic Stock search "
            "(r = +0.4984, HAC p_holm = 0.0432) and 'Corporate Earnings' ↔ Corporate Earnings search (r = +0.4718, HAC p_holm = 0.0011), "
            "whereas 'Interest Rate & Inflation' ↔ Interest Rate search showed r = +0.3397 (raw HAC p = 0.0170) but did not remain "
            "significant after HAC Holm adjustment (HAC p_holm = 0.3575). Avoiding unverified claims of market forecasting or causality, "
            "this study provides a reproducible text-mining methodology for multi-regime representation and cross-source concordance analysis."
        ),
    ]
    for txt in abs_en_paragraphs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.30
        p.paragraph_format.first_line_indent = Pt(10)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(txt)
        set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.5, char_spacing_pt=-0.2)

    # 국문 키워드 (고딕 10pt 레이블 + 명조 8.5pt 내용, 줄간격 156%, 왼쪽정렬)
    p_kw_ko = doc.add_paragraph()
    p_kw_ko.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_kw_ko.paragraph_format.line_spacing = 1.56
    p_kw_ko.paragraph_format.space_before = Pt(6)
    p_kw_ko.paragraph_format.space_after = Pt(2)
    r_kw_lbl = p_kw_ko.add_run("키워드 : ")
    set_run_font(r_kw_lbl, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True)
    r_kw_txt = p_kw_ko.add_run("경제 뉴스 빅데이터, 텍스트 마이닝, 토픽 모델링, 비음수 행렬 분해(NMF), 다중 국면 활성화, 표본 외(Strict OOS) 검증, 네이버 데이터랩, 교차 데이터 검증")
    set_run_font(r_kw_txt, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.5)

    # 영문 Keywords (Arial 10pt 레이블 + Times New Roman 8.5pt 내용, 알파벳순)
    p_kw_en = doc.add_paragraph()
    p_kw_en.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_kw_en.paragraph_format.line_spacing = 1.56
    p_kw_en.paragraph_format.space_before = Pt(0)
    p_kw_en.paragraph_format.space_after = Pt(12)
    r_kwe_lbl = p_kw_en.add_run("Keywords : ")
    set_run_font(r_kwe_lbl, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True)
    r_kwe_txt = p_kw_en.add_run(
        "Cross-Source Validation, Economic News Big Data, Multi-Regime Activation, Naver Datalab, "
        "Non-negative Matrix Factorization (NMF), Strict Out-of-Sample Validation, Text Mining, Topic Modeling"
    )
    set_run_font(r_kwe_txt, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.5)

    # 제1면 하단 출판사/교신저자/Open Access 블록
    add_horizontal_rule(doc, sz=4, color="000000", space_before=8, space_after=2)
    p_rec = doc.add_paragraph()
    p_rec.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rec.paragraph_format.space_before = Pt(0)
    p_rec.paragraph_format.space_after = Pt(2)
    r_rec = p_rec.add_run("Received XX Month 2026,          Revised XX Month 2026,          Accepted XX Month 2026 (출판사에서 작성)")
    set_run_font(r_rec, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.0)

    # ③ 교신저자 각주 (심사용 파일에서는 완전히 삭제)
    if not blind_mode:
        add_horizontal_rule(doc, sz=4, color="000000", space_before=0, space_after=2)
        p_corr = doc.add_paragraph()
        p_corr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_corr.paragraph_format.space_before = Pt(0)
        p_corr.paragraph_format.space_after = Pt(2)
        r_corr = p_corr.add_run(
            "* Corresponding Author: Dong-Soon Hong (E-mail: author@bible.ac.kr, Tel: +82-2-XXX-XXXX) "
            "[※ 실제 교신저자 정보 기입]\n"
            "Professor, School of AI Convergence, Korean Bible University, Seoul, 01757 Korea"
        )
        set_run_font(r_corr, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.0)

    add_horizontal_rule(doc, sz=4, color="000000", space_before=0, space_after=2)
    p_oa = doc.add_paragraph()
    p_oa.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_oa.paragraph_format.line_spacing = 1.15
    p_oa.paragraph_format.space_before = Pt(0)
    p_oa.paragraph_format.space_after = Pt(0)
    r_oa = p_oa.add_run(
        "Open Access  http://doi.org/10.6109/jkiice.2026.30.X.XXX          pISSN: 2234-4772\n"
        "This is an Open Access article distributed under the terms of the Creative Commons Attribution Non-Commercial License "
        "(http://creativecommons.org/licenses/by-nc/3.0/) which permits unrestricted non-commercial use, distribution, and reproduction "
        "in any medium, provided the original work is properly cited. Copyright © The Korea Institute of Information and Communication Engineering."
    )
    set_run_font(r_oa, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=7.5, color_rgb=(60, 60, 60))

    # 양식 필수 지침: "서론부터는 페이지를 바꾸어서 작성하시기 바랍니다"
    doc.add_page_break()

    # =========================================================================
    # 본문 헬퍼 함수들
    # =========================================================================
    def add_chapter_heading(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=11.0, bold=True)
        return p

    def add_section_heading(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True)
        return p

    def add_subsection_heading(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=9.5, bold=True)
        return p

    def add_body_p(text, indent=True, bold_prefix=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.50
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        if indent:
            p.paragraph_format.first_line_indent = Pt(10)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            set_run_font(rb, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2, bold=True)
        r = p.add_run(text)
        set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2)
        return p

    def add_bullet_p(bold_prefix, text, left_indent_pt=12):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.45
        p.paragraph_format.left_indent = Pt(left_indent_pt)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            set_run_font(rb, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2, bold=True)
        r = p.add_run(text)
        set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2)
        return p

    def add_equation_p(eq_text, eq_num):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.rows[0].cells[0].width = Mm(150)
        tbl.rows[0].cells[1].width = Mm(20)
        p0 = tbl.rows[0].cells[0].paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(4)
        p0.paragraph_format.space_after = Pt(4)
        r0 = p0.add_run(eq_text)
        set_run_font(r0, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.5, italic=True, bold=True)

        p1 = tbl.rows[0].cells[1].paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(4)
        p1.paragraph_format.space_after = Pt(4)
        r1 = p1.add_run(f"({eq_num})")
        set_run_font(r1, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2)
        return tbl

    def add_table_caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.30
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=8.5, bold=True)
        return p

    def add_table_note(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run(text)
        set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.0, color_rgb=(40, 40, 40))
        return p

    def populate_table(headers, rows, col_widths_mm, left_align_cols=(0,)):
        tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_jkiice_table_borders(tbl)

        for c_idx, h_text in enumerate(headers):
            cell = tbl.rows[0].cells[c_idx]
            cell.width = Mm(col_widths_mm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.20
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(h_text)
            set_run_font(r, FONT_GOTHIC, FONT_EN_SERIF, size_pt=8.0, bold=True)
            set_cell_background(cell, "F2F4F8")
            set_cell_margins(cell, top=60, bottom=60, left=70, right=70)

        for r_idx, r_data in enumerate(rows, start=1):
            is_summary_row = (r_idx == len(rows) and ("합계" in r_data[0] or "적합도" in r_data[0] or "결합 검정" in r_data[0]))
            for c_idx, val in enumerate(r_data):
                cell = tbl.rows[r_idx].cells[c_idx]
                cell.width = Mm(col_widths_mm[c_idx])
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx in left_align_cols else WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.line_spacing = 1.20
                p.paragraph_format.space_before = Pt(1.5)
                p.paragraph_format.space_after = Pt(1.5)
                is_bold = is_summary_row or val.startswith("**")
                clean_val = val.replace("**", "")
                r = p.add_run(clean_val)
                set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.0, bold=is_bold)
                if is_summary_row:
                    set_cell_background(cell, "F8FAFC")
                set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
        return tbl

    # =========================================================================
    # Ⅰ. 서  론
    # =========================================================================
    add_chapter_heading("Ⅰ. 서  론")
    add_body_p(
        "현대 경제 시스템은 통화정책 긴축, 인플레이션 압력, 글로벌 무역 마찰, 그리고 첨단 산업 구조 재편 등 다양한 거시경제 요인들이 "
        "복합적으로 상호작용하며 전개된다[1-3]. 이러한 거시 환경의 변화는 주식시장과 외환시장의 단기 가격 변동을 수반할 뿐만 아니라, "
        "기업의 자본 조달과 경제 주체의 기대 형성에 영향을 미친다[4-6]. 이에 따라 정책 당국과 시장 참여자들은 거시경제 주요 어젠다의 변화를 "
        "정량적으로 파악하고 다원적 이슈 구조를 추적하기 위한 텍스트 정보 분석 체계를 필요로 하고 있다."
    )
    add_body_p(
        "전통적인 거시경제 통계인 국내총생산(GDP), 소비자물가지수(CPI), 산업생산지수 등은 집계 및 공표 시차(Publication Lag)를 수반하며[3, 5], "
        "사후적인 통계 수정(Revision)이 발생할 수 있어 고빈도로 변화하는 경제 현안을 실시간으로 요약하는 데 제약이 있다[2]. 이를 보완하기 위해 "
        "최근 정보처리 및 금융 빅데이터 분야에서는 매일 대량으로 생성되는 비정형 뉴스 텍스트(News Text) 빅데이터로부터 경제정책불확실성(EPU)[1], "
        "뉴스심리지수(NSI)[5], 잠재 토픽 관심도(Topic Attention)[2, 3]를 도출하여 거시 현안을 추적하려는 연구가 진행되어 왔다."
    )
    add_body_p(
        "그러나 비정형 텍스트 기반 거시 이슈 국면 분석을 다룬 기존 연구들은 정보 표현 및 실증 검증 측면에서 다음과 같은 세 가지 한계를 나타낸다."
    )
    add_body_p(
        "첫째, 단일 대표 국면(Single Dominant Regime) 선택 방식으로 인한 복합 이슈 표현의 제한이다. 기존 연구들은 각 시점에서 출현 비중이 "
        "1위인 토픽만을 해당 시점의 대표 국면으로 지정하거나 단일 지수로 축약하는 방식을 주로 채택하였다[2, 7]. 그러나 현실 경제에서는 "
        "고물가·금리 인상 충격과 부동산 시장 침체, 또는 증시 변동과 기업실적 공시가 같은 달에 동시에 부각되는 복합 현상이 빈번하다. 월별 대표 "
        "국면 1개만을 선택하여 표현을 제한할 경우, 동일한 시점에 임계 수준 이상으로 활성화된 제2·제3의 유효 국면 신호가 별도의 국면으로 "
        "표현되지 못하는 한계가 발생한다."
    )
    add_body_p(
        "둘째, 표본 외(Out-of-Sample) 검증 설계의 미흡과 미래 정보 누수(Data Leakage)이다. 많은 텍스트 마이닝 연구들이 전체 분석 기간의 모든 "
        "문서를 한꺼번에 투입하여 TF-IDF 어휘 사전을 구축하고 토픽 모델(LDA, NMF) 및 표준화 모수를 적합한 뒤, 그 결과를 과거와 미래 시점에 "
        "동일하게 적용한다. 이는 평가 기간에 아직 발생하지 않은 미래의 어휘 분포와 토픽 구조가 과거 시점의 지표 산출에 반영되는 정보 누수 문제를 야기한다."
    )
    add_body_p(
        "셋째, 이종 빅데이터를 활용한 주별 차분 교차 검증 및 시계열 정상성 통제의 부족이다. 비지도 학습으로 추출된 뉴스 토픽 지표가 언론사의 "
        "보도 관행에 그치는지, 아니면 일반 대중의 검색 관심도와도 동시점에 동조하는지를 독립된 외부 데이터로 교차 검증한 연구가 부족하였다. "
        "또한 시계열 수준값(Level)의 비정상성(단위근 추세)을 제거하지 않은 채 단순 상관계수를 보고할 경우, 공통 추세에 의한 가짜 상관(Spurious "
        "Correlation)을 유의한 관계로 오인할 위험이 크다."
    )
    add_body_p(
        "이에 본 연구는 2021년 1월부터 2026년 7월까지(총 67개월) 국내 3대 경제 일간지(매일경제, 서울경제, 한국경제)에서 수집한 931,709건의 "
        "경제 뉴스 기사 코퍼스를 바탕으로 비음수 행렬 분해(NMF)를 적용하여 한국형 경제 이슈 국면 탐지 체계를 구축한다. 특히 학습 기간"
        "(2021.01~2024.12, 48개월)과 테스트 기간(2025.01~2026.07, 19개월)을 엄격히 분리한 결정론적 표본 외(Strict OOS) 파이프라인을 설계하고, "
        "시계열 변환 및 다중검정 보정을 거친 보수적 실증 검증을 수행한다. 본 연구가 규명하고자 하는 핵심 연구 질문(Research Questions)은 다음과 같다:"
    )
    add_bullet_p(
        "• RQ1 (단일 국면과 다중 국면 활성화 비교): ",
        "한국 경제 뉴스에서 다중 국면 동시 활성화 방식(z ≥ 0.5)과 단일 대표 국면 선택 방식은 활성 국면 신호 표현에서 어떠한 정량적 차이를 보이는가?"
    )
    add_bullet_p(
        "• RQ2 (Phase 5.6 Strict OOS 기반 시장·경제 지표 관계 분석): ",
        "학습 기간 고정 모델로부터 도출된 6대 유효 국면 비중은 코스피 수익률 충격 및 기준금리 변동과 어떠한 동행·시차 관계를 보이며, 조기경보 규칙으로서의 한계는 무엇인가?"
    )
    add_bullet_p(
        "• RQ3 (네이버 검색 데이터를 이용한 주별 교차 데이터 검증): ",
        "뉴스 국면 점유율의 주간 변동은 네이버 데이터랩(Datalab) 상대 검색 관심도의 주간 변동과 Newey-West HAC 및 다중검정 보정 하에서 유의한 동시점 동조화를 나타내는가?"
    )

    # =========================================================================
    # Ⅱ. 관련 연구 및 이론적 배경
    # =========================================================================
    add_chapter_heading("Ⅱ. 관련 연구 및 이론적 배경")
    add_section_heading("2.1 뉴스 텍스트 기반 거시경제 지표 및 시장 반응")
    add_body_p(
        "텍스트 데이터를 계량경제학적 분석에 도입한 대표적 연구인 Baker, Bloom, and Davis[1]는 주요 신문 기사에서 '경제', '정책', '불확실성' "
        "관련 키워드의 출현 빈도를 집계하여 경제정책불확실성(EPU) 지수를 개발하였다. 이후 텍스트 분석 연구는 단어 빈도 계측에서 확률적·선형대수적 "
        "토픽 모델링으로 확장되었다. Bybee et al.[2]은 월스트리트저널(WSJ) 기사 약 80만 건을 토픽 모델링으로 분석하여 거시경제 주제 비중(Attention) "
        "시계열을 도출하고 실물 경기 변동과의 관련성을 분석하였다. Thorsrud[3]는 일간 비즈니스 신문의 토픽 비중 시계열을 동적 요인 모형(DFM)과 "
        "결합하여 경기 동행 지수를 구축하였다."
    )
    add_body_p(
        "국내에서도 텍스트 마이닝을 활용한 거시경제 지표 연구가 진행되었다. 서범석 외[5]는 뉴스심리지수(NSI)를 개발하여 소비자심리지수(CCSI) "
        "등과의 관계를 분석하였고, 김수현·박기영[6]과 송원호·강규호[16]는 경제 기사 텍스트를 활용하여 거시 심리 및 통화정책 관련 반응을 연구하였다. "
        "그러나 기존 연구들은 주로 단일 지수나 단일 대표 국면 할당에 초점을 맞추었으며, 복수의 경제 이슈가 동일 월에 동시에 활성화되는 다중 국면 "
        "구조와 단일 대표 국면 선택 시 미표현되는 신호의 비중을 학습·테스트 분할 환경에서 정량화한 연구는 드물다."
    )

    add_section_heading("2.2 비음수 행렬 분해(NMF)와 고정 특징 투영")
    add_body_p(
        "토픽 모델링 기법 중 비음수 행렬 분해(NMF)는 문서-어휘 가중치 행렬 V ∈ R₊^(N×M)를 두 개의 저차원 비음수 행렬 W ∈ R₊^(N×K)와 "
        "H ∈ R₊^(K×M)의 곱으로 근사 분해하는 기법이다[8]:"
    )
    add_equation_p("V ≈ W × H    (단, W ≥ 0, H ≥ 0)", 1)
    add_body_p(
        "여기서 W는 각 문서가 K개 잠재 토픽에 갖는 가중치 행렬이며, H는 각 토픽이 M개 어휘에 갖는 단어 가중치 행렬이다. NMF는 비음수 제약"
        "(Non-negativity Constraint)을 통해 가산적 부분 기반 표현(Part-based Representation)을 산출하며, 고정된 초기화(nndsvd)와 좌표 하강법"
        "(Coordinate Descent)을 사용할 때 결정론적 재현성을 확보할 수 있다."
    )
    add_body_p(
        "특히 표본 외(Strict OOS) 평가를 수행할 때, 학습 기간(Train) 문서에서 적합된 기저 행렬 H_train과 IDF 가중치를 고정(Freeze)한 뒤, "
        "테스트 기간(Eval)의 새로운 문서 행렬 V_eval에 대해 W_eval ≈ argmin_{W ≥ 0} ||V_eval - W H_train||_F를 투영함으로써 평가 기간의 "
        "미래 텍스트 정보가 토픽 기저 형성에 개입하는 것을 원천 차단할 수 있다."
    )

    add_section_heading("2.3 시계열 정상성, Newey-West HAC 공분산 및 다중검정 보정")
    add_body_p(
        "거시경제 및 뉴스·검색 시계열 데이터는 자기상관(Autocorrelation)과 이분산성(Heteroskedasticity)을 수반하며[11, 15], 수준값(Level) "
        "시계열이 단위근 추세를 공유할 경우 실제 단기 동조성이 없더라도 높은 상관계수가 산출되는 가짜 상관(Spurious Correlation)이 발생한다."
    )
    add_body_p(
        "본 연구에서는 단위근 추세에 의한 착시를 방지하기 위해 상관 및 교차 검증 시 지수 수준값 대신 월간 수익률·차분 또는 주간 1차 차분"
        "(First Difference) 변환 시계열을 사용한다. 또한 회귀분석 및 주별 상관 검정 시 Newey and West[12]의 HAC(Heteroskedasticity and "
        "Autocorrelation Consistent) 견고 공분산 추정량(Bartlett 커널)을 적용한다:"
    )
    add_equation_p("V_HAC = (X'X)⁻¹ [ Γ₀ + Σ_{l=1}^{q} (1 - l/(q+1)) (Γ_l + Γ_l') ] (X'X)⁻¹", 2)
    add_body_p(
        "아울러 복수의 국면·지표·시차를 동시에 검정할 때 발생하는 제1종 오류(Family-wise Error Rate) 팽창을 통제하기 위해, 모든 다중 가설 "
        "패밀리에 대해 Holm-Bonferroni 단계적 보정(p_holm)을 적용하고 p_holm < 0.05 기준을 충족한 경우에만 다중검정 보정 후 통계적으로 유의한 "
        "결과로 판정한다."
    )

    # =========================================================================
    # Ⅲ. 연구 방법 및 Strict OOS 시스템 설계
    # =========================================================================
    add_chapter_heading("Ⅲ. 연구 방법 및 Strict OOS 시스템 설계")
    add_section_heading("3.1 경제 뉴스 코퍼스 및 전처리")
    add_body_p(
        "텍스트 데이터는 한국언론진흥재단 빅카인즈(BigKinds)를 통해 2021년 1월 1일부터 2026년 7월 31일까지(총 67개월) 국내 3대 경제 일간지인 "
        "매일경제, 서울경제, 한국경제의 경제 섹션 기사 전량을 수집하였다. 저작권 보호로 본문 200자 절단이 적용되는 원문 요약 대신, 기사 전문에서 "
        "추출된 형태소 분석 명사 키워드 필드(keywords)를 사용하였다. 수집된 원시 데이터 931,709건은 결측치 및 중복(article_id) 검사 후 "
        "931,709건 전량이 분석 코퍼스로 확정되었다(어휘 사전에 매칭되는 토큰이 전혀 없는 11건만 월별 비중 분모에서 제외됨)."
    )
    add_body_p("거시금융 시장 지표는 한국은행 경제통계시스템(ECOS) 등을 통해 월별 패널(monthly_panel.csv, 67개월)로 구축하였다:")
    add_bullet_p("1) 코스피 월간 로그수익률 (kospi_ret): ", "kospi_ret_t = 100 × ln(KOSPI_t / KOSPI_{t-1}) (%)")
    add_bullet_p(
        "2) 과거 변동성 정규화 월간 수익률 (kospi_ret_std): ",
        "kospi_ret_std_t = kospi_ret_t / kospi_vol12_{t-1}, 여기서 kospi_vol12_t = SD(kospi_ret_{t-11:t})는 직전 12개월 월간 수익률의 표본 표준편차이다. "
        "이는 변동성 수준 자체가 아니라 과거 변동성 크기로 스케일을 조정한 월간 수익률 충격 지표이다."
    )
    add_bullet_p(
        "3) 거시 변동 지표: ",
        "한국은행 기준금리 월간 변화폭(base_rate_diff = BASE_RATE_t - BASE_RATE_{t-1}), 소비자심리지수 월간 변화분(ccsi_diff), 원/달러 환율 월간 로그수익률(usdkrw_ret)."
    )
    add_body_p(
        "대중 검색 관심도 대조를 위해서는 네이버 데이터랩(Datalab) Search Trend API를 통해 고정 조회 기간(2016-01-01 ~ 2026-07-31) 동안 각 "
        "검색어 그룹을 공통 앵커 키워드('은행')와 함께 조회하여 일별 원시 상대지수(score, 그룹 내 최대 검색일=100 기준)와 앵커 대비 상대지수"
        "(score_rel = score / anchor_score)를 수집하고, 뉴스 코퍼스와 동일한 ISO 8601 주차(iso_yw) 기준 주별 평균으로 집계하였다."
    )

    add_section_heading("3.2 TF-IDF와 NMF 기반 경제 이슈 토픽 추출")
    add_body_p(
        "본 연구는 미래 정보 누수를 원천 차단하기 위해 전체 67개월을 학습 기간(Train: 2021-01 ~ 2024-12, 48개월, 기사 643,095건)과 표본 외 "
        "테스트 기간(Eval OOS: 2025-01 ~ 2026-07, 19개월, 기사 288,614건)으로 고정 분할하였다(RUN_PHASE5_6_20261027_184959). 모든 텍스트 특징 "
        "선택과 모델 적합은 학습 기간(48개월) 내부에서만 수행되었다:"
    )
    add_bullet_p(
        "1) 어휘 사전(Vocabulary): ",
        "학습 기간 643,095건 기사에서 최소 문서빈도 MIN_DF = 200, 최대 문서빈도 비율 MAX_DF_RATIO = 0.15, 상한 30,000개 조건을 적용하고 "
        "(-DF, 토큰 사전순)으로 정렬하여 최종 22,193개 어휘를 확정하였다."
    )
    add_bullet_p(
        "2) IDF 및 NMF 적합 표본: ",
        "학습 기간 48개월에서 월별 3,000건씩 층화 비복원 추출(seed=42)한 144,000건의 학습 표본에 대해 TfidfTransformer와 NMF(n_components=14, "
        "init='nndsvd', solver='cd', max_iter=400, random_state=42)를 단 1회 적합하여 기저 행렬 H_train (14 × 22,193)을 고정하였다."
    )
    add_bullet_p(
        "3) 전 기간 변환 및 월별·주별 집계: ",
        "고정된 어휘 사전, IDF, H_train에 전체 문서를 transform 방식으로만 투영하여 문서별 토픽 가중치 W_{i,k}를 산출하고, 유효 문서(Σ_k W_{i,k} > 0)의 "
        "정규화 토픽 비중 w_{i,k} = W_{i,k} / Σ_{k=0}^{13} W_{i,k}를 월별 및 ISO 주차별로 평균하였다."
    )

    add_section_heading("3.3 14개 토픽에서 6개 유효 경제 국면으로의 매핑")
    add_body_p(
        "토픽 번호에 대한 자의적 개입을 배제하기 위해, 사전 구축된 8개 경제 도메인 키워드 사전(DOMAIN_SPEC)과 학습 기저 행렬 H_train만을 "
        "입력으로 하는 규칙 기반 자동 매핑 함수(map_topics)를 적용하였다. 각 토픽에서 1위 도메인의 어휘 가중치 점유율(best_share)이 "
        "0.01(MIN_MAP_SHARE) 미만이면 residual(잔차), 2위 도메인과의 질량 비율(second_mass / best_mass)이 0.90(MASS_TIE_RATIO) 이상이면 "
        "ambiguous(경합·모호), 두 조건을 모두 통과하면 1위 도메인으로 assigned(할당) 판정하였다. 학습 기간 14개 잠재 토픽(토픽 0 ~ 13)의 "
        "실제 상위 키워드와 매핑 결과는 다음과 같다:"
    )
    add_bullet_p(
        "• macro (금리·물가, 1개 토픽): ",
        "토픽 1 (물가, 금리, 경제, Fed, 인상, 인플레이션, 통화, 경기, 연방, 중앙은행, 정책, 기준금리 — macro 점유율 0.0472, 2위/1위 비율 0.191, 신뢰도 0.809)"
    )
    add_bullet_p(
        "• realestate (부동산, 2개 토픽): ",
        "토픽 2 (대출, 주택, 금리, 부동산, 은행, 아파트, 전세, 집계, 포인트, 매매, 집값, 담보 — realestate 점유율 0.0284, 2위 hhdebt와의 비율 0.664) "
        "+ 토픽 3 (단지, 분양, 가구, 아파트, 지상, 지하, 전용, 인근, 청약, 조성, 주택, 입주 — realestate 점유율 0.0403, 2위/1위 비율 0.009)"
    )
    add_bullet_p(
        "• aichip (첨단산업(전기차·배터리 중심), 1개 토픽): ",
        "토픽 12 (차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, SUV, 성능, 기아, 충전, 배터리, 전기 — aichip 점유율 0.0125, 2위/1위 비율 0.027, 우세 세부 그룹 전기차배터리)"
    )
    add_bullet_p(
        "• market (시황, 2개 토픽): ",
        "토픽 4 (종목, 매수, 외국인, 지수, 순매도, 주가, 하락, 삼성전자, 증시, 상위, 시가, 코스피 — market 점유율 0.0343, 2위/1위 비율 0.381) "
        "+ 토픽 13 (코스닥, 출발, 개장, 마감, 코스피, 거래일, 종료, 포인트, 상장, 공모가, 하락, 보통주추가상장 — market 점유율 0.2651, 2위/1위 비율 0.081)"
    )
    add_bullet_p(
        "• earnings (기업실적, 1개 토픽): ",
        "토픽 7 (영업, 이익, 전년, 영업이익, 실적, 매출액, 공시, 연결, 감소, 영업익, 순이익, 분기 — earnings 점유율 0.0189, 2위/1위 비율 0.181)"
    )
    add_bullet_p(
        "• capital (자본거래, 1개 토픽): ",
        "토픽 6 (상장, 주식, 투자자, 펀드, 자산, 지분, 보유, 자금, 수익, 운용, 주주, IB, 인수, ETF, 공모, 매각, 발행, IPO — capital 점유율 0.0222, 2위/1위 비율 0.234)"
    )
    add_bullet_p(
        "• 미형성 국면 (unrepresented / NaN, 2개 도메인): ",
        "가계대출(hhdebt)은 토픽 2에서 realestate에 차순위(질량비 0.664)로 흡수되어 독립 토픽을 형성하지 못하였으며, 대외통상(trade)은 토픽 0(점유율 0.0012 < 0.01)과 "
        "토픽 8(aichip과 경합비 0.951 ≥ 0.90)이 임계 규칙을 통과하지 못하여 미형성 처리되었다."
    )
    add_bullet_p(
        "• 비할당 잔차·경합 토픽 (residual / ambiguous, 6개 토픽): ",
        "토픽 0(경영, 환경, 사회, ESG, 지배구조, 탄소 — residual), 토픽 5(브랜드, 고객, 상품, 구매, 출시, 매장, 할인 — residual), "
        "토픽 8(공장, 수출, 중국, 제조, 반도체, 확보, 유럽, 소재, 장비, 배터리 — trade 1위·aichip 2위 경합비 0.951로 ambiguous), "
        "토픽 9(현지시간, 마켓, 글로벌마켓, 달러, 플랫폼, 해외, CEO, 주가, 테슬라, 뉴욕, 애플, 머스크 — aichip 1위·market 2위 경합비 0.906으로 ambiguous), "
        "토픽 10(지적, 방안, 제도, 조치, 시행, 위원회, 국회, 규정, 개정 — residual), 토픽 11(분야, AI, 협력, 혁신, 인공지능, 구축, 역량, 교육, 스타트업, 디지털, 플랫폼, 데이터, 솔루션 — "
        "1위 aichip 점유율 0.0088 < 0.01로 residual) 등 6개 토픽의 비중 합은 residual_share로 집계되었다."
    )
    add_body_p(
        "기존 코드의 KEYWORD_SETS['AI반도체'](aichip) 검색어 분류체계는 4개 세부 그룹(인공지능, 반도체, 빅테크인프라, 전기차배터리)을 묶어 "
        "구성되었다. 학습 기간 NMF 적합 결과, 인공지능 관련 어휘가 모인 토픽 11은 영문 단일 토큰 'AI'가 한글 위주 사전 키워드에 포함되지 않아 "
        "도메인 점유율(0.88%)이 최소 기준(1.0%)에 미달(residual)하였고, 반도체·수출 중심의 토픽 8과 해외 빅테크 중심의 토픽 9는 각각 trade 및 "
        "market 도메인과의 질량비가 0.90을 초과하여 ambiguous로 분류되었다. 반면 주요 키워드가 차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, "
        "탑재, SUV, 성능, 기아, 충전, 배터리, 전기 등에 집중된 토픽 12는 사전 내 전기차배터리 세부 그룹의 지지를 받아 유일하게 aichip 식별자에 "
        "매핑되었다(supported_ev_battery_only). 본 연구는 사후적인 토픽 재할당이나 규칙 변경을 배제하기 위해 코드 식별자(aichip)와 모델 매핑"
        "(토픽 12)을 그대로 유지하되, 실제 포착된 토픽의 의미를 반영하여 논문 내 국면 명칭을 '첨단산업(전기차·배터리 중심)'으로 표기한다. "
        "또한 이러한 매핑이 AI·반도체 산업 전반에 대한 의미 타당성을 입증하는 것은 아니라는 점을 명확히 한계로 규정한다."
    )

    add_section_heading("3.4 학습 기간 고정 다중 국면 활성화 체계 (z ≥ 0.5)")
    add_body_p(
        "각 유효 국면 d의 월별 점유율 s_{d,t}에 대해, 미래 정보 누수를 차단하기 위해 학습 기간(2021.01~2024.12, 48개월)만의 표본 평균 "
        "μ_{d,train}과 표본 표준편차 σ_{d,train}(ddof=1)을 모수로 고정하여 표준화 점수를 산출하였다:"
    )
    add_equation_p("z_{d,t} = (s_{d,t} - μ_{d,train}) / σ_{d,train}", 3)
    add_body_p(
        "테스트 기간(2025.01~2026.07, 19개월)에서도 테스트 표본의 평균·표준편차를 다시 계산하지 않고 학습 기간 고정 모수(μ_{d,train}, σ_{d,train})를 "
        "그대로 적용하였으며, z_{d,t} ≥ 0.5를 충족하는 모든 국면을 해당 월의 활성 국면으로 정의하였다."
    )

    # =========================================================================
    # Ⅳ. 실증 분석 결과
    # =========================================================================
    add_chapter_heading("Ⅳ. 실증 분석 결과")
    add_section_heading("4.1 6대 유효 경제 국면 분포 및 기술통계")
    add_body_p(
        "phase5_6_train_only_regime_monthly.csv에서 산출된 6대 유효 국면 및 잔차 비중의 학습 기간(48개월) 고정 표준화 모수와 구간별 활성 개월 수 분포는 표 1과 같다."
    )

    add_table_caption("Table 1. Training-Period Standardization Parameters (2021.01–2024.12, N=48) and Active Month Counts (z ≥ 0.5) Across Sample Splits.")
    t1_headers = [
        "국면 표시 명칭 (실질 포착 내용)",
        "코드 (Slug)",
        "할당 토픽 (K=14)",
        "학습 평균 μ_train (%, N=48)",
        "학습 표준편차 σ_train (%p, N=48)",
        "활성화 임계 비중 (z≥0.5, %)",
        "전체 활성 월수 (N=67)",
        "학습 활성 월수 (N=48)",
        "테스트 활성 월수 (N=19)",
    ]
    t1_rows = [
        ["**부동산** (전월세·청약분양)", "realestate", "[2, 3]", "12.54", "0.70", "12.89", "18 (26.9%)", "16 (33.3%)", "2 (10.5%)"],
        ["**자본거래** (IPO·공모주·M&A)", "capital", "[6]", "8.66", "0.71", "9.02", "22 (32.8%)", "17 (35.4%)", "5 (26.3%)"],
        ["**금리·물가** (통화정책·물가)", "macro", "[1]", "6.67", "1.26", "7.30", "13 (19.4%)", "12 (25.0%)", "1 (5.3%)"],
        ["**시황** (국내외 증시 마감·수급)", "market", "[4, 13]", "6.16", "0.37", "6.35", "25 (37.3%)", "16 (33.3%)", "9 (47.4%)"],
        ["**첨단산업(전기차·배터리 중심)**", "aichip", "[12]", "6.05", "0.42", "6.26", "16 (23.9%)", "14 (29.2%)", "2 (10.5%)"],
        ["**기업실적** (매출·영업이익 공시)", "earnings", "[7]", "5.63", "1.13", "6.19", "18 (26.9%)", "14 (29.2%)", "4 (21.1%)"],
        ["(미형성 국면: 가계대출·대외통상)", "hhdebt, trade", "—", "NaN", "NaN", "—", "—", "—", "—"],
        ["(비할당 잔차·경합 토픽 합계)", "residual", "[0,5,8,9,10,11]", "54.30", "1.27", "—", "—", "—", "—"],
        ["**할당 6대 국면 합계 / 활성 신호 총합**", "—", "**8개 토픽**", "**45.70**", "—", "—", "**112건**", "**89건**", "**23건**"],
    ]
    populate_table(t1_headers, t1_rows, [38, 17, 17, 16, 16, 16, 17, 17, 16], left_align_cols=(0,))
    add_table_note(
        "주: 표 1의 평균 비중(μ_train)과 표준편차(σ_train, ddof=1)는 Strict OOS 표준화 공식 z_{d,t} = (s_{d,t} - μ_{d,train})/σ_{d,train}에 사용된 "
        "학습 기간(2021.01~2024.12, 48개월) 통계량이며, 활성화 임계 비중은 μ_{d,train} + 0.5σ_{d,train}이다. 참고로 전체 67개월(2021.01~2026.07) "
        "평균 비중은 realestate 12.28%, capital 8.71%, macro 6.59%, market 6.24%, aichip 5.96%, earnings 5.54%, residual 54.69%이며, 테스트 기간"
        "(2025.01~2026.07, 19개월) 평균 비중은 realestate 11.62%, capital 8.81%, macro 6.41%, market 6.43%, aichip 5.75%, earnings 5.31%, residual 55.67%이다."
    )
    add_body_p(
        "표 1에서 확인되듯, 학습 기간 기준 6대 할당 국면의 평균 비중 합계는 45.70%이며 6개 비할당·경합 토픽이 54.30%의 잔차 비중(residual_share)을 "
        "차지한다. 개별 국면의 전체 67개월 중 활성 월수(z_{d,t} ≥ 0.5)는 금리·물가 13개월(19.4%)부터 시황 25개월(37.3%)까지 분포하며, 6대 국면의 "
        "활성 신호 총합은 전체 기간 112건(학습 89건 + 테스트 23건)이다."
    )

    add_section_heading("4.2 단일 국면과 다중 국면 활성화 비교 (RQ1)")
    add_body_p(
        "다중 국면 활성화 체계와 단일 대표 국면(Argmax) 선택 방식이 월별 활성 국면 신호를 어떻게 다르게 표현하는지 single_vs_multi_metrics.csv, "
        "single_vs_multi_monthly.csv, single_vs_multi_regime_combinations.csv를 통해 정량적으로 비교하였다. 비교 대상 방식은 다음 세 가지이다:"
    )
    add_bullet_p("• 방식 A-1 (Unconstrained Argmax): ", "임계값 조건 없이 매월 6개 국면 중 z_{d,t}가 가장 높은 1개 국면을 무조건 대표 국면으로 지정.")
    add_bullet_p("• 방식 A-2 (Hurdle Argmax): ", "매월 최대 점수 국면이 max_d z_{d,t} ≥ 0.5를 충족할 때만 해당 1개 국면을 대표 국면으로 지정하고, 미달 시 비활성(none)으로 분류.")
    add_bullet_p("• 방식 B (Multi-Regime Activation, 제안): ", "매월 z_{d,t} ≥ 0.5를 충족하는 모든 국면을 동시에 활성 국면으로 지정.")

    add_table_caption("Table 2. Quantitative Comparison of Single-Dominant vs. Multi-Regime Activation Representations.")
    t2_headers = [
        "분석 구간 (Sample Split)",
        "개월 수 (N)",
        "월평균 활성 국면 수",
        "0개 활성 (none) 월수",
        "1개 활성 월수",
        "2개 활성 월수",
        "3개 활성 월수",
        "≥2개 다중 활성 월수",
        "다중 방식 활성 신호 수",
        "단일 방식 표현 신호 수",
        "단일 제한 시 미표현 신호 수",
    ]
    t2_rows = [
        ["**Full Sample (2021-01~2026-07)**", "67", "1.672", "4 (5.97%)", "24 (35.82%)", "29 (43.28%)", "10 (14.93%)", "**39 (58.21%)**", "112", "63", "**49 (43.75%)**"],
        ["**Train Period (2021-01~2024-12)**", "48", "1.854", "1 (2.08%)", "15 (31.25%)", "22 (45.83%)", "10 (20.83%)", "**32 (66.67%)**", "89", "47", "**42 (47.19%)**"],
        ["**Eval OOS Period (2025-01~2026-07)**", "19", "1.211", "3 (15.79%)", "9 (47.37%)", "7 (36.84%)", "0 (0.00%)", "**7 (36.84%)**", "23", "16", "**7 (30.43%)**"],
    ]
    populate_table(t2_headers, t2_rows, [32, 10, 14, 14, 15, 15, 15, 16, 13, 13, 13], left_align_cols=(0,))
    add_body_p("표 2 및 국면 조합 분석 결과는 다음 네 가지 사실을 보여준다:")
    add_bullet_p(
        "1) 복합 국면 활성화의 빈도: ",
        "전체 67개월 중 58.21%(39개월)에서 월 2개 이상의 경제 국면이 동시에 임계값(z_{d,t} ≥ 0.5)을 상회하였다(2개 활성 29개월[43.28%], 3개 활성 10개월[14.93%], "
        "4개 이상 활성 0개월). 학습 기간(48개월)에서는 다중 활성화 비율이 66.67%(32개월)였으며, 표본 외 테스트 기간(19개월)에서도 36.84%(7개월)에서 2개 국면이 동시에 활성화되었다."
    )
    add_bullet_p(
        "2) 단일 대표 국면 표현의 구조적 차이(43.75%): ",
        "단일 대표 국면 방식으로 표현을 제한할 경우, 다중 국면 방식에서 관측된 활성 국면 신호 중 43.75%(112건 중 49건; 학습 기간 89건 중 42건[47.19%], 테스트 기간 "
        "23건 중 7건[30.43%])가 별도 국면으로 표현되지 않는다. 또한 모든 국면이 z_{d,t} < 0.5인 비활성 4개월(전체 5.97%: 학습 1개월[2021-07], 테스트 3개월[2025-05, 2026-04, 2026-06])에 대해 "
        "무제약 Argmax(방식 A-1)는 임계값 미달 국면을 강제로 할당하는 반면, Hurdle Argmax(방식 A-2)와 다중 국면 방식(방식 B)은 이를 비활성(none) 상태로 구분한다."
    )
    add_bullet_p(
        "3) 실제 관측된 동시 활성화 국면 조합: ",
        "single_vs_multi_regime_combinations.csv 및 single_vs_multi_monthly.csv 확인 결과, 전체 67개월에서 가장 빈번히 관측된 2국면 단독 조합은 "
        "market;earnings(5개월: 학습 3, 테스트 2)였으며, 이어서 aichip;capital(4개월: 학습 4), macro;realestate(3개월: 학습 3), realestate;capital(3개월: 학습 3), "
        "earnings;capital(3개월: 학습 2, 테스트 1) 순으로 나타났다. 3국면 동시 활성 월(10개월)까지 포함한 쌍별 동시 활성화 빈도를 시기별로 보면, 2022~2023년 고물가·금리 인상기에는 "
        "2022년 중 macro와 realestate의 동시 활성화가 5개월(2국면 단독 macro;realestate 3개월[2022-05, 2022-07, 2022-11] + 3국면 조합 2개월[2022-06, 2022-10]), "
        "2022~2023년 중 macro와 market의 동시 활성화가 5개월(2국면 단독 macro;market 2개월[2022-09, 2023-09] + 3국면 조합 3개월[2022-06, 2022-10, 2023-08]) 관측된 반면, "
        "같은 2022~2023년 기간 중 macro와 capital이 동시에 활성화된 달은 없었다(0개월; 전 기간 중 macro와 capital의 동시 활성화는 2024-12의 macro;market;capital 1개월뿐임)."
    )
    add_bullet_p(
        "4) 해석 범위의 명확한 제한: ",
        "위 43.75% 수치는 월별 국면 표현 방식에 따른 표현상 정보 보존성(Representational Information Preservation)에 관한 결과이며, 다중 국면 방식이 시장 수익률이나 거시지표의 예측 정확도를 개선한다는 것을 입증하지 않는다."
    )

    add_section_heading("4.3 Phase 5.6 Strict OOS 기반 시장·경제 지표 관계 분석 (RQ2)")
    add_subsection_heading("4.3.1 코스피 수익률 충격에 대한 Newey-West HAC OLS 동행 회귀분석")
    add_body_p(
        "학습 기간 고정 NMF 투영으로 도출된 6대 유효 국면 표준화 점수(z_*)를 설명변수로 하고, 과거 변동성 정규화 월간 코스피 수익률(kospi_ret_std)을 "
        "종속변수로 하여 전체 67개월(2021-01 ~ 2026-07, 결측치 없음) 표본에서 Newey-West HAC 견고 회귀분석(Bartlett 커널, maxlags=3)을 수행한 "
        "결과(verification_ols_results.csv, 모형 ID Phase56_StrictOOS_ret_std_67m)는 표 3과 같다."
    )

    add_table_caption("Table 3. Newey-West HAC OLS Estimation on Volatility-Standardized Monthly KOSPI Return (kospi_ret_std, N=67, maxlags=3).")
    t3_headers = [
        "설명변수 (Variable)",
        "회귀계수 (β)",
        "HAC 표준오차 (SE)",
        "t-통계량 (z)",
        "95% 신뢰구간 (CI)",
        "원시 p-값 (p_value_raw)",
        "Holm 보정 p-값 (6변수)",
        "VIF",
    ]
    t3_rows = [
        ["const (상수항)", "+0.0631", "0.1357", "+0.465", "[-0.2029, +0.3291]", "0.6419", "—", "—"],
        ["**z_macro (금리·물가)**", "**-0.7418**", "**0.2093**", "**-3.543**", "**[-1.1521, -0.3315]**", "**0.0004**", "**0.0024**", "1.95"],
        ["**z_capital (자본거래)**", "**-0.5299**", "**0.1758**", "**-3.015**", "**[-0.8744, -0.1854]**", "**0.0026**", "**0.0129**", "1.91"],
        ["z_realestate (부동산)", "-0.2082", "0.1185", "-1.757", "[-0.4403, +0.0240]", "0.0789", "0.3155", "1.27"],
        ["z_market (시황)", "-0.1437", "0.0898", "-1.600", "[-0.3197, +0.0323]", "0.1096", "0.3289", "1.16"],
        ["z_aichip (첨단산업(전기차·배터리 중심))", "-0.2583", "0.1802", "-1.434", "[-0.6115, +0.0948]", "0.1517", "0.3289", "1.33"],
        ["z_earnings (기업실적)", "-0.1143", "0.1698", "-0.673", "[-0.4471, +0.2185]", "0.5008", "0.5008", "1.27"],
    ]
    populate_table(t3_headers, t3_rows, [45, 16, 18, 16, 28, 18, 18, 11], left_align_cols=(0,))
    add_table_note(
        "주: 모형 적합도 N = 67 (2021-01~2026-07, 결측치 0건), df_model = 6, df_resid = 60, R² = 0.161879 (16.19%), Adjusted R² = 0.078067 (7.81%). "
        "Newey-West HAC (maxlags=3) 결합 검정 F(6, 60) = 4.683257 (p = 0.000573), Wald χ² = 28.099544."
    )
    add_body_p("표 3의 주요 결과는 다음과 같다:")
    add_bullet_p(
        "1) 모형 설명력 및 결합 유의성: ",
        "6대 국면 동행 회귀모형은 과거 변동성 정규화 월간 수익률(kospi_ret_std) 변동의 R² = 16.19% (Adj-R² = 7.81%)를 설명하며, Newey-West HAC 결합 검정 통계량 "
        "F = 4.6833 (p = 0.000573)으로 유의하였다. 모든 설명변수의 분산팽창계수(VIF)는 1.16 ~ 1.95로 다중공선성 문제가 없었다(학습 48개월 단독 적합 시에는 R² = 24.55%, Adj-R² = 13.50%, HAC F = 2.9842, p = 0.0164)."
    )
    add_bullet_p(
        "2) 개별 국면 다중검정 보정 결과: ",
        "6개 국면 변수에 대한 Holm-Bonferroni 다중검정 보정 결과, z_macro(금리·물가: β = -0.7418, HAC SE = 0.2093, p_raw = 0.0004, p_holm = 0.0024)와 "
        "z_capital(자본거래: β = -0.5299, HAC SE = 0.1758, p_raw = 0.0026, p_holm = 0.0129) 두 변수만 유의한 음(-)의 동행 관계를 보였다."
    )
    add_bullet_p(
        "3) 해석 경계: ",
        "본 회귀분석은 67개월 전체 표본에서 당월(t) 뉴스 국면 점유율과 당월(t) 수익률 충격 간의 관계를 추정한 표본 내 동시점 설명 회귀(In-sample Contemporaneous Regression)이며, 미래 수익률 예측력을 의미하지 않는다."
    )

    add_subsection_heading("4.3.2 월별 거시지표 시차 상관 및 조기경보 규칙 평가의 구분")
    add_body_p(
        "verification_correlation_lag_results.csv에서 6대 유효 국면과 차분·수익률 변환된 4대 거시·금융 지표(kospi_ret, base_rate_diff, ccsi_diff, usdkrw_ret) 간 "
        "5개 시차(h ∈ {-2, -1, 0, +1, +2}, h > 0은 뉴스 선행, h < 0은 경제지표 선행)의 총 120개 검정 패밀리에 대해 단일 Holm 보정을 수행한 결과는 다음과 같다:"
    )
    add_bullet_p(
        "• kospi_ret과의 시차 상관: ",
        "macro ↔ kospi_ret 상관은 h=0(N=67, r=-0.1598, p_raw=0.1965, p_holm=1.000) 및 h=+1(N=66, r=+0.0734, p_raw=0.5583, p_holm=1.000) 모두 비유의하였으며, "
        "6대 국면 전체에서 120개 검정 Holm 보정 후 유의한 단일 변수 주가 수익률 시차 상관은 존재하지 않았다(p_holm ≥ 0.4304)."
    )
    add_bullet_p(
        "• base_rate_diff(한국은행 기준금리 월간 변화폭)와의 시차 상관: ",
        "120개 검정 중 Holm 보정 후 유의한(p_holm < 0.05) 조합은 총 4개로, ① macro ↔ base_rate_diff (h=-2, 금리 2개월 선행, N=65): r = +0.4886 (p_raw = 3.63×10⁻⁵, p_holm = 0.0044), "
        "② macro ↔ base_rate_diff (h=+1, 뉴스 1개월 선행, N=66): r = +0.4749 (p_raw = 5.60×10⁻⁵, p_holm = 0.0067), ③ macro ↔ base_rate_diff (h=0, 동월 동행, N=67): r = +0.4580 "
        "(p_raw = 9.74×10⁻⁵, p_holm = 0.0115), ④ capital ↔ base_rate_diff (h=0, 동월 동행, N=67): r = -0.4260 (p_raw = 3.25×10⁻⁴, p_holm = 0.0380)이다. "
        "h=-2(금리 변동 선행) 상관이 h=+1(뉴스 선행)보다 더 크게 나타난 것은 2022~2023년 연속 금리 인상기 동안 통화정책 결정과 언론 보도가 상호 피드백하며 동조화(Co-movement)되었음을 보여준다."
    )
    add_body_p(
        "또한 verification_warning_performance_results.csv에서 검증된 월별 조기경보 규칙(향후 1~2개월 예측창 t+1, t+2 평가; 마지막 2개월을 제외한 전체 평가 가능 기간 "
        "2021-01~2026-05 [N=65개월] 및 테스트 평가 가능 기간 2025-01~2026-05 [N=17개월])의 성과와 한계는 평가 기준별로 다음과 같이 엄격히 구분된다:"
    )
    add_bullet_p(
        "1) 일반 주가 하락 경고 (kospi_ret_{t+1} < 0% 또는 kospi_ret_{t+2} < 0%): ",
        "과거 8국면 기반의 원래 2국면 결합 규칙(z_macro ≥ 0.5 | z_hhdebt ≥ 0.5)은 65개월 동안 28회 경고를 발생시켜 정밀도 67.86%(TP=19, FP=9, FN=26, TN=11, Recall 42.22%, Specificity 55.00%)를 기록하였으나, "
        "동일 기간 실제 하락창 자연발생률 69.23%(45/65)보다 -1.37%p 낮아 변별력이 없었으며, Phase 5.6 Strict OOS에서는 hhdebt 국면이 미형성(NaN)되어 원래 규칙 자체를 평가할 수 없다. "
        "hhdebt 결측에 따라 z_macro ≥ 0.5 단독으로 축소한 Phase 5.6 대체 규칙(Phase5.6_StrictOOS_MacroOnly)은 전체 65개월에서 경고 13건 중 9건 적중(Precision 69.23%, Recall 20.00%, TP=9, FP=4, FN=36, TN=16)으로 "
        "자연발생률(69.23%)과 차이가 없었으며(0.00%p), Strict OOS 테스트 평가 가능 기간(17개월, 2025-01~2026-05)에서는 경고 1건(2026-03)이 발생했으나 실제 하락 사건창(9건)을 포착하지 못하였다"
        "(TP=0, FP=1, FN=9, TN=7, Precision 0.00%, Recall 0.00%, Specificity 87.50%, F1 = 0.000, MCC = -0.2582)."
    )
    add_bullet_p(
        "2) 코스피 급락(kospi_ret_t ≤ -3.0%, 전체 67개월 중 16건) 사전 포착: ",
        "과거 2국면 결합 규칙은 16건 중 11건(68.75%: hhdebt 단독 8건, macro 3건)에서 직전 1~2개월 경고가 켜졌으나, Phase 5.6의 z_macro ≥ 0.5 단독 대체 규칙은 2022년 급락 3건"
        "(2022-06, 2022-09, 2022-12)만 포착(3/16 = 18.75%)하였고 테스트 기간 급락 3건(2025-11, 2026-03, 2026-07)은 포착하지 못하였다(0/3 = 0.00%)."
    )
    add_bullet_p(
        "3) 한국은행 기준금리 인상(base_rate_diff_t > 0, 전체 11건) 사전 포착: ",
        "직전 1~2개월 z_macro ≥ 0.5 기준 포착률은 전체 7/11 = 63.64%였으나, 포착된 7건은 모두 z_macro ≥ 0.5가 11개월 연속 지속된 2022-04~2023-01 연속 인상기"
        "(7/7 = 100%, 직전 인상의 사후 보도와 차기 인상 사전 경고창이 중첩되는 구간)에 집중되었고, 긴축 전환 초기 인상 3건(2021-08, 2021-11, 2022-01)과 표본 외 재인상 1건(2026-07)은 모두 미탐지(0/4 = 0.00%)되었다."
    )
    add_body_p(
        "따라서 본 연구는 월별 뉴스 국면 지표를 주가나 금리 전환점의 사전 예측(Early-Warning Forecasting) 도구로 주장하지 않으며, 당월 시장 충격과의 "
        "동행 설명력(표 3) 및 대중 검색 관심도와의 동시점 교차 검증(표 4)에 실증적 초점을 둔다."
    )

    add_section_heading("4.4 네이버 검색 데이터를 이용한 주별 교차 데이터 검증 (RQ3)")
    add_body_p(
        "뉴스 코퍼스에서 도출된 주별 국면 점유율(news_share_*)과 네이버 데이터랩 주별 상대 검색 지수(score_rel) 간의 교차 타당성을 검증하기 위해, "
        "292개 ISO 주차(2020-W53 ~ 2026-W31: 학습 209주[2020-W53~2024-W52], 테스트 83주[2025-W01~2026-W31]) 패널을 구축하였다. 비정상 시계열의 공통 추세로 "
        "인한 가짜 상관을 배제하기 위해 각 구간(Train, Eval OOS, Full) 내부에서 뉴스 점유율과 검색 지수에 각각 주간 1차 차분(First Difference)을 "
        "적용하였으며(차분 후 h=0 유효 표본 수: 학습 N=208, 테스트 N=82, 전체 N=291; 시차 h=±1 유효 표본 수: 학습 N=207, 테스트 N=81, 전체 N=290), 시계열 "
        "자기상관과 이분산성을 통제하기 위해 표준화 차분 회귀에 Newey-West HAC 표준오차(Bartlett 커널, maxlags=4)를 적용하였다. 다중검정 보정은 "
        "각 구간별로 사전 지정된 8개 뉴스-검색 매칭 쌍 × 3개 시차(h ∈ {-1, 0, +1}) = 총 24개 검정 패밀리에 대해 Holm-Bonferroni 보정(hac_p_holm)을 "
        "수행하였다. news_search_hac_results.csv의 전체 검증 결과는 표 4와 같다."
    )

    add_table_caption("Table 4. Weekly First-Difference Cross-Validation Between News Regimes and Naver Datalab Relative Search Indices (news_search_hac_results.csv, Newey-West HAC maxlags=4, 24-Test Holm Adjustment per Split).")
    t4_headers = [
        "뉴스 국면 ↔ 네이버 검색 그룹 (pair_label)",
        "시차 (h)",
        "학습 구간 (2021~2024, N=208/207) r (HAC p_holm)",
        "테스트 구간 (2025~2026, N=82/81) r (HAC p_holm)",
        "전체 구간 (2021~2026, N=291/290) r (HAC p_holm)",
        "다중검정 보정 후 판정 (HAC p_holm < 0.05)",
    ]
    t4_rows = [
        ["**1. 시황 뉴스 ↔ 국내증시 검색** (market)", "**h = 0 (동행)**", "**+0.6478 (1.14×10⁻⁷)**", "**+0.4984 (0.0432)**", "**+0.4868 (9.06×10⁻⁵)**", "**학습·테스트·전체 동행 유의**"],
        ["(market ↔ search_market)", "h = -1 (검색 1주 선행)", "-0.2448 (0.1783)", "-0.3461 (0.0244)", "-0.2822 (0.0026)", "1주 시차 음(-)의 반전"],
        ["", "h = +1 (뉴스 1주 선행)", "-0.1338 (1.0000)", "+0.0442 (1.0000)", "-0.0144 (1.0000)", "비유의"],
        ["**2. 기업실적 뉴스 ↔ 기업실적 검색** (earnings)", "**h = 0 (동행)**", "**+0.2160 (0.0143)**", "**+0.4718 (0.0011)**", "**+0.2795 (3.48×10⁻⁵)**", "**학습·테스트·전체 동행 유의**"],
        ["(earnings ↔ search_earnings)", "h = -1 (검색 1주 선행)", "-0.1654 (0.1603)", "+0.0444 (1.0000)", "-0.1160 (0.7033)", "비유의"],
        ["", "h = +1 (뉴스 1주 선행)", "-0.0638 (1.0000)", "-0.2033 (1.0000)", "-0.0968 (1.0000)", "비유의"],
        ["**3. 금리·물가 뉴스 ↔ 금리 검색** (macro)", "**h = 0 (동행)**", "**+0.5511 (2.57×10⁻¹³)**", "+0.3397 (0.3575)†", "**+0.5026 (1.29×10⁻¹³)**", "**학습·전체 동행 유의** (테스트 보정 후 비유의)"],
        ["(macro ↔ search_macro_interest)", "h = -1 (검색 1주 선행)", "-0.2885 (9.48×10⁻⁵)", "-0.1246 (1.0000)", "-0.2588 (3.00×10⁻⁵)", "학습·전체 1주 시차 음(-)의 반전"],
        ["", "h = +1 (뉴스 1주 선행)", "-0.2556 (2.15×10⁻⁵)", "-0.2221 (0.7698)", "-0.2453 (4.11×10⁻⁶)", "학습·전체 1주 시차 음(-)의 반전"],
        ["**4. 금리·물가 뉴스 ↔ 금리+물가 검색** (macro)", "**h = 0 (동행)**", "**+0.4978 (3.28×10⁻¹¹)**", "+0.2254 (1.0000)", "**+0.3217 (5.07×10⁻⁶)**", "**학습·전체 동행 유의** (테스트 비유의)"],
        ["(macro ↔ search_macro_combined)", "h = -1 (검색 1주 선행)", "-0.3060 (8.93×10⁻⁵)", "+0.0420 (1.0000)", "-0.1311 (0.0100)", "학습·전체 1주 시차 음(-)의 반전"],
        ["", "h = +1 (뉴스 1주 선행)", "-0.1104 (1.0000)", "+0.0839 (1.0000)", "-0.0174 (1.0000)", "비유의"],
        ["**5. 금리·물가 뉴스 ↔ 물가 검색** (macro)", "h = 0 (동행)", "+0.0658 (1.0000)", "+0.1355 (1.0000)", "+0.0776 (1.0000)", "비유의 (h=-1,+1 모두 p_holm ≥ 0.1406)"],
        ["**6. 자본거래 뉴스 ↔ 공모주 검색** (capital)", "h = 0 (동행)", "+0.1437 (1.0000)", "+0.1658 (1.0000)", "+0.1348 (0.9527)", "비유의 (h=-1,+1 모두 p_holm = 1.0000)"],
        ["**7. 부동산 뉴스 ↔ 부동산 검색** (realestate)", "h = 0 (동행)", "+0.1288 (1.0000)", "-0.0768 (1.0000)", "+0.1008 (1.0000)", "비유의 (h=-1,+1 모두 p_holm ≥ 0.5117)"],
        ["**8. 첨단산업(전기차·배터리 중심) 뉴스 ↔ AI반도체 검색**", "h = 0 (동행)", "-0.0357 (1.0000)", "+0.1417 (1.0000)", "+0.0609 (1.0000)", "비유의 (h=-1,+1 모두 p_holm = 1.0000)"],
    ]
    populate_table(t4_headers, t4_rows, [42, 22, 26, 26, 26, 28], left_align_cols=(0, 5))
    add_table_note(
        "주: h=0은 동일 ISO 주차 내 뉴스 점유율 차분과 검색 지수 차분 간 상관(N=208, 82, 291)이며, h=+1은 t주 뉴스 차분과 t+1주 검색 차분, h=-1은 t주 뉴스 차분과 t-1주 검색 차분 간 상관(N=207, 81, 290)이다. "
        "괄호 안 수치는 각 구간 내 24개 검정에 대한 Newey-West HAC(maxlags=4) Holm 보정 p-값(hac_p_holm)이다. †테스트 구간(Eval OOS, N=82)의 '금리·물가 뉴스 ↔ 금리 검색'(h=0)은 "
        "r = +0.3397, HAC 원시 p = 0.0170이나 24개 검정 HAC Holm 보정 후 p_holm = 0.3575로 유의수준(0.05)을 초과하므로 다중검정 보정 후 유의 결과로 분류하지 않는다."
    )
    add_body_p("표 4의 분석 결과는 다음과 같이 요약된다:")
    add_bullet_p(
        "1) 표본 외 테스트 기간에서도 HAC Holm 보정 후 재현된 동시점(h=0) 동조 관계: ",
        "테스트 기간(N=82주)에서 24개 검정 HAC Holm 보정 후 통계적으로 유의한 동시점 양(+)의 관계는 ① '시황 뉴스 ↔ 국내증시 검색'(r = +0.4984, HAC p_raw = 0.0020, HAC p_holm = 0.0432)과 "
        "② '기업실적 뉴스 ↔ 기업실적 검색'(r = +0.4718, HAC p_raw = 4.49×10⁻⁵, HAC p_holm = 0.0011) 두 쌍으로 확인되었다. 이 두 쌍은 학습 기간(r = +0.6478 [p_holm = 1.14×10⁻⁷], r = +0.2160 [p_holm = 0.0143])과 "
        "전체 기간(r = +0.4868 [p_holm = 9.06×10⁻⁵], r = +0.2795 [p_holm = 3.48×10⁻⁵]) 모두에서 일관되게 유의하였다."
    )
    add_bullet_p(
        "2) 금리·물가 뉴스와 금리 검색의 구간별 결과 구분: ",
        "'금리·물가 뉴스 ↔ 금리 검색'(h=0)은 학습 기간(r = +0.5511, HAC p_holm = 2.57×10⁻¹³)과 전체 기간(r = +0.5026, HAC p_holm = 1.29×10⁻¹³)에서 가장 강한 동시점 동조성을 나타냈으며, "
        "'금리+물가 통합 검색'(h=0) 역시 학습(r = +0.4978, p_holm = 3.28×10⁻¹¹)과 전체(r = +0.3217, p_holm = 5.07×10⁻⁶)에서 유의하였다. 반면 금리 변동의 빈도가 줄어든 테스트 기간(N=82주)에서 "
        "금리 검색은 r = +0.3397, HAC 원시 p = 0.0170의 양(+)의 상관을 보였으나, 24개 검정에 대한 HAC Holm 보정 후에는 p_holm = 0.3575로 통계적 유의수준을 충족하지 못하였다."
    )
    add_bullet_p(
        "3) 1주 시차(h = ±1)에서의 양(+)의 선행성 부재: ",
        "h = -1(검색 1주 선행) 및 h = +1(뉴스 1주 선행)에서는 모든 국면 쌍에서 유의한 양(+)의 상관이 관찰되지 않았으며, 오히려 급등 직후 차주의 기저효과(평균 회귀)로 인해 '시황'(h=-1)과 '금리'(h=±1)에서 "
        "음(-)의 반전 상관이 나타났다. 이는 뉴스 보도와 대중 검색 관심이 1주 단위의 시차를 두고 한쪽이 다른 쪽을 일방향으로 선행하기보다 동일 주간(h=0) 내에 동시적으로 반응함을 보여준다."
    )
    add_bullet_p(
        "4) 차분 후 비유의 국면(부동산·자본거래·물가·첨단산업)의 원인: ",
        "수준값에서는 완만한 추세를 공유하던 부동산, 공모주(자본거래), 물가 검색은 주간 1차 차분 후 단기 변동 상관이 비유의하였다. 특히 '첨단산업(전기차·배터리 중심) 뉴스(aichip) ↔ AI반도체 검색'"
        "(h=0, r = +0.0609, p_holm = 1.0000)의 비유의성은 3.3절에서 규명한 바와 같이 학습 기간 NMF에서 aichip 식별자에 할당된 토픽 12가 실제로는 전기차·배터리·자동차 어휘 중심으로 구성된 반면, "
        "검색 지수는 생성형 AI·HBM·반도체 전반을 포괄하는 의미적 범위 차이에 기인한다."
    )
    add_bullet_p(
        "5) 공통 앵커('은행') 분모 민감도 점검 (news_search_anchor_sensitivity.csv): ",
        "네이버 데이터랩 상대지수(score_rel = score / anchor_score)는 서로 다른 API 호출 간 스케일 비교를 위해 공통 앵커 키워드('은행')의 상대지수로 나눈 값이다. 공통 분모의 변동이 주간 차분 상관에 미친 영향을 "
        "점검하기 위해 ① 앵커 지수(anchor_score)로 나누지 않은 각 검색 그룹 자체의 원래 상대 검색 지수(score, 단일 API 조회 구간 내 자체 최대값=100 기준 상대 지표)의 주간 1차 차분(Δscore)을 사용한 분석과, "
        "② Δscore_rel 회귀식에 주간 앵커 차분(Δanchor_score)을 통제변수로 추가한 부분회귀 분석을 수행하였다. 분석 결과, 앵커를 나누지 않은 원래 상대 검색 지표(Δscore)의 차분에서도 전체 구간 동시점(h=0)에서 "
        "'금리'(r = +0.5290, HAC p_holm = 3.95×10⁻¹⁶), '시황'(r = +0.5330, HAC p_holm = 1.92×10⁻⁵), '금리+물가'(r = +0.3651, HAC p_holm = 1.30×10⁻⁸), '기업실적'(r = +0.3464, HAC p_holm = 8.26×10⁻⁸) "
        "및 테스트 구간(N=82)의 '시황'(r = +0.5355, HAC p_holm = 0.0327), '기업실적'(r = +0.5508, HAC p_holm = 0.00016)에서 유사한 양(+)의 동행 관계가 일관되게 확인되었다(테스트 구간 '금리'는 r = +0.3461, "
        "HAC p_holm = 0.1615로 동일하게 보정 후 비유의). 다만 네이버 데이터랩의 원래 지수(score) 역시 조회 기간 내 최댓값을 100으로 둔 상대 지표이므로 이를 절대 검색량이나 실제 검색 횟수로 해석할 수 없으며, "
        "API 정규화 구조상 공통 분모나 스케일링의 영향이 완전히 제거되었다고 단정하지 않는다."
    )

    # =========================================================================
    # Ⅴ. 결  론
    # =========================================================================
    add_chapter_heading("Ⅴ. 결  론")
    add_section_heading("5.1 연구 요약 및 학술적 기여")
    add_body_p(
        "본 연구는 2021년 1월부터 2026년 7월까지 수집된 국내 3대 경제 일간지 기사 931,709건을 바탕으로, 미래 정보 누수를 차단한 결정론적 표본 외"
        "(Strict OOS) NMF 파이프라인과 다중 국면 활성화 체계를 구축하고 금융시장 지표 및 네이버 검색 트렌드와의 관계를 검증하였다. 본 연구의 핵심 기여는 다음 세 가지로 요약된다:"
    )
    add_bullet_p(
        "1) 결정론적 Strict OOS 텍스트 마이닝 파이프라인 및 국면 매핑 체계 확립: ",
        "어휘 사전(22,193개), IDF, NMF 기저 행렬(H_train, 14개 토픽), 그리고 국면 표준화 모수(μ_train, σ_train)를 모두 48개월 학습 기간(2021~2024)에서만 적합·고정하고 "
        "19개월 표본 외 테스트 기간(2025~2026.07)으로 투영하는 무누수(Zero-Leakage) 아키텍처와 6대 유효 국면의 동시점 시장 반응 설명력(R² = 16.19%, HAC F = 4.6833, p = 0.000573)을 검증하였다."
    )
    add_bullet_p(
        "2) 단일 국면 대비 다중 국면 활성화의 정보 보존성 정량화: ",
        "한국 경제 뉴스는 전체 67개월 중 58.21%(학습 66.67%, 테스트 36.84%)에서 월 2개 이상의 경제 국면이 동시에 활성화되었으며, 단일 대표 국면 방식으로 표현을 제한할 경우 "
        "다중 국면 방식에서 관측된 활성 국면 신호 중 43.75%(112건 중 49건; 학습 47.19%, 테스트 30.43%)가 별도 국면으로 표현되지 않는다는 점을 실증적으로 규명하였다."
    )
    add_bullet_p(
        "3) 주별 1차 차분 및 Newey-West HAC 기반 뉴스-네이버 검색 데이터 교차 검증: ",
        "단위근 추세를 제거한 주별 1차 차분 시계열(291주)과 24개 검정 HAC Holm 보정을 통해, 전체 기간에서 금리(r = +0.5026, HAC p_holm = 1.29×10⁻¹³), "
        "시황(r = +0.4868, HAC p_holm = 9.06×10⁻⁵), 금리+물가(r = +0.3217, HAC p_holm = 5.07×10⁻⁶), 기업실적(r = +0.2795, HAC p_holm = 3.48×10⁻⁵) 뉴스 점유율과 "
        "네이버 상대 검색 지수 간의 유의한 동시점(h=0) 양(+)의 동조성을 확인하였으며, 특히 시황(r = +0.4984, HAC p_holm = 0.0432)과 기업실적(r = +0.4718, HAC p_holm = 0.0011) "
        "두 국면은 표본 외 테스트 기간(N=82주)에서도 다중검정 보정 후 유의성이 재현됨을 입증하였다."
    )

    add_section_heading("5.2 연구 한계 및 향후 연구")
    add_bullet_p(
        "1) 동시점 설명 관계와 사전 예측력의 엄격한 구분: ",
        "본 연구의 월별 코스피 수익률 회귀분석(R² = 16.19%, HAC F = 4.6833)과 주별 네이버 검색 교차 검증(h=0)은 모두 동시점(Contemporaneous) 동행 관계를 검증한 것이며, "
        "미래 주가나 금리 변동의 인과적 예측력을 입증한 것이 아니다. 실제로 월별 주가 하락 조기경보 평가에서 기존 2국면 규칙의 일반 하락 정밀도(67.86%)는 자연발생률(69.23%)을 상회하지 못했고, "
        "Phase 5.6의 z_macro ≥ 0.5 단독 대체 규칙 역시 테스트 평가 가능 기간(17개월)에서 경고 1건, 적중 0건(TP=0, FP=1)에 그쳤다."
    )
    add_bullet_p(
        "2) 비지도 토픽 매핑의 미형성 국면 및 첨단산업(전기차·배터리 중심)(aichip) 국면의 의미적 한계: ",
        "학습 기간 NMF에서 가계대출(hhdebt)과 대외통상(trade)이 독립 토픽으로 분리되지 못하여 미형성(unrepresented) 처리되었다. 또한 코드 식별자 aichip에 매핑된 토픽 12는 "
        "주요 키워드가 차량, 전기차, 자동차, 현대차, 충전, 배터리 등에 집중되어 있으며, 기존 AI·반도체 검색어 분류체계에 전기차·배터리 세부 그룹이 포함되어 해당 토픽이 매핑되었다"
        "(supported_ev_battery_only). 따라서 본 연구에서는 실제 토픽의 의미를 반영하여 국면 명칭을 첨단산업(전기차·배터리 중심)으로 표기하였으며, 이러한 매핑이 AI·반도체 전반의 의미 타당성을 "
        "입증하는 것은 아니라는 한계를 갖는다. 향후 연구에서는 씨드 단어 가중치를 결합한 준지도(Anchored/Seeded) 토픽 모델링을 통해 도메인 분리도를 개선할 필요가 있다."
    )
    add_bullet_p(
        "3) 기사 단위 인간 평가 미수행에 따른 의미 타당성 검증의 한계: ",
        "본 연구는 비지도 학습으로 도출된 경제 이슈 국면의 의미적 타당성을 독립 평가자의 기사 단위 라벨링을 통해 검증하지 못했다는 한계를 갖는다. 향후 연구에서는 복수의 평가자가 참여하는 "
        "블라인드 다중 라벨 평가를 수행하여 국면별 의미 일치도와 분류 성능을 추가적으로 검증할 필요가 있다."
    )

    # =========================================================================
    # REFERENCES (양식: 고딕 11p 왼쪽정렬 제목 + Times New Roman 8pt 줄간격 150%)
    # =========================================================================
    add_chapter_heading("REFERENCES")
    references = [
        '[1] S. R. Baker, N. Bloom, and S. J. Davis, “Measuring Economic Policy Uncertainty,” The Quarterly Journal of Economics, vol. 131, no. 4, pp. 1593-1636, Nov. 2016. DOI: 10.1093/qje/qjw024.',
        '[2] L. Bybee, B. T. Kelly, A. Manela, and D. Xiu, “Business News and Business Cycles,” The Journal of Finance, vol. 79, no. 5, pp. 2947-2993, Oct. 2024. DOI: 10.1111/jofi.13377.',
        '[3] L. A. Thorsrud, “Words are the New Numbers: A Newsy Coincident Index of the Business Cycle,” Journal of Business & Economic Statistics, vol. 38, no. 2, pp. 393-409, Apr. 2020. DOI: 10.1080/07350015.2018.1506344.',
        '[4] P. C. Tetlock, “Giving Content to Investor Sentiment: The Role of Media in the Stock Market,” The Journal of Finance, vol. 62, no. 3, pp. 1139-1168, Jun. 2007. DOI: 10.1111/j.1540-6261.2007.01232.x.',
        '[5] B. Seo, Y. Lee, and H. Cho, “Constructing and Utilizing a News Sentiment Index (NSI) Using Machine Learning,” National Accounts Review (Bank of Korea), no. 2022-1, pp. 1-32, 2022. (서범석, 이영환, 조형배, “기계학습을 이용한 뉴스심리지수(NSI)의 작성과 활용,” 국민계정리뷰, 제2022-1호, pp. 1-32, 2022.)',
        '[6] S. Kim and K. Park, “A Study on Economic Sentiment and Business Cycles in Korea Using Text Analysis,” Journal of Money & Finance (KIF), vol. 35, no. 3, pp. 1-35, 2021. (김수현, 박기영, “텍스트 분석을 이용한 한국의 경제 심리 및 경기 변동 연구,” 금융연구, 제35권 제3호, pp. 1-35, 2021.)',
        '[7] S. Park and Y. Jung, “Lead-Lag Analysis of Macroeconomic Indicators Using Unstructured News Big Data,” Journal of the Korean Data & Information Science Society, vol. 31, no. 5, pp. 895-909, 2020. (박성호, 정용운, “비정형 뉴스 빅데이터를 활용한 거시경제 지표 선행성 분석,” 한국데이터정보과학회지, 제31권 제5호, pp. 895-909, 2020.)',
        '[8] D. D. Lee and H. S. Seung, “Learning the Parts of Objects by Non-negative Matrix Factorization,” Nature, vol. 401, no. 6755, pp. 788-791, Oct. 1999. DOI: 10.1038/44565.',
        '[9] D. M. Blei, A. Y. Ng, and M. I. Jordan, “Latent Dirichlet Allocation,” Journal of Machine Learning Research, vol. 3, pp. 993-1022, Jan. 2003.',
        '[10] C. Truong, L. Runge, and N. Vayatis, “Selective Review of Offline Change Point Detection Methods,” Signal Processing, vol. 167, 107299, Feb. 2020. DOI: 10.1016/j.sigpro.2019.107299.',
        '[11] J. H. Stock and M. W. Watson, Introduction to Econometrics, 4th ed. New York, NY: Pearson, 2019.',
        '[12] W. K. Newey and K. D. West, “A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix,” Econometrica, vol. 55, no. 3, pp. 703-708, May 1987. DOI: 10.2307/1913610.',
        '[13] J. D. Hamilton, “A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle,” Econometrica, vol. 57, no. 2, pp. 357-384, Mar. 1989. DOI: 10.2307/1912559.',
        '[14] D. Garcia, “Sentiment During Recessions,” The Journal of Finance, vol. 68, no. 3, pp. 1267-1300, Jun. 2013. DOI: 10.1111/jofi.12027.',
        '[15] R. F. Engle, “Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation,” Econometrica, vol. 50, no. 4, pp. 987-1007, Jul. 1982. DOI: 10.2307/1912773.',
        '[16] W. Song and K. Kang, “Analysis of the Financial Market Spillover Effects of Monetary Policy Shocks Using News Text,” The Korean Journal of Economic Studies, vol. 67, no. 4, pp. 5-42, 2019. (송원호, 강규호, “뉴스 텍스트를 활용한 통화정책 충격의 금융시장 파급효과 분석,” 경제학연구, 제67권 제4호, pp. 5-42, 2019.)',
    ]
    for ref in references:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.50
        p.paragraph_format.left_indent = Pt(18)
        p.paragraph_format.first_line_indent = Pt(-18)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(ref)
        set_run_font(r, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.0)

    # ⑤ 저자 약력란 (원문파일에만 포함, 심사용 블라인드 파일에서는 삭제)
    if not blind_mode:
        add_horizontal_rule(doc, sz=6, color="000000", space_before=14, space_after=6)
        bio_tbl = doc.add_table(rows=1, cols=2)
        bio_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        bio_tbl.rows[0].cells[0].width = Mm(30)
        bio_tbl.rows[0].cells[1].width = Mm(140)
        set_jkiice_table_borders(bio_tbl)

        c0 = bio_tbl.rows[0].cells[0]
        c0.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_photo = c0.paragraphs[0]
        p_photo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ph = p_photo.add_run("[저자 사진\nJPEG/JPG 삽입]")
        set_run_font(r_ph, FONT_GOTHIC, FONT_EN_SANS, size_pt=8.0, color_rgb=(100, 100, 100))
        set_cell_margins(c0, 120, 120, 80, 80)

        c1 = bio_tbl.rows[0].cells[1]
        c1.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_bio = c1.paragraphs[0]
        p_bio.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_bio.paragraph_format.line_spacing = 1.35
        r_bname = p_bio.add_run("홍길동 (Kil-Dong Hong)  [※ 원문파일 제출 시 실제 저자 약력 기입 / 산돌고딕M 10p]\n")
        set_run_font(r_bname, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True)
        r_bhist = p_bio.add_run(
            "• 20XX년 X월 : OO대학교 OO학과 (학사/석사/박사 — 각 항목 앞 연도 기재)\n"
            "• 20XX년 X월 ~ 현재 : 한국성서대학교 AI융합학부 (재직/재학사항 기재)\n"
            "• 관심분야 : 텍스트 마이닝, 금융 빅데이터 분석, 머신러닝, 시계열 분석 (산돌고딕L 7.5p)"
        )
        set_run_font(r_bhist, FONT_GOTHIC, FONT_EN_SANS, size_pt=7.5)
        set_cell_margins(c1, 80, 80, 100, 100)

    doc.save(out_path)
    print(f"Saved Word file: {out_path} ({out_path.stat().st_size} bytes, blind_mode={blind_mode})")


if __name__ == "__main__":
    build_jkiice_2026_docx(OUT_SUBMISSION_PATH, blind_mode=False)
    build_jkiice_2026_docx(OUT_BLIND_PATH, blind_mode=True)
