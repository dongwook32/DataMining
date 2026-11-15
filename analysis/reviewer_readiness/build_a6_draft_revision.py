"""
Study A-6: JKIICE Draft Revision Builder (draft-stage only; no submission work)
===============================================================================
Input  : docs/drafts/PAPER_DRAFT_JKIICE_A4_20261106.md (read-only)
Output : docs/drafts/PAPER_DRAFT_JKIICE_DRAFT_REVISION_20261107.md
         data/processed/reviewer_readiness/RUN_20261107_A6_DRAFT_REVISION_01/
             protected_hashes_before.csv, protected_hashes_after.csv, a6_checks.json
Every textual edit is an exact, count-asserted replacement so that unmatched
anchors fail loudly instead of silently skipping.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
RR = ROOT / "data" / "processed" / "reviewer_readiness"
SRC = DOCS / "drafts" / "PAPER_DRAFT_JKIICE_A4_20261106.md"
OUT = DOCS / "drafts" / "PAPER_DRAFT_JKIICE_DRAFT_REVISION_20261107.md"
RUN_DIR = RR / "RUN_20261107_A6_DRAFT_REVISION_01"

PROTECTED = [
    SRC,
    DOCS / "A4_CHANGELOG_20261106.md",
    DOCS / "A4_CLAIM_EVIDENCE_MATRIX_20261106.csv",
    DOCS / "A4_FINAL_QC_20261106.md",
    DOCS / "PAPER_DRAFT_JKIICE.md",
    DOCS / "drafts" / "PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md",
]
for d in [
    "RUN_20261106_NMF_CONVERGENCE_01",
    "RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01",
    "RUN_20261106_A3_CONSISTENCY_AUDIT_01",
    "RUN_20261106_A3_2_WEEKLY_PERIOD_AUDIT_01",
    "RUN_20261106_A5_REFERENCE_AUDIT_01",
    "RUN_20261106_A5_1_REFERENCE_CORRECTION_01",
]:
    PROTECTED += sorted(p for p in (RR / d).iterdir() if p.is_file())


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [{"file_path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(p)} for p in PROTECTED]
    )


EDIT_LOG: list[dict] = []


def rep(text: str, old: str, new: str, edit_id: str, section: str, count: int = 1) -> str:
    n = text.count(old)
    assert n == count, f"[{edit_id}] expected {count} occurrence(s), found {n}: {old[:80]!r}"
    EDIT_LOG.append({"edit_id": edit_id, "section": section})
    return text.replace(old, new)


def rep_line(text: str, startswith: str, new_line: str, edit_id: str, section: str) -> str:
    lines = text.split("\n")
    idx = [i for i, ln in enumerate(lines) if ln.startswith(startswith)]
    assert len(idx) == 1, f"[{edit_id}] line anchor matched {len(idx)} times"
    lines[idx[0]] = new_line
    EDIT_LOG.append({"edit_id": edit_id, "section": section})
    return "\n".join(lines)


def build(text: str) -> str:
    # ---------------- 요약 / ABSTRACT ----------------
    text = rep(
        text,
        r"6대 기본 분석 체계 중 5개 불변 국면(시황, 기업실적, AI·반도체, 금리·물가, 자본거래)의 67개월 월별 비중은 Pearson $r = 0.9910 \sim 0.9998$로 고도로 일치하였으며, 완전 수렴 시 부동산 국면(NMF-400 평균 12.28%)은 순수 부동산(6.05%)과 가계대출(5.99%)로 정밀하게 분리되는 구조적 분화 현상을 발견하였다.",
        r"6대 기본 분석 체계 중 5개 비분할 국면(시황, 기업실적, 첨단산업(전기차·배터리 중심), 금리·물가, 자본거래)의 67개월 월별 비중은 Pearson $r = 0.9910 \sim 0.9998$로 높게 일치하였으며, NMF-800에서는 부동산 국면(NMF-400 평균 12.28%)이 순수 부동산(6.05%)과 가계대출(5.99%)로 분리되는 현상이 추가로 관찰되었다(기본 분석 체계는 NMF-400의 6대 국면으로 유지).",
        "E01", "요약",
    )
    text = rep(text, "다중 국면 동시 탐지의 필요성이 일관되게 확인되었다.",
               "단일 대표 국면 표현의 정보 누락이 일관되게 확인되었다.", "E02", "요약")
    text = rep(
        text,
        "두 쌍에서 견고한 대중 관심 동조화가 실증되었다. 본 연구는 뉴스 텍스트 기반 다중 경제 이슈 국면 탐지의 정보 보존성과 수렴 강건성을 입증한 실증적 기초를 제공한다.",
        r"두 쌍에서 Holm 보정 후 유의한 동시점 동조가 확인되었다(단, NMF-800의 '시황' 쌍은 HAC `maxlags=4` 기준 $p_{\text{holm}} = 0.0508$로 경계 수준). 이러한 결과는 동시점 관계에 관한 것으로 인과성이나 사전 예측력을 의미하지 않으며, 본 연구는 뉴스 텍스트 기반 다중 경제 이슈 국면 탐지의 정보 보존성과 NMF 수렴 조건 변화에 대한 주요 결과의 강건성을 실증적으로 검토한 기초 자료를 제공한다.",
        "E03", "요약",
    )
    text = rep(text, "while real estate bifurcated cleanly into pure property (6.05%) and household debt (5.99%).",
               "while, under NMF-800, the real-estate regime split into pure property (6.05%) and household debt (5.99%), which is reported only as an additional finding.",
               "E04", "ABSTRACT")
    text = rep(text, "consistently substantiating the need for multi-regime representations",
               "consistently indicating information loss under single-regime representations", "E05", "ABSTRACT")
    text = rep(text, "exhibiting robust negative co-movements across both NMF-400 and NMF-800",
               "exhibiting significant negative contemporaneous co-movements under both NMF-400 and NMF-800", "E06", "ABSTRACT")
    text = rep(
        text,
        r"confirmed robust out-of-sample (82 weeks) contemporaneous synchronization in market conditions ($r = +0.4984, p_{\text{holm}} = 0.0432$) and earnings ($r = +0.4718, p_{\text{holm}} = 0.0011$). This research provides rigorous methodological and empirical foundations for unsupervised multi-regime economic monitoring.",
        r"identified Holm-significant out-of-sample (82 weeks) contemporaneous co-movement for market conditions ($r = +0.4984, p_{\text{holm}} = 0.0432$) and earnings ($r = +0.4718, p_{\text{holm}} = 0.0011$), although the market pair was borderline under NMF-800 ($p_{\text{holm}} = 0.0508$ at maxlags=4). These results describe contemporaneous associations and do not establish causality or predictive ability.",
        "E07", "ABSTRACT",
    )

    # ---------------- Ⅰ. 서론 ----------------
    text = rep(text, "그 결과를 과거와 미래 시점에 동일하게 적용한다[10].",
               "그 결과를 과거와 미래 시점에 동일하게 적용한다.", "E08", "1장 (참고문헌 [10] 인용 위치 조정)")
    text = rep(
        text,
        "강건한 동시점 동조화를 나타내는가(연구 D)?\n",
        "강건한 동시점 동조화를 나타내는가(연구 D)?\n\n"
        "아울러 본 연구는 기준 모델(NMF-400)이 최대 반복 횟수(`max_iter=400`) 상한에 도달하여 수렴 경고가 발생한 사실을 보고하고, 허용오차 기준 수렴에 도달한 NMF-800 모델을 강건성 검증 모델로 사용하여 RQ1~RQ4의 주요 결과가 수렴 조건 변화에 대해 유지되는지 점검한다. 기본 분석 체계는 사전에 확정된 NMF-400의 6대 국면이며, NMF-800에서 분리된 가계대출(`hhdebt`) 국면은 추가 발견으로만 보고한다.\n",
        "E09", "1장 (강건성 검증 설계 안내)",
    )

    # ---------------- Ⅱ. 관련 연구 ----------------
    text = rep(
        text,
        "또한 Glasserman and Mamaysky[10]는 과거 학습 창을 기준으로만 뉴스 비정상성(Unusualness)을 산출하여 미래 정보 누수(Look-ahead Bias)를 차단한 금융 시장 스트레스 분석을 제시하였다.",
        "또한 Glasserman and Mamaysky[10]는 50개 대형 금융회사 관련 기사 36만여 건(1996~2014)을 분석하여, 부정적 감성을 띤 뉴스의 비정상성(unusualness) 증가가 개별 기업 및 시장 전체의 주식 변동성 증가를 예측함을 보였다. 검색 데이터 측면에서는 Da, Engelberg, and Gao[15]가 가계의 인터넷 검색량으로 투자자 심리 지표(FEARS)를 구성하여 자산 가격과의 관계를 분석하였고, Youk, Kim, and Kim[16]은 미세먼지 관련 일별 뉴스 보도량·뉴스 감성과 네이버 검색량의 관계가 COVID-19 확산 전후로 어떻게 달라지는지를 시계열 모형으로 분석하였으며, Cho[17]는 네이버 검색 열기와 한국 AI 공급망 관련 주식의 변동성 간 관계를 분석하였다.",
        "E10", "2.1절 (참고문헌 [10] 인용 범위 조정, [15]-[17] 설명 보강)",
    )
    text = rep(
        text,
        "김수현·이영준·신진영·박기영[7]은 한국은행 금융통화위원회 의사록과 경제 뉴스 텍스트를 활용한 거시경제 분석 프레임워크를 정리하였으며",
        "김수현·이영준·신진영·박기영[7]은 텍스트 마이닝 및 자연어 처리 기법을 소개하고 이를 거시경제 분석에 활용한 연구 사례를 정리하였으며",
        "E11", "2.1절 (참고문헌 [7] 설명을 초록 확인 범위로 한정)",
    )
    text = rep_line(
        text, "| **Glasserman & Mamaysky (2019)** [10]",
        "| **Glasserman & Mamaysky (2019)** [10] | 대형 금융회사 관련 기사 36만여 건 (`1996~2014`) | 뉴스 비정상성(unusualness) + 감성 | 비정상성·감성 상호작용 지표 | 미수행 | 해당 없음 (토픽 기저 미사용) | 미수행 (주식 변동성 예측) |",
        "E12", "표 F-1 ([10] 행)",
    )
    text = rep_line(
        text, "| **Youk et al. (2026) [16] / Cho (2026) [17]**",
        "| **Youk et al. (2026) [16] / Cho (2026) [17]** | 미세먼지 뉴스량·감성 및 네이버 검색 (일별, `2019~2020`) / 네이버 검색 | 일별 시계열 모형 / 검색 열기 지수 | 미세먼지·COVID-19 이슈 경쟁 / 단일 AI 섹터 | 미수행 | 미적용 | 적용 (비경제 이슈·일별 자료 / AI 단일 섹터) |",
        "E13", "표 F-1 ([16]/[17] 행)",
    )
    m = re.search(r"O'Callaghan et al\.\[13\]과 Egger and Yu\[14\]가 실증한 바와 같이,.*?완벽한 수치적 재현성을 보장한다\.", text, flags=re.S)
    assert m, "[E14] anchor not found"
    text = text[: m.start()] + (
        "O'Callaghan et al.[13]은 여러 텍스트 코퍼스에서 NMF와 LDA가 생성한 토픽 기술어(descriptor)의 응집도를 비교하여, LDA 토픽에는 고빈도 일반 어휘가 상위어로 포함되는 경향이 있는 반면 NMF 토픽은 상대적으로 구체적인 어휘로 구성되는 경향이 있음을 보고하였다. Egger and Yu[14]는 트위터 게시물을 대상으로 LDA, NMF, Top2Vec, BERTopic을 비교하여 기법에 따라 도출되는 토픽의 해석 가능성이 달라짐을 보였다. 이들 선행연구는 영어 텍스트를 대상으로 하였으므로, 본 연구는 한국어 경제 뉴스 코퍼스에서 NMF와 LDA를 직접 비교한다(3.2절). NMF는 비음수 제약을 통해 가산적 부분 기반 표현(Part-based Representation)을 형성하며[11], 결정론적 특이값 분해 초기화(`nndsvd`)와 좌표 하강법을 사용하면 동일한 계산 환경에서 결정론적으로 재현 가능한 결과를 얻을 수 있다."
    ) + text[m.end():]
    EDIT_LOG.append({"edit_id": "E14", "section": "2.2절 ([13]·[14] 인용 표현 한정)"})
    text = rep(text, "가짜 상관(Spurious Correlation)이 발생한다[15].",
               "가짜 상관(Spurious Correlation)이 발생한다[20].", "E15", "2.3절 (가짜 상관 근거를 [15]→[20]으로 교체)")

    # ---------------- Ⅲ. 연구 방법 ----------------
    text = rep(
        text,
        "최대 절대 오차 `0.000e+00`로 완벽히 일치함).",
        "최대 절대 오차 `0.000e+00`로 완벽히 일치함). 단, 이 적합은 최대 반복 횟수(`max_iter=400`) 상한에 도달하여 수렴 경고(`ConvergenceWarning`)가 발생하였으며, 이에 대한 수렴성 강건성 검증은 3.3.1절에서 제시한다.",
        "E16", "3.2절 (수렴 경고 명시)",
    )
    text = rep(
        text,
        "\n\n**Table A-2.",
        "\n\n#### 3.3.1 NMF 반복 상한 도달에 대한 수렴성 강건성 검증 (NMF-400 vs NMF-800)\n"
        "기준 모델(NMF-400)은 `max_iter=400` 상한에서 정지하여 수렴 경고가 발생하였다. 이 경고가 토픽 구조와 후속 분석 결과에 미치는 영향을 점검하기 위해, 학습 표본(144,000건), 어휘 사전(22,193개), 초기화(`nndsvd`), 난수 시드(42)를 동일하게 두고 최대 반복 횟수만 800회로 늘린 NMF-800 모델을 별도로 적합하였다(`convergence_metrics.csv`, `topic_similarity.csv`, `topic_alignment.csv`). NMF-800은 447회 반복에서 허용오차(`tol=1e-4`) 조건을 충족하여 정지하였으며, 재구성 오차는 369.8048에서 369.7777로 0.0073% 감소하는 데 그쳤다. 1:1 토픽 대응 기준 14개 토픽 전체의 평균 코사인 유사도는 0.9802였고 최저 유사도는 Topic 2(0.7846)에서 관측되었으며, Topic 2를 제외한 13개 토픽의 평균 코사인 유사도는 0.9953(최솟값 0.9686, Topic 3)이었다(표 A-2). NMF-800에서 Topic 2는 가계대출(`hhdebt`) 국면으로 재매핑되어, NMF-400에서 토픽 2·3이 함께 구성하던 `realestate` 국면이 순수 부동산(토픽 3)과 가계대출(토픽 2)로 분리되었다(4.1절).\n\n"
        "NMF-800의 수렴은 좌표 하강법의 허용오차 기준 정지를 의미하며, 비볼록 최적화 문제인 NMF의 전역 최적해 도달을 보장하지 않는다. 본 연구는 사후적 모형 선택을 배제하기 위해 사전에 확정된 NMF-400을 기준 모델로 유지하고, NMF-800은 4장의 주요 결과가 수렴 조건 변화에 대해 유지되는지 점검하는 강건성 검증 모델로만 사용한다.\n\n"
        "**Table A-2.",
        "E17", "3.3.1절 신설 (수렴성 강건성 검증 본문)",
    )
    text = rep(text, "| 400회는 수학적 미완전 수렴 상태였음 확인 |",
               "| 400회 적합은 허용오차 기준 미수렴 상태 |", "E18", "표 A-2")
    text = rep(text, r"| 오차 개선율 $0.007\%$로 사실상 플래토(Plateau) 도달 |",
               r"| 추가 반복에 따른 오차 개선은 $0.007\%$ 수준으로 미미 |", "E19", "표 A-2")
    text = rep(text, r"| 13개 핵심 토픽은 $0.995$ 수준의 완벽에 가까운 불변성 |",
               r"| Topic 2 제외 13개 토픽은 평균 $0.995$ 수준의 높은 유사도 |", "E20", "표 A-2")
    text = rep_line(
        text, "| **Topic 2 (`realestate`) 토픽 분화**",
        r"| **Topic 2 매핑 변화 (`realestate` 국면)** | `realestate` = 토픽 2+3 (67개월 평균 $12.28\%$) | 토픽 2 → `hhdebt` (평균 $5.99\%$), 토픽 3 → `realestate` (평균 $6.05\%$) | Topic 2 Cosine $0.7846$ (14개 중 최저) | 수렴 조건 변화에 따른 가계대출 국면 분리 (추가 발견) |",
        "E21", "표 A-2 (Topic 2 행 정정)",
    )

    # Table 1: topic id brackets look like citation numbers -> T-notation
    for old, new in [
        ("| `realestate` | [2, 3] |", "| `realestate` | T2, T3 |"),
        ("| `capital` | [6] |", "| `capital` | T6 |"),
        ("| `macro` | [1] |", "| `macro` | T1 |"),
        ("| `market` | [4, 13] |", "| `market` | T4, T13 |"),
        ("| `aichip` | [12] |", "| `aichip` | T12 |"),
        ("| `earnings` | [7] |", "| `earnings` | T7 |"),
        ("| `residual` | [0, 5, 8, 9, 10, 11] |", "| `residual` | T0, T5, T8, T9, T10, T11 |"),
    ]:
        text = rep(text, old, new, "E22", "표 1 (토픽 번호 표기를 인용번호와 구분)")

    # ---------------- Ⅳ. 실증 분석 ----------------
    text = rep(text, "나아가 완전 수렴 모형(NMF-800)과의 비교 분석", "나아가 강건성 검증 모델(NMF-800)과의 비교 분석", "E23", "4.1절")
    text = rep(text, "모두 $0.991$ 이상의 극히 높은 정합성", "모두 $0.991$ 이상의 높은 정합성", "E24", "4.1절")
    text = rep(
        text,
        "이를 완전한 통계적 독립성으로 단정하기보다는 서로 다른 거시 정책 국면을 포착하는 상이한 이슈 차원으로 해석하는 것이 타당하다.",
        "분석 구간에 따라 관계의 방향과 유의성이 달라지므로 두 국면의 통계적 독립성을 단정할 수 없으며, 두 국면이 서로 다른 이슈 차원을 포착하는지는 추가 검증이 필요하다. 가계대출 국면의 분리는 사전 확정된 6대 국면 체계에 포함되지 않은 추가 발견으로만 보고한다.",
        "E25", "4.1절 (해석 과장 완화)",
    )
    text = rep(text, "| **36.84% (7개월)** |", "| **7 (36.84%)** |", "E26", "표 2 (표기 통일)")
    text = rep(
        text, "\n\n**Table 2-1.",
        "\n\n강건성 검증 모델(NMF-800)에서 동일한 비교를 수행한 결과는 표 2-1과 같다. 6국면 기준 누락률은 43.24%~43.75%로 기준 모델과 유사하였으며, 가계대출을 포함한 7국면 체계에서는 후보 국면 수 증가와 함께 누락률이 50.40%로 높아졌다.\n\n**Table 2-1.",
        "E27", "4.2절 (표 2-1 도입 문장)",
    )
    text = rep(text, "| hhdebt 제외 시 43.64%로 기존과 완벽 일관 |", "| `hhdebt`를 제외한 6국면 기준으로 기준 모델과 유사 |", "E28", "표 2-1")
    text = rep(text, "| 후보 국면 확장 시 복합성 포착 필요성 한층 부각 |", "| 후보 국면 수 증가(6→7)에 따라 활성 신호와 누락 신호가 함께 증가 |", "E29", "표 2-1")

    m = re.search(r"\\multicolumn\{7\}\{l\}\{(.*)\} \|\n(\| \*\*HAC 결합 검정)", text)
    assert m, "[E30] multicolumn 1 not found"
    text = re.sub(r"\\multicolumn\{7\}\{l\}\{(.*)\} \|", lambda mm: mm.group(1) + " | | | | | | |", text)
    assert "\\multicolumn" not in text
    EDIT_LOG.append({"edit_id": "E30", "section": "표 3 (Markdown 비호환 \\multicolumn 제거)"})

    text = rep(
        text, "\n\n**Table 3-1.",
        "\n\n강건성 검증 모델(NMF-800)의 국면 점수로 동일한 회귀를 재추정한 결과는 표 3-1과 같다. 7국면 모형은 설명변수 추가로 $R^2$가 상승하였으나 Adjusted $R^2$는 기준 모델보다 낮았으며, 네 모형 모두에서 `z_macro`와 `z_capital`의 음(-)의 계수는 Holm 보정 후 유의수준 5%에서 유의하게 유지되었다.\n\n**Table 3-1.",
        "E31", "4.3.1절 (표 3-1 도입 문장)",
    )
    text = rep(text, "| 동일 자유도에서 Adj-$R^2$ 8.65%로 최고 적합도 |", "| 네 모형 중 Adj-$R^2$ 최대 (8.65%) |", "E32", "표 3-1")
    text = rep(text, "| 핵심 변수 음(-)의 유의성 100% 보존 확인 |", "| `z_macro`·`z_capital`의 음(-)의 유의성 유지 |", "E33", "표 3-1")

    # 4.3.2: move ARX block before the concluding paragraph and add NMF-800 early-warning result
    m = re.search(r"\n+4\. \*\*엄격한 표본 외\(Strict OOS\) 시계열 예측\(ARX\) 보조 분석\*\*:\n(?:   - [^\n]*\n){3}", text)
    assert m, "[E34] ARX block not found"
    block = m.group(0).strip("\n")
    text = text[: m.start()] + "\n\n" + text[m.end():]
    block = block.replace(
        "연구 A-3(`strict_oos_comparison.csv`)에서 NMF-800 완전 수렴 모델로부터 분리된 가계대출(`hhdebt`) 국면 점유율을",
        "강건성 검증 모델(NMF-800)에서 분리된 가계대출(`hhdebt`) 국면 점유율(`strict_oos_comparison.csv`)을",
    )
    assert "연구 A-3" not in block
    ew = ("강건성 검증 모델(NMF-800)의 `z_macro >= 0.5` 단독 규칙 역시 테스트 평가 가능 기간(17개월)에서 "
          "$TP=0, FP=1, FN=9, TN=7$로 NMF-400과 동일한 결과를 보여, 표본 외 조기경보 성능이 입증되지 않았다는 결론은 수렴 조건과 무관하게 유지되었다.")
    text = rep(text, "따라서 본 연구는 월별 뉴스 국면 지표를",
               block + "\n\n" + ew + "\n\n따라서 본 연구는 월별 뉴스 국면 지표를",
               "E34", "4.3.2절 (ARX 항목 위치 이동, NMF-800 조기경보 결과 추가)")
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    text = rep(
        text,
        "나아가 연구 A-3.2의 주별 데이터 역법 감사(`weekly_period_audit_report.md`, `weekly_diff_method_comparison.csv`) 결과에 따라, ",
        "나아가 테스트 구간 경계 주차의 차분 처리 방식이 결과에 미치는 영향을 점검하기 위해(`weekly_diff_method_comparison.csv`), ",
        "E35", "4.4절 (내부 작업 명칭 제거)",
    )
    text = rep(text, "또한 NMF-800 모델과의 비교", "또한 강건성 검증 모델(NMF-800)과의 비교", "E36", "4.4절")
    text = rep(text, "로 0을 견고히 배제함)", "로 0을 포함하지 않음)", "E37", "4.4절")

    # ---------------- Ⅴ. 결론 ----------------
    text = rep(text, "본 연구의 핵심 기여는 다음 세 가지로 요약된다:", "본 연구의 핵심 기여는 다음 네 가지로 요약된다:", "E38", "5.1절")
    text = rep(
        text, "재현**됨을 입증하였다.\n",
        "재현**됨을 확인하였다.\n"
        "4. **[강건성 검증] NMF 수렴 조건 변화에 대한 주요 결과의 유지 확인**: 기준 모델(NMF-400)의 반복 상한 도달을 보고하고 허용오차 기준 수렴 모델(NMF-800, 447회)과 비교한 결과, 재구성 오차 차이는 0.0073%, Topic 2를 제외한 13개 토픽의 평균 코사인 유사도는 0.9953, 5개 비분할 국면의 월별 비중 상관은 $r = 0.9910 \\sim 0.9998$이었다. 6국면 기준 단일 국면 누락률(43.24%~43.75%), 코스피 회귀에서 `z_macro`·`z_capital`의 유의성, 테스트 17개월 조기경보 결과($TP=0$), 주별 '기업실적' 동조성은 NMF-800에서도 유지되었으며, '시황' 쌍은 `maxlags=4`에서 경계 수준($p_{\\text{holm}} = 0.0508$)으로 나타났다. 또한 수렴 모델에서 가계대출(`hhdebt`) 국면이 부동산 국면으로부터 분리되는 현상을 추가로 관찰하였다.\n",
        "E39", "5.1절 (기여 4 추가)",
    )
    text = rep(text, "적중 0건($TP=0, FP=1$)에 그쳤다.", "적중 0건($TP=0, FP=1$)에 그쳤으며, 이 결과는 NMF-800에서도 동일하였다.", "E40", "5.2절")
    text = rep(
        text, "기사 단위 의미 타당성 검증을 수행할 필요가 있다.\n",
        "기사 단위 의미 타당성 검증을 수행할 필요가 있다.\n"
        "4. **기준 모델의 수렴 경고와 가계대출 국면 분리의 해석 범위**: 기준 모델(NMF-400)은 반복 상한에서 정지하였으며, 허용오차 기준 수렴 모델(NMF-800)에서는 토픽 2가 가계대출 국면으로 재매핑되었다. 본 연구는 사전 확정된 6대 국면 체계를 유지하였으므로 가계대출 국면은 추가 발견으로만 보고하였고, 7국면 체계의 타당성과 안정성은 별도의 검증이 필요하다. 또한 NMF-800의 수렴은 허용오차 기준 정지로서 전역 최적해를 보장하지 않는다.\n"
        "5. **Strict OOS 적용 범위와 검색 데이터의 측정 한계**: Strict OOS 원칙은 텍스트 특징 추출(어휘 사전·IDF·$H_{\\text{train}}$·표준화 모수)에 적용되었으며, 월별 코스피 회귀는 67개월 전체 표본에서 추정한 동시점 설명 회귀이다. ARX 보조 분석에서 관찰된 RMSE 감소(약 9.25%)는 19개월 소표본 결과로서 일반화할 수 없고, 기준금리 변화폭 예측(H2)에서는 개선이 없었다. 또한 네이버 데이터랩 지수는 조회 기간 내 최댓값을 100으로 정규화한 상대지수로서 절대 검색량을 의미하지 않는다.\n",
        "E41", "5.2절 (한계 4·5 추가)",
    )

    # ---------------- REFERENCES [7] ----------------
    text = rep(
        text,
        "[7] S.-H. Kim, Y.-J. Lee, J.-Y. Shin, and K.-Y. Park, “Text Mining for Macroeconomic Analysis,” *Journal of Korean Economic Analysis*, vol. 26, no. 1, pp. 1-65, 2020. (김수현, 이영준, 신진영, 박기영, “거시경제 분석을 위한 텍스트 마이닝,” *한국경제의 분석*, 제26권 제1호, pp. 1-65, 2020.)",
        "[7] S. Kim, Y. J. Lee, J. Shin, and K. Y. Park, “Text Mining for Economic Analysis,” *Journal of Korean Economic Analysis*, vol. 26, no. 1, pp. 1-70, 2020. DOI: 10.22823/jkea.26.1.202004.1. (김수현, 이영준, 신진영, 박기영, “거시경제 분석을 위한 텍스트 마이닝,” *한국경제의 분석*, 제26권 제1호, pp. 1-70, 2020.)",
        "E42", "REFERENCES [7]",
    )
    text = rep(text, "**[ 저자 미정 (심사 대비 최종 개정본) ]**", "**[ 저자 미정 (투고 전 개정 초안, 2026-11-07) ]**", "E43", "표제부")
    return text


TABLE_RE = re.compile(r"(?<![가-힣])(Table|표) (F-1|A-1|A-2|B-1|E-1|C-1|D-1|2-1|3-1|[1-4])(?![\d\-])")


def renumber_tables(text: str) -> tuple[str, dict]:
    captions = [(m.start(), m.group(1)) for m in re.finditer(r"\*\*Table (F-1|A-1|A-2|B-1|E-1|C-1|D-1|2-1|3-1|[1-4])\.", text)]
    order = [lab for _, lab in sorted(captions)]
    assert len(order) == len(set(order)) == 13, order
    mapping = {lab: str(i) for i, lab in enumerate(order, 1)}
    text = TABLE_RE.sub(lambda m: f"{m.group(1)} {mapping[m.group(2)]}", text)
    EDIT_LOG.append({"edit_id": "E44", "section": "전체 (표 번호 등장순 1~13 연번화)"})
    return text, mapping


def citation_checks(text: str) -> dict:
    body, refs = text.split("## REFERENCES")
    ref_ids = [int(x) for x in re.findall(r"^\[(\d+)\]", refs.strip(), flags=re.M)]
    first_seen: list[int] = []
    cited: set[int] = set()
    for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
        nums: list[int] = []
        for part in m.group(1).split(","):
            part = part.strip()
            if "-" in part:
                a, b = (int(x) for x in part.split("-"))
                nums += list(range(a, b + 1))
            else:
                nums.append(int(part))
        for n in nums:
            if n not in cited:
                first_seen.append(n)
            cited.add(n)
    return {
        "reference_count": len(ref_ids),
        "reference_ids_sequential": ref_ids == list(range(1, 25)),
        "cited_numbers": sorted(cited),
        "uncited_references": sorted(set(ref_ids) - cited),
        "citations_without_reference": sorted(cited - set(ref_ids)),
        "first_appearance_order": first_seen,
        "first_appearance_is_ascending": first_seen == sorted(first_seen),
    }


REQUIRED = [
    "0.161879", "0.078067", "4.683257", "0.000573", "0.169783", "0.071282", "0.169581", "0.086539",
    "43.75%", "43.24%", "43.64%", "50.40%", "TP=0, FP=1, FN=9, TN=7", "0.9802", "0.9953", "0.9686", "0.7846",
    "0.0073%", "447", "0.9910", "0.9998", "0.9648", "0.9693", "0.0467", "12.28%", "6.05%", "5.99%",
    "7/11 = 63.64%", "7/7 = 100%", "15.2825", "13.8687", "0.1097", "0.1266", "0.1267",
    "$N=291$", "$N=208$", "$N=82$", "292개 ISO 8601 주차", "209주", "83주", "|\\Delta r| \\le 0.0045",
    "+0.4718", "+0.4687", "+0.4984", "+0.4920", "0.0508", "0.0409", "0.0432", "0.0011", "0.0014",
    "pp. 1-70", "10.22823/jkea.26.1.202004.1", "Text Mining for Economic Analysis",
    "Adjusted } R^2 = 0.078067",
]
FORBIDDEN = [
    "pp. 1-65", "과거 학습 창을 기준으로만", "적용 (과거 롤링 창)", "AI·반도체, 금리", "\\multicolumn",
    "연구 A-3", "완벽한 수치적 재현성", "정밀하게 분리되는 구조적 분화", "견고한 대중 관심 동조화가 실증",
    "rigorous methodological and empirical foundations", "bifurcated cleanly", "| [2, 3] |", "Text Mining for Macroeconomic Analysis",
]


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=False)
    assert not OUT.exists()
    before = snapshot()
    before.to_csv(RUN_DIR / "protected_hashes_before.csv", index=False, encoding="utf-8-sig")

    src = SRC.read_text(encoding="utf-8")
    text = build(src)
    text, mapping = renumber_tables(text)

    captions = [int(x) for x in re.findall(r"\*\*Table (\d+)\.", text)]
    tags = [int(x) for x in re.findall(r"\\tag\{(\d+)\}", text)]
    table_refs = sorted({int(x) for x in re.findall(r"(?<![가-힣])표 (\d+)(?![\d\-])", text)})
    missing = [s for s in REQUIRED if s not in text]
    present_forbidden = [s for s in FORBIDDEN if s in text]
    cites = citation_checks(text)
    src_refs = src.split("## REFERENCES")[1].strip().splitlines()
    out_refs = text.split("## REFERENCES")[1].strip().splitlines()
    changed_refs = [i + 1 for i, (a, b) in enumerate(zip(src_refs, out_refs)) if a != b]

    checks = {
        "table_label_mapping_old_to_new": mapping,
        "table_captions_in_order": captions,
        "table_captions_sequential": captions == list(range(1, 14)),
        "table_refs_in_text": table_refs,
        "table_refs_all_have_caption": set(table_refs) <= set(captions),
        "equation_tags": tags,
        "equation_tags_sequential": tags == list(range(1, len(tags) + 1)),
        "required_values_missing": missing,
        "forbidden_phrases_present": present_forbidden,
        "citations": cites,
        "reference_lines_changed": changed_refs,
        "edits_applied": len(EDIT_LOG),
        "chars_src": len(src),
        "chars_out": len(text),
    }
    assert not missing, missing
    assert not present_forbidden, present_forbidden
    assert checks["table_captions_sequential"] and checks["table_refs_all_have_caption"]
    assert cites["reference_count"] == 24 and not cites["uncited_references"] and not cites["citations_without_reference"]
    assert changed_refs == [7], changed_refs

    OUT.write_text(text, encoding="utf-8")
    after = snapshot()
    after["match_before"] = after["sha256"].values == before["sha256"].values
    after.to_csv(RUN_DIR / "protected_hashes_after.csv", index=False, encoding="utf-8-sig")
    checks["protected_files_checked"] = int(len(after))
    checks["protected_files_modified"] = int((~after["match_before"]).sum())
    checks["edit_log"] = EDIT_LOG
    (RUN_DIR / "a6_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    assert checks["protected_files_modified"] == 0
    print(json.dumps({k: v for k, v in checks.items() if k != "edit_log"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

