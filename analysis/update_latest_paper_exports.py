#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JKIICE 최종 논문 원고(docs/PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md)를 파싱하여
1) 최신 마크다운(PAPER_DRAFT_JKIICE.md) 동기화
2) JKIICE 2026 공식 투고양식 Word 파일 3종 (.docx) 생성:
   - docs/PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.docx
   - docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx (원문파일)
   - docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx (심사용 블라인드본)
   - docs/PAPER_DRAFT_JKIICE.docx (기본 파일명 동기화)
3) JKIICE 학술지 스타일 PDF 파일 2종 (.pdf) 생성:
   - docs/PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.pdf
   - docs/PAPER_DRAFT_JKIICE.pdf (기본 파일명 동기화)

주의: A-6.1의 protected_hashes_after.csv 검증 대상인
      `docs/PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md`,
      `docs/PAPER_DRAFT_JKIICE_A4_20261106.md`,
      `docs/PAPER_DRAFT_JKIICE_DRAFT_REVISION_20261107.md` 등은 절대 건드리지 않으며,
      `PAPER_DRAFT_JKIICE.md`는 사용자 요청에 따라 최신 최종본으로 업데이트한다.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Mm, Pt, RGBColor

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC_MD = DOCS / "PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md"

FONT_GOTHIC = "맑은 고딕"
FONT_MYEONGJO = "바탕"
FONT_EN_SERIF = "Times New Roman"
FONT_EN_SANS = "Arial"

FONT_REG = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BD = Path(r"C:\Windows\Fonts\malgunbd.ttf")


def clean_latex_to_unicode(text: str) -> str:
    """마크다운 내 LaTeX 수식을 Word/PDF에서 읽기 좋은 유니코드 수식 표현으로 변환한다."""
    s = text
    # Remove display math delimiters
    s = s.replace("$$", "")
    # Common LaTeX commands
    replacements = [
        (r"\text{max\_iter}", "max_iter"),
        (r"\text{tol}", "tol"),
        (r"\text{Adj-}", "Adj-"),
        (r"\text{Adjusted }", "Adjusted "),
        (r"\text{HAC }", "HAC "),
        (r"\text{HAC}", "HAC"),
        (r"\text{train}", "train"),
        (r"\text{eval}", "eval"),
        (r"\text{holm}", "holm"),
        (r"\text{raw}", "raw"),
        (r"\text{mass}", "mass"),
        (r"\text{iter}", "iter"),
        (r"\text{model}", "model"),
        (r"\text{resid}", "resid"),
        (r"\text{kospi\_ret\_std}", "kospi_ret_std"),
        (r"\text{kospi\_ret}", "kospi_ret"),
        (r"\text{kospi\_vol12}", "kospi_vol12"),
        (r"\text{KOSPI}", "KOSPI"),
        (r"\text{BASE\_RATE}", "BASE_RATE"),
        (r"\text{base\_rate\_diff}", "base_rate_diff"),
        (r"\text{base\_rate}", "base_rate"),
        (r"\text{share\_hhdebt}", "share_hhdebt"),
        (r"\text{share\_macro}", "share_macro"),
        (r"\text{score\_rel}", "score_rel"),
        (r"\text{anchor\_score}", "anchor_score"),
        (r"\text{score}", "score"),
        (r"\text{TD@20}", "TD@20"),
        (r"\text{NPMI}", "NPMI"),
        (r"\text{MCC}", "MCC"),
        (r"\text{Wald }", "Wald "),
        (r"\text{bp}", "bp"),
        (r"\text{p}", "p"),
        (r"\text{단, }", "단, "),
        (r"\operatorname{SD}", "SD"),
        (r"\arg\min", "argmin"),
        (r"\max", "max"),
        (r"\mathbb{R}", "ℝ"),
        (r"\ge", "≥"),
        (r"\le", "≤"),
        (r"\ne", "≠"),
        (r"\approx", "≈"),
        (r"\sim", "~"),
        (r"\to", "→"),
        (r"\times", "×"),
        (r"\pm", "±"),
        (r"\in", "∈"),
        (r"\sum", "∑"),
        (r"\ln", "ln"),
        (r"\hat{\beta}", "β̂"),
        (r"\beta", "β"),
        (r"\mu", "μ"),
        (r"\sigma", "σ"),
        (r"\phi", "φ"),
        (r"\kappa", "κ"),
        (r"\chi^2", "χ²"),
        (r"\Delta", "Δ"),
        (r"\Gamma", "Γ"),
        (r"10^{-4}", "10⁻⁴"),
        (r"10^{-5}", "10⁻⁵"),
        (r"10^{-6}", "10⁻⁶"),
        (r"10^{-7}", "10⁻⁷"),
        (r"10^{-8}", "10⁻⁸"),
        (r"10^{-11}", "10⁻¹¹"),
        (r"10^{-12}", "10⁻¹²"),
        (r"10^{-13}", "10⁻¹³"),
        (r"10^{-14}", "10⁻¹⁴"),
        (r"10^{-16}", "10⁻¹⁶"),
        (r"10^{-39}", "10⁻³⁹"),
        (r"R^2", "R²"),
        (r"\|", "||"),
        (r"\left[", "["),
        (r"\right]", "]"),
        (r"\left(", "("),
        (r"\right)", ")"),
        (r"\quad", "  "),
        (r"\%", "%"),
        (r"\_", "_"),
        (r"\{", "{"),
        (r"\}", "}"),
        (r"^{\dagger}", "†"),
    ]
    for old, new in replacements:
        s = s.replace(old, new)

    # Unwrap remaining text commands and subscripts before parsing fractions.
    s = re.sub(r"\\text\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"_\{([^{}]+)\}", r"_\1", s)

    # Convert \frac{a}{b} -> (a)/(b)
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", s)
    # Remove \tag{n} and keep (n)
    s = re.sub(r"\\tag\{(\d+)\}", r"   (\1)", s)
    # Remove remaining $ delimiters
    s = s.replace("$", "")
    # Clean remaining superscript braces.
    s = re.sub(r"\^\{([^{}]+)\}", r"^\1", s)
    # Remove backticks
    s = s.replace("`", "")
    return s


def parse_markdown_blocks(md_text: str):
    """마크다운 원고를 구조화된 블록 리스트로 파싱한다."""
    lines = md_text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped or stripped == "---":
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            blocks.append(("title_ko", stripped[2:].strip()))
            i += 1
            continue
        if stripped.startswith("### ") and i < 10:
            blocks.append(("title_en", stripped[4:].strip()))
            i += 1
            continue
        if stripped.startswith("## "):
            blocks.append(("h1", clean_latex_to_unicode(stripped[3:].strip())))
            i += 1
            continue
        if stripped.startswith("### "):
            blocks.append(("h2", clean_latex_to_unicode(stripped[4:].strip())))
            i += 1
            continue
        if stripped.startswith("#### "):
            blocks.append(("h3", clean_latex_to_unicode(stripped[5:].strip())))
            i += 1
            continue

        # Table caption
        if stripped.startswith("**Table ") and stripped.endswith("**"):
            cap = clean_latex_to_unicode(stripped.strip("*").strip())
            blocks.append(("table_caption", cap))
            i += 1
            continue

        # Markdown Table
        if stripped.startswith("|") and stripped.endswith("|"):
            tbl_lines = []
            while i < n and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
            if len(tbl_lines) >= 2:
                headers = [clean_latex_to_unicode(c.strip()) for c in tbl_lines[0].strip("|").split("|")]
                rows = []
                for tl in tbl_lines[2:]:
                    cells = [clean_latex_to_unicode(c.strip()) for c in tl.strip("|").split("|")]
                    if len(cells) < len(headers):
                        cells += [""] * (len(headers) - len(cells))
                    rows.append(cells[: len(headers)])
                blocks.append(("table", (headers, rows)))
            continue

        # Blockquote / Note
        if stripped.startswith(">"):
            q_lines = []
            while i < n and lines[i].strip().startswith(">"):
                ql = lines[i].strip().lstrip(">").strip()
                if ql != "[!NOTE]":
                    q_lines.append(ql)
                i += 1
            blocks.append(("note", clean_latex_to_unicode(" ".join(q_lines))))
            continue

        # Display equation
        if stripped.startswith("$$") and stripped.endswith("$$"):
            eq_raw = stripped.strip("$").strip()
            m_tag = re.search(r"\\tag\{(\d+)\}", eq_raw)
            eq_num = m_tag.group(1) if m_tag else ""
            eq_clean = re.sub(r"\\tag\{\d+\}", "", eq_raw).strip()
            eq_clean = clean_latex_to_unicode(eq_clean)
            blocks.append(("equation", (eq_clean, eq_num)))
            i += 1
            continue

        # Table note (*주:)
        if stripped.startswith("*주:"):
            note_txt = clean_latex_to_unicode(stripped.lstrip("*").rstrip("*").strip())
            blocks.append(("table_note", note_txt))
            i += 1
            continue

        # Author meta at top (lines 4-5)
        if i < 10 and (stripped.startswith("**[ 저자") or "한국성서대학교" in stripped):
            i += 1
            continue

        # Reference item
        if re.match(r"^\[\d+\]\s+", stripped):
            blocks.append(("reference", clean_latex_to_unicode(stripped)))
            i += 1
            continue

        # Bullet / numbered list
        if re.match(r"^(\d+\.|-)\s+", stripped):
            blocks.append(("bullet", clean_latex_to_unicode(stripped)))
            i += 1
            continue

        # Indented sub-bullet
        if re.match(r"^\s+(-\s+|\d+\)\s+)", line):
            blocks.append(("subbullet", clean_latex_to_unicode(stripped)))
            i += 1
            continue

        # Normal paragraph
        blocks.append(("paragraph", clean_latex_to_unicode(stripped)))
        i += 1

    return blocks


# =============================================================================
# 1. Word (.docx) 생성기
# =============================================================================
def set_run_font(
    run,
    kor_font=FONT_MYEONGJO,
    eng_font=FONT_EN_SERIF,
    size_pt=9.2,
    bold=False,
    italic=False,
    color_rgb=(0, 0, 0),
    char_spacing_pt=0,
):
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


def add_formatted_runs(p, text: str, kor_font=FONT_MYEONGJO, eng_font=FONT_EN_SERIF, size_pt=9.2, color_rgb=(0, 0, 0), char_spacing_pt=0):
    """**볼드** 및 *이탤릭* 마크업을 파싱하여 Word Run으로 추가한다."""
    tokens = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**"):
            r = p.add_run(tok[2:-2])
            set_run_font(r, kor_font, eng_font, size_pt=size_pt, bold=True, color_rgb=color_rgb, char_spacing_pt=char_spacing_pt)
        elif tok.startswith("*") and tok.endswith("*"):
            r = p.add_run(tok[1:-1])
            set_run_font(r, kor_font, eng_font, size_pt=size_pt, italic=True, color_rgb=color_rgb, char_spacing_pt=char_spacing_pt)
        else:
            r = p.add_run(tok)
            set_run_font(r, kor_font, eng_font, size_pt=size_pt, bold=False, color_rgb=color_rgb, char_spacing_pt=char_spacing_pt)


def set_cell_margins(cell, top=50, bottom=50, left=65, right=65):
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
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f"</w:tblBorders>"
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
        f"</w:pBdr>"
    )
    pPr.append(pBdr)
    return p


def build_docx_from_final_md(blocks, out_path: Path, blind_mode: bool = False):
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
        mode_tag = "심사용 블라인드본" if blind_mode else "투고 최종본 (A-6.1)"
        hrun = hp.add_run(
            f"한국정보통신학회논문지 (JKIICE) 2026 ({mode_tag})  |  "
            "뉴스 빅데이터와 NMF 기반의 한국형 경제 이슈 다중 국면 탐지 및 다각적 실증 검증"
        )
        set_run_font(hrun, FONT_GOTHIC, FONT_EN_SANS, size_pt=7.5, color_rgb=(100, 100, 100))

    # 상단 학회 배너
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

    title_ko = next((v for k, v in blocks if k == "title_ko"), "")
    title_en = next((v for k, v in blocks if k == "title_en"), "")

    # 국문 제목
    p_title_ko = doc.add_paragraph()
    p_title_ko.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title_ko.paragraph_format.line_spacing = 1.30
    p_title_ko.paragraph_format.space_before = Pt(4)
    p_title_ko.paragraph_format.space_after = Pt(6)
    r_tko = p_title_ko.add_run(title_ko)
    set_run_font(r_tko, FONT_GOTHIC, FONT_EN_SANS, size_pt=16.5, bold=True, char_spacing_pt=-0.5)

    if not blind_mode:
        p_auth_ko = doc.add_paragraph()
        p_auth_ko.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_auth_ko.paragraph_format.line_spacing = 1.20
        p_auth_ko.paragraph_format.space_before = Pt(2)
        p_auth_ko.paragraph_format.space_after = Pt(6)
        r_ako = p_auth_ko.add_run("[ 저자 미정 (투고 전 최종본, 2026-11-07) ] · 한국성서대학교 AI융합학부")
        set_run_font(r_ako, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=11.0, bold=True, char_spacing_pt=-0.3)

    # 영문 제목
    p_title_en = doc.add_paragraph()
    p_title_en.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_title_en.paragraph_format.line_spacing = 1.20
    p_title_en.paragraph_format.space_before = Pt(2)
    p_title_en.paragraph_format.space_after = Pt(6)
    r_ten = p_title_en.add_run(title_en)
    set_run_font(r_ten, FONT_GOTHIC, FONT_EN_SANS, size_pt=12.0, bold=True)

    if not blind_mode:
        p_affil = doc.add_paragraph()
        p_affil.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_affil.paragraph_format.line_spacing = 1.20
        p_affil.paragraph_format.space_before = Pt(0)
        p_affil.paragraph_format.space_after = Pt(8)
        r_aff = p_affil.add_run("School of AI Convergence, Korean Bible University, Seoul, 01757 Korea")
        set_run_font(r_aff, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.0)

    current_sec = ""
    page_break_done = False

    for btype, bval in blocks:
        if btype in ("title_ko", "title_en"):
            continue

        if btype == "h1":
            current_sec = bval
            if bval.startswith("Ⅰ.") and not page_break_done:
                # 제1면 하단 키워드 및 서지 정보 블록 추가 후 페이지 나누기
                p_kw_ko = doc.add_paragraph()
                p_kw_ko.paragraph_format.space_before = Pt(6)
                p_kw_ko.paragraph_format.space_after = Pt(2)
                r_kl = p_kw_ko.add_run("키워드 : ")
                set_run_font(r_kl, FONT_GOTHIC, FONT_EN_SANS, size_pt=9.5, bold=True)
                r_kt = p_kw_ko.add_run("경제 뉴스 빅데이터, 텍스트 마이닝, 토픽 모델링, 비음수 행렬 분해(NMF), 다중 국면 활성화, 표본 외(Strict OOS) 검증, 네이버 데이터랩, 수렴 강건성")
                set_run_font(r_kt, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.5)

                p_kw_en = doc.add_paragraph()
                p_kw_en.paragraph_format.space_before = Pt(0)
                p_kw_en.paragraph_format.space_after = Pt(8)
                r_kel = p_kw_en.add_run("Keywords : ")
                set_run_font(r_kel, FONT_GOTHIC, FONT_EN_SANS, size_pt=9.5, bold=True)
                r_ket = p_kw_en.add_run("Convergence Sensitivity, Cross-Source Validation, Economic News Big Data, Multi-Regime Activation, Naver Datalab, Non-negative Matrix Factorization (NMF), Strict Out-of-Sample Validation, Topic Modeling")
                set_run_font(r_ket, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.5)

                add_horizontal_rule(doc, sz=4, color="000000", space_before=4, space_after=4)
                doc.add_page_break()
                page_break_done = True

            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12 if page_break_done else 6)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(bval)
            set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=11.0, bold=True)
            continue

        if btype == "h2":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(bval)
            set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=10.0, bold=True)
            continue

        if btype == "h3":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(bval)
            set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=9.5, bold=True)
            continue

        if btype == "paragraph":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            is_abs_en = current_sec == "ABSTRACT"
            p.paragraph_format.line_spacing = 1.30 if current_sec in ("요 약", "ABSTRACT") else 1.48
            p.paragraph_format.first_line_indent = Pt(10)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3.5)
            add_formatted_runs(
                p,
                bval,
                FONT_MYEONGJO,
                FONT_EN_SERIF,
                size_pt=8.5 if is_abs_en else 9.2,
                char_spacing_pt=-0.2 if is_abs_en else 0,
            )
            continue

        if btype in ("bullet", "subbullet"):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.42
            p.paragraph_format.left_indent = Pt(12 if btype == "bullet" else 22)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2.5)
            add_formatted_runs(p, bval, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.0)
            continue

        if btype == "note":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.35
            p.paragraph_format.left_indent = Pt(10)
            p.paragraph_format.right_indent = Pt(10)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            add_formatted_runs(p, "[참고] " + bval, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.4, color_rgb=(30, 41, 59))
            continue

        if btype == "equation":
            eq_clean, eq_num = bval
            tbl = doc.add_table(rows=1, cols=2)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.rows[0].cells[0].width = Mm(150)
            tbl.rows[0].cells[1].width = Mm(20)
            p0 = tbl.rows[0].cells[0].paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r0 = p0.add_run(eq_clean)
            set_run_font(r0, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.2, italic=True, bold=True)
            p1 = tbl.rows[0].cells[1].paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r1 = p1.add_run(f"({eq_num})" if eq_num else "")
            set_run_font(r1, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=9.0)
            continue

        if btype == "table_caption":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing = 1.25
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(bval)
            set_run_font(r, FONT_GOTHIC, FONT_EN_SANS, size_pt=8.5, bold=True)
            continue

        if btype == "table":
            headers, rows = bval
            ncols = len(headers)
            tbl = doc.add_table(rows=len(rows) + 1, cols=ncols)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_jkiice_table_borders(tbl)
            font_sz = 7.0 if ncols >= 10 else (7.5 if ncols >= 7 else 8.0)

            for c_idx, h_text in enumerate(headers):
                cell = tbl.rows[0].cells[c_idx]
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                add_formatted_runs(p, h_text.replace("**", ""), FONT_GOTHIC, FONT_EN_SERIF, size_pt=font_sz)
                for run in p.runs:
                    run.font.bold = True
                set_cell_background(cell, "F2F4F8")
                set_cell_margins(cell, top=45, bottom=45, left=45, right=45)

            for r_idx, r_data in enumerate(rows, start=1):
                for c_idx, val in enumerate(r_data):
                    cell = tbl.rows[r_idx].cells[c_idx]
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    p = cell.paragraphs[0]
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_before = Pt(1.5)
                    p.paragraph_format.space_after = Pt(1.5)
                    add_formatted_runs(p, val, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=font_sz)
                    set_cell_margins(cell, top=40, bottom=40, left=45, right=45)
            continue

        if btype == "table_note":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.20
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(6)
            add_formatted_runs(p, bval, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=7.8, color_rgb=(50, 50, 50))
            continue

        if btype == "reference":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.40
            p.paragraph_format.left_indent = Pt(18)
            p.paragraph_format.first_line_indent = Pt(-18)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            add_formatted_runs(p, bval, FONT_MYEONGJO, FONT_EN_SERIF, size_pt=8.0)
            continue

    doc.save(out_path)
    print(f"[DOCX 생성 완료] {out_path} ({out_path.stat().st_size:,} bytes)")


# =============================================================================
# 2. PDF (.pdf) 생성기 (ReportLab)
# =============================================================================
def md_inline_to_reportlab(text: str) -> str:
    """마크다운 **볼드** 및 *이탤릭*을 ReportLab XML 태그로 변환한다."""
    s = xml_escape(text)
    s = re.sub(r"\*\*([^*]+)\*\*", r'<font name="Malgun-Bold">\1</font>', s)
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    return s


def build_pdf_from_final_md(blocks, out_path: Path):
    pdfmetrics.registerFont(TTFont("Malgun", str(FONT_REG)))
    pdfmetrics.registerFont(TTFont("Malgun-Bold", str(FONT_BD)))

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    st_banner = ParagraphStyle("Banner", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=8.5, leading=11, alignment=TA_RIGHT, textColor=HexColor("#475569"), spaceAfter=4)
    st_title_ko = ParagraphStyle("TitleKo", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=14.5, leading=19, alignment=TA_LEFT, textColor=HexColor("#0F172A"), spaceAfter=4)
    st_title_en = ParagraphStyle("TitleEn", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=10.0, leading=13.5, alignment=TA_LEFT, textColor=HexColor("#334155"), spaceAfter=4)
    st_author = ParagraphStyle("Author", parent=styles["Normal"], fontName="Malgun", fontSize=8.8, leading=12, alignment=TA_LEFT, textColor=HexColor("#475569"), spaceAfter=6)
    st_h1 = ParagraphStyle("H1", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=11.0, leading=15, spaceBefore=10, spaceAfter=4, textColor=HexColor("#0F172A"), keepWithNext=True)
    st_h2 = ParagraphStyle("H2", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=9.8, leading=13.5, spaceBefore=8, spaceAfter=3, textColor=HexColor("#1E293B"), keepWithNext=True)
    st_h3 = ParagraphStyle("H3", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=9.0, leading=12.5, spaceBefore=6, spaceAfter=2, textColor=HexColor("#334155"), keepWithNext=True)
    st_body = ParagraphStyle("Body", parent=styles["Normal"], fontName="Malgun", fontSize=8.6, leading=13.2, alignment=TA_JUSTIFY, firstLineIndent=8, spaceAfter=3, textColor=HexColor("#0F172A"))
    st_bullet = ParagraphStyle("Bullet", parent=styles["Normal"], fontName="Malgun", fontSize=8.4, leading=12.8, alignment=TA_JUSTIFY, leftIndent=10, spaceAfter=2.5, textColor=HexColor("#0F172A"))
    st_note = ParagraphStyle("Note", parent=styles["Normal"], fontName="Malgun", fontSize=8.0, leading=12.0, alignment=TA_JUSTIFY, leftIndent=10, rightIndent=10, backColor=HexColor("#F8FAFC"), borderPadding=5, spaceBefore=4, spaceAfter=5, textColor=HexColor("#334155"))
    st_eq = ParagraphStyle("Eq", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=8.8, leading=13, alignment=TA_CENTER, spaceBefore=4, spaceAfter=4, textColor=HexColor("#0F172A"))
    st_tcap = ParagraphStyle("TCap", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=8.2, leading=11.5, spaceBefore=6, spaceAfter=2, textColor=HexColor("#0F172A"), keepWithNext=True)
    st_tnote = ParagraphStyle("TNote", parent=styles["Normal"], fontName="Malgun", fontSize=7.4, leading=10.5, alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=5, textColor=HexColor("#475569"))
    st_ref = ParagraphStyle("Ref", parent=styles["Normal"], fontName="Malgun", fontSize=7.6, leading=11.2, alignment=TA_JUSTIFY, leftIndent=14, firstLineIndent=-14, spaceAfter=2, textColor=HexColor("#1E293B"))

    story = []
    story.append(Paragraph("한국정보통신학회논문지 (JKIICE) 2026 최종본 (A-6.1 검증 완료, 2026-11-07)", st_banner))
    story.append(HRFlowable(width="100%", thickness=1.2, color=HexColor("#0F172A"), spaceAfter=6))

    title_ko = next((v for k, v in blocks if k == "title_ko"), "")
    title_en = next((v for k, v in blocks if k == "title_en"), "")
    story.append(Paragraph(md_inline_to_reportlab(title_ko), st_title_ko))
    story.append(Paragraph(md_inline_to_reportlab(title_en), st_title_en))
    story.append(Paragraph("[ 저자 미정 (투고 전 최종본, 2026-11-07) ] · 한국성서대학교 AI융합학부 (School of AI Convergence, Korean Bible University)", st_author))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#CBD5E1"), spaceAfter=6))

    printable_width = 180 * mm

    for btype, bval in blocks:
        if btype in ("title_ko", "title_en"):
            continue
        if btype == "h1":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_h1))
        elif btype == "h2":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_h2))
        elif btype == "h3":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_h3))
        elif btype == "paragraph":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_body))
        elif btype in ("bullet", "subbullet"):
            story.append(Paragraph(md_inline_to_reportlab(bval), st_bullet))
        elif btype == "note":
            story.append(Paragraph(md_inline_to_reportlab("[참고] " + bval), st_note))
        elif btype == "equation":
            eq_clean, eq_num = bval
            eq_str = f"{eq_clean}     ({eq_num})" if eq_num else eq_clean
            story.append(Paragraph(md_inline_to_reportlab(eq_str), st_eq))
        elif btype == "table_caption":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_tcap))
        elif btype == "table":
            headers, rows = bval
            ncols = len(headers)
            fsz = 6.2 if ncols >= 10 else (6.8 if ncols >= 7 else 7.3)
            st_th = ParagraphStyle("TH", parent=styles["Normal"], fontName="Malgun-Bold", fontSize=fsz, leading=fsz + 2.2, alignment=TA_CENTER, textColor=HexColor("#0F172A"))
            st_td_l = ParagraphStyle("TDL", parent=styles["Normal"], fontName="Malgun", fontSize=fsz, leading=fsz + 2.2, alignment=TA_LEFT, textColor=HexColor("#0F172A"))
            st_td_c = ParagraphStyle("TDC", parent=styles["Normal"], fontName="Malgun", fontSize=fsz, leading=fsz + 2.2, alignment=TA_CENTER, textColor=HexColor("#0F172A"))

            t_data = [[Paragraph(md_inline_to_reportlab(h.replace("**", "")), st_th) for h in headers]]
            for r in rows:
                row_Flow = []
                for c_idx, cell_txt in enumerate(r):
                    st_use = st_td_l if c_idx == 0 else st_td_c
                    row_Flow.append(Paragraph(md_inline_to_reportlab(cell_txt), st_use))
                t_data.append(row_Flow)

            # Column widths proportional to max text length
            col_weights = []
            for c_idx in range(ncols):
                max_len = max([len(headers[c_idx])] + [len(r[c_idx]) for r in rows[:10]])
                col_weights.append(max(min(max_len, 42), 8))
            total_w = sum(col_weights)
            col_widths = [(w / total_w) * printable_width for w in col_weights]

            tbl = Table(t_data, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F1F5F9")),
                        ("LINEABOVE", (0, 0), (-1, 0), 1.0, HexColor("#0F172A")),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.7, HexColor("#334155")),
                        ("LINEBELOW", (0, -1), (-1, -1), 1.0, HexColor("#0F172A")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, HexColor("#CBD5E1")),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("LEFTPADDING", (0, 0), (-1, -1), 3),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            story.append(tbl)
            story.append(Spacer(1, 3))
        elif btype == "table_note":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_tnote))
        elif btype == "reference":
            story.append(Paragraph(md_inline_to_reportlab(bval), st_ref))

    doc.build(story)
    print(f"[PDF 생성 완료]  {out_path} ({out_path.stat().st_size:,} bytes)")


def main():
    assert SRC_MD.exists(), f"최종 마크다운 원고가 존재하지 않습니다: {SRC_MD}"
    md_text = SRC_MD.read_text(encoding="utf-8")
    blocks = parse_markdown_blocks(md_text)
    print(f"파싱 완료: 총 {len(blocks)}개 문서 블록 (표 {sum(1 for k, _ in blocks if k == 'table')}개, 참고문헌 {sum(1 for k, _ in blocks if k == 'reference')}개)")

    # 1. 기본 마크다운 파일(PAPER_DRAFT_JKIICE.md)을 최신 최종본(PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md)으로 동기화
    legacy_md = DOCS / "PAPER_DRAFT_JKIICE.md"
    shutil.copy2(SRC_MD, legacy_md)
    print(f"[MD 동기화 완료] {legacy_md} <- {SRC_MD.name}")

    # 2. Word (.docx) 최신화 빌드
    out_docx_final = DOCS / "PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.docx"
    out_docx_sub = DOCS / "PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx"
    out_docx_blind = DOCS / "PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx"
    out_docx_legacy = DOCS / "PAPER_DRAFT_JKIICE.docx"

    build_docx_from_final_md(blocks, out_docx_final, blind_mode=False)
    shutil.copy2(out_docx_final, out_docx_sub)
    shutil.copy2(out_docx_final, out_docx_legacy)
    build_docx_from_final_md(blocks, out_docx_blind, blind_mode=True)

    # 3. PDF (.pdf) 최신화 빌드
    out_pdf_final = DOCS / "PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.pdf"
    out_pdf_legacy = DOCS / "PAPER_DRAFT_JKIICE.pdf"

    build_pdf_from_final_md(blocks, out_pdf_final)
    shutil.copy2(out_pdf_final, out_pdf_legacy)
    print(f"[PDF 동기화 완료] {out_pdf_legacy} <- {out_pdf_final.name}")


if __name__ == "__main__":
    main()

