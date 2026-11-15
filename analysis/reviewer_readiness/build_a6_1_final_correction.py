"""
Study A-6.1: JKIICE Final Draft Correction and Statistical Expression Refinement
================================================================================
Input  : docs/drafts/PAPER_DRAFT_JKIICE_DRAFT_REVISION_20261107.md (read-only)
Output : docs/PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md
         docs/verification/A6_1_FINAL_CORRECTION_LOG_20261107.md
         data/processed/reviewer_readiness/RUN_20261107_A6_1_FINAL_CORRECTION_01/
             protected_hashes_before.csv, protected_hashes_after.csv, a6_1_checks.json
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
SRC = DOCS / "drafts" / "PAPER_DRAFT_JKIICE_DRAFT_REVISION_20261107.md"
OUT = DOCS / "PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md"
LOG_OUT = DOCS / "verification" / "A6_1_FINAL_CORRECTION_LOG_20261107.md"
RUN_DIR = RR / "RUN_20261107_A6_1_FINAL_CORRECTION_01"

PROTECTED = [
    DOCS / "PAPER_DRAFT_JKIICE.md",
    DOCS / "drafts" / "PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md",
    DOCS / "drafts" / "PAPER_DRAFT_JKIICE_A4_20261106.md",
    DOCS / "verification" / "A4_CHANGELOG_20261106.md",
    DOCS / "verification" / "A4_CLAIM_EVIDENCE_MATRIX_20261106.csv",
    DOCS / "verification" / "A4_FINAL_QC_20261106.md",
    SRC,
    DOCS / "verification" / "A6_DRAFT_CHANGELOG_20261107.md",
    DOCS / "verification" / "A6_DRAFT_QC_20261107.md",
]
for d in [
    "RUN_20261106_NMF_CONVERGENCE_01",
    "RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01",
    "RUN_20261106_A3_CONSISTENCY_AUDIT_01",
    "RUN_20261106_A3_2_WEEKLY_PERIOD_AUDIT_01",
    "RUN_20261106_A5_REFERENCE_AUDIT_01",
    "RUN_20261106_A5_1_REFERENCE_CORRECTION_01",
    "RUN_20261107_A6_DRAFT_REVISION_01",
]:
    p_dir = RR / d
    if p_dir.exists():
        PROTECTED += sorted(p for p in p_dir.iterdir() if p.is_file())


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
    EDIT_LOG.append({"edit_id": edit_id, "section": section, "old": old, "new": new})
    return text.replace(old, new)


def rep_line(text: str, startswith: str, new_line: str, edit_id: str, section: str) -> str:
    lines = text.split("\n")
    idx = [i for i, ln in enumerate(lines) if ln.startswith(startswith)]
    assert len(idx) == 1, f"[{edit_id}] line anchor matched {len(idx)} times: {startswith!r}"
    old_line = lines[idx[0]]
    lines[idx[0]] = new_line
    EDIT_LOG.append({"edit_id": edit_id, "section": section, "old": old_line, "new": new_line})
    return "\n".join(lines)


def build_final(text: str) -> str:
    # 0. 표제부
    text = rep(
        text,
        "**[ 저자 미정 (투고 전 개정 초안, 2026-11-07) ]**",
        "**[ 저자 미정 (투고 전 최종본, 2026-11-07) ]**",
        "F01", "표제부"
    )

    # 1. 요약 / ABSTRACT: Zero-Leakage 범위 정밀화
    text = rep(
        text,
        "미래 정보 누수(Data Leakage)를 원천 차단하기 위해 학습 기간(2021.01~2024.12, 48개월) 전용 어휘 사전(22,193개 단어)과 IDF, NMF 기저 행렬($H$, 14개 잠재 토픽)을 고정하여 테스트 기간(2025.01~2026.07, 19개월)으로 확장 투영하는 엄격한 표본 외(Strict Out-of-Sample) 파이프라인을 확립하였다.",
        "뉴스 텍스트 특징 추출 파이프라인에서 미래 정보 누수(Data Leakage)를 차단하기 위해 학습 기간(2021.01~2024.12, 48개월) 전용 어휘 사전(22,193개 단어)과 IDF, NMF 기저 행렬($H$, 14개 잠재 토픽)을 고정하여 테스트 기간(2025.01~2026.07, 19개월)으로 확장 투영하는 엄격한 표본 외(Strict Out-of-Sample) 파이프라인을 확립하였다.",
        "F02", "요약 (Zero-Leakage 범위 텍스트 파이프라인으로 한정)"
    )
    text = rep(
        text,
        "To strictly eliminate look-ahead bias, vocabulary (22,193 words), IDF, and the NMF basis matrix ($H$, $K=14$) were fixed strictly using the training period (2021.01-2024.12, 48 months) and projected onto the test period (2025.01-2026.07, 19 months) under a Strict Out-of-Sample (Strict OOS) pipeline.",
        "To prevent look-ahead bias in text feature extraction, vocabulary (22,193 words), IDF, and the NMF basis matrix ($H$, $K=14$) were fixed strictly using the training period (2021.01-2024.12, 48 months) and projected onto the test period (2025.01-2026.07, 19 months) under a Strict Out-of-Sample (Strict OOS) pipeline.",
        "F03", "ABSTRACT (Zero-Leakage 범위 텍스트 특징 추출로 한정)"
    )

    # 2. 1장 서론: 단위근 추세 및 정상성 표현 수정
    text = rep(
        text,
        "넷째, **이종 빅데이터를 활용한 주별 차분 교차 검증 및 시계열 정상성·유한 표본 강건성 통제의 부족**이다.",
        "넷째, **이종 빅데이터를 활용한 주별 차분 교차 검증 및 시계열 추세·유한 표본 강건성 통제의 부족**이다.",
        "F04", "1장 서론 (시계열 정상성 -> 시계열 추세)"
    )
    text = rep(
        text,
        "또한 시계열 수준값(Level)의 비정상성(단위근 추세)을 제거하지 않은 채 단순 상관계수를 보고하거나,",
        "또한 시계열 수준값(Level)의 추세를 통제하지 않은 채 단순 상관계수를 보고하거나,",
        "F05", "1장 서론 (비정상성(단위근 추세) 제거 -> 추세 통제)"
    )

    # 3. 2.3절: 시계열 차분 변환 및 가짜 상관 표현 객관화 (Stock & Watson [20] 유지)
    text = rep(
        text,
        "### 2.3 시계열 정상성, Newey-West HAC 공분산, 다중검정 및 블록 부트스트랩",
        "### 2.3 시계열 1차 차분 변환, Newey-West HAC 공분산, 다중검정 및 블록 부트스트랩",
        "F06", "2.3절 제목 (시계열 정상성 -> 시계열 1차 차분 변환)"
    )
    text = rep(
        text,
        "수준값(Level) 시계열이 단위근 추세를 공유할 경우 실제 단기 동조성이 없더라도 높은 상관계수가 산출되는 가짜 상관(Spurious Correlation)이 발생한다[20]. 본 연구에서는 단위근 추세에 의한 착시를 방지하기 위해 상관 및 교차 검증 시 지수 수준값 대신 **월간 수익률·차분 또는 주간 1차 차분(First Difference)** 변환 시계열을 사용한다.",
        "수준값(Level) 시계열이 공통 추세를 공유할 경우 실제 단기 동조성이 없더라도 높은 상관계수가 산출되는 가짜 상관(Spurious Correlation)이 발생할 수 있다[20]. 본 연구에서는 단위근 검정을 별도로 수행하여 정상성을 단정하기보다는, 추세적 연동에 따른 가짜 상관 위험을 완화하고 단기 변동 간의 동행성을 관찰하기 위해 지수 수준값 대신 **월간 수익률·차분 또는 주간 1차 차분(First Difference)** 변환 시계열을 사용한다.",
        "F07", "2.3절 본문 (단위근 추세 단정 완화 및 1차 차분 목적 객관화, [20] 유지)"
    )

    # 4. 3.2절: Zero-Leakage 표현 텍스트 특징 추출 구조로 한정
    text = rep(
        text,
        "19개월 표본 외 테스트 기간(2025~2026.07)으로 투영하는 무누수(Zero-Leakage) 아키텍처를 구현하였다.",
        "19개월 표본 외 테스트 기간(2025~2026.07)으로 투영하는 뉴스 텍스트 특징 추출의 무누수(Zero-Leakage) 파이프라인을 구현하였다.",
        "F08", "3.2절 (Zero-Leakage 범위 한정)"
    )

    # 5. Table 4: 13개 토픽 코사인 중앙값 검증 결과 정정 (0.999510 -> 0.999093)
    text = rep(
        text,
        "| **Topic 2 제외 13개 토픽 평균 Cosine** | — | **$0.995269$** | 중앙값 $0.999510$, 최솟값 $0.968629$ | Topic 2 제외 13개 토픽은 평균 $0.995$ 수준의 높은 유사도 |",
        "| **Topic 2 제외 13개 토픽 평균 Cosine** | — | **$0.995269$** | 중앙값 $0.999093$, 최솟값 $0.968629$ | Topic 2 제외 13개 토픽은 평균 $0.995$ 수준의 높은 유사도 |",
        "F09", "Table 4 (13개 토픽 코사인 중앙값 원본 검증 수치 0.999093으로 정정)"
    )

    # 6. Table 5: 네이버 검색 상대지수 API 전역 정규화 한계 명시
    text = rep_line(
        text,
        "| **6. 주별 네이버 검색 1차 차분 교차 검증 (표 12, 표 13)** |",
        "| **6. 주별 네이버 검색 1차 차분 교차 검증 (표 12, 표 13)** | `Train`(208w) / `Eval OOS`(82w) / `Full`(291w) 분리 차분·검정 | 뉴스 지표는 고정 추출기 사용, 차분은 구간별 독립 수행 | **누수 없음 (0건)** (단, 검색 지수 API 전역 정규화 한계 존재) | **Strict OOS 테스트 기간($N=82$주) 동시점($h=0$) 외부 교차 검증** (원자료 상대지수 스케일링 특성 유의) |",
        "F10", "Table 5 (네이버 검색 지수 API 전역 정규화 한계 명시)"
    )

    # 7. 4.2절: 다중 국면 누락률 표현 정밀화 ("비슷하게 유지" 및 7국면 설명)
    text = rep(
        text,
        "강건성 검증 모델(NMF-800)에서 동일한 비교를 수행한 결과는 표 9과 같다. 6국면 기준 누락률은 43.24%~43.75%로 기준 모델과 유사하였으며, 가계대출을 포함한 7국면 체계에서는 후보 국면 수 증가와 함께 누락률이 50.40%로 높아졌다.",
        "강건성 검증 모델(NMF-800)에서 동일한 비교를 수행한 결과는 표 9과 같다. 동일한 6국면 체계에서 NMF-800 Legacy-6의 누락률은 43.24%로 기준 모델(43.75%)과 비슷하게 유지되었으며(6국면 부분집합 시 43.64%), 가계대출을 포함한 7국면 체계에서는 후보 국면 수 증가(6→7)에 따라 활성 신호 수와 누락 신호 수가 함께 증가하면서 누락률이 50.40%로 산출되었다.",
        "F11", "4.2절 (다중 국면 누락률 '비슷하게 유지' 및 7국면 후보 국면 증가 설명)"
    )
    text = rep(
        text,
        "| **NMF-800 (Legacy-6 합산)** | 6 | **36개월** (53.73%) | **111건** | **48건** | **`43.24%`** | **`-0.51%p`** | 동일 6국면 조건에서 누락률 사실상 불변 |",
        "| **NMF-800 (Legacy-6 합산)** | 6 | **36개월** (53.73%) | **111건** | **48건** | **`43.24%`** | **`-0.51%p`** | 동일 6국면 조건에서 누락률(43.24%)이 기준 모델(43.75%)과 비슷하게 유지 |",
        "F12", "Table 9 (비슷하게 유지 표현 정밀화)"
    )
    text = rep(
        text,
        "| **NMF-800 (6국면 부분집합)** | 6 | **37개월** (55.22%) | **110건** | **48건** | **`43.64%`** | **`-0.11%p`** | `hhdebt`를 제외한 6국면 기준으로 기준 모델과 유사 |",
        "| **NMF-800 (6국면 부분집합)** | 6 | **37개월** (55.22%) | **110건** | **48건** | **`43.64%`** | **`-0.11%p`** | `hhdebt`를 제외한 6국면 기준으로 누락률(43.64%)이 기준 모델과 비슷하게 유지 |",
        "F13", "Table 9 (비슷하게 유지 표현 정밀화)"
    )

    # 8. 4.4절: 비정상 시계열 가짜 상관 표현 정밀화
    text = rep(
        text,
        "비정상 시계열의 공통 추세로 인한 가짜 상관을 배제하기 위해 각 구간(`Train`, `Eval OOS`, `Full`) 내부에서 뉴스 점유율과 검색 지수에 각각 **주간 1차 차분(First Difference)**을 적용하였으며",
        "원자료 시계열의 공통 추세로 인한 가짜 상관 위험을 완화하기 위해 각 구간(`Train`, `Eval OOS`, `Full`) 내부에서 뉴스 점유율과 검색 지수에 각각 **주간 1차 차분(First Difference)**을 적용하였으며",
        "F14", "4.4절 (비정상 시계열 배제 -> 원자료 시계열 공통 추세 가짜 상관 위험 완화)"
    )

    # 9. 5.1절 결론 기여 3: 단위근 추세 제거 -> 주별 원자료에 1차 차분을 적용한 시계열 (사용자 지정 권장 문구 반영)
    text = rep(
        text,
        "또한 단위근 추세를 제거한 주별 1차 차분 시계열(291주)과 24개 검정 HAC Holm 보정 및 이동 블록 부트스트랩($B=2,000$)을 통해,",
        "또한 주별 원자료에 1차 차분을 적용한 시계열(291주)과 24개 검정 HAC Holm 보정 및 이동 블록 부트스트랩($B=2,000$)을 통해,",
        "F15", "5.1절 결론 기여 3 (사용자 권장 문구 '주별 원자료에 1차 차분을 적용한 시계열' 반영)"
    )

    # 10. 5.2절 결론 한계 5: Zero-Leakage 범위 및 상대지수 API 전역 정규화 한계 보강
    text = rep(
        text,
        "5. **Strict OOS 적용 범위와 검색 데이터의 측정 한계**: Strict OOS 원칙은 텍스트 특징 추출(어휘 사전·IDF·$H_{\\text{train}}$·표준화 모수)에 적용되었으며, 월별 코스피 회귀는 67개월 전체 표본에서 추정한 동시점 설명 회귀이다. ARX 보조 분석에서 관찰된 RMSE 감소(약 9.25%)는 19개월 소표본 결과로서 일반화할 수 없고, 기준금리 변화폭 예측(H2)에서는 개선이 없었다. 또한 네이버 데이터랩 지수는 조회 기간 내 최댓값을 100으로 정규화한 상대지수로서 절대 검색량을 의미하지 않는다.",
        "5. **Strict OOS 적용 범위와 검색 데이터의 정규화 한계**: 무누수(Zero-Leakage) 및 Strict OOS 원칙은 뉴스 텍스트 특징 추출 파이프라인(어휘 사전, IDF, $H_{\\text{train}}$, 표준화 모수)에 엄격히 적용된 것으로, 연구 전체의 모든 외부 데이터가 완전 무누수임을 의미하지 않는다. 월별 코스피 회귀는 67개월 전체 표본에서 추정한 동시점 설명 회귀이며, 네이버 데이터랩 지수는 주별 차분을 구간별로 분리 수행하였으나 원자료 자체가 조회 기간 전체 최댓값(=100) 기준 상대지수로 정규화된 API 구조적 한계를 갖는다. 또한 ARX 보조 분석에서 관찰된 RMSE 감소(약 9.25%)는 19개월 소표본 결과로서 일반화할 수 없고, 기준금리 변화폭 예측(H2)에서는 개선이 없었다.",
        "F16", "5.2절 결론 한계 5 (Zero-Leakage 텍스트 파이프라인 한정 및 검색 API 전역 상대지수 한계 명시)"
    )

    return text


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
    }


REQUIRED_VALUES = [
    "0.161879", "0.078067", "4.683257", "0.000573", "0.169783", "0.071282", "0.169581", "0.086539",
    "43.75%", "43.24%", "43.64%", "50.40%", "TP=0, FP=1, FN=9, TN=7", "0.9802", "0.9953", "0.9686", "0.7846",
    "0.999093",  # newly verified median
    "0.0073%", "447", "0.9910", "0.9998", "0.9648", "0.9693", "0.0467", "12.28%", "6.05%", "5.99%",
    "7/11 = 63.64%", "7/7 = 100%", "15.2825", "13.8687", "0.1097", "0.1266", "0.1267",
    "$N=291$", "$N=208$", "$N=82$", "292개 ISO 8601 주차", "209주", "83주", "|\\Delta r| \\le 0.0045",
    "+0.4718", "+0.4687", "+0.4984", "+0.4920", "0.0508", "0.0409", "0.0432", "0.0011", "0.0014",
    "pp. 1-70", "10.22823/jkea.26.1.202004.1", "Text Mining for Economic Analysis",
    "J. H. Stock and M. W. Watson",
]

FORBIDDEN_PHRASES = [
    "단위근 추세를 제거한",
    "단위근을 제거",
    "정상성을 확보",
    "정상성 확보",
    "시계열 정상성·",
    "### 2.3 시계열 정상성",
    "0.999510",  # superseded median
    "pp. 1-65",
    "\\multicolumn",
    "연구 A-3",
    "완벽한 일관성",
]


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=False)
    assert not OUT.exists()
    assert not LOG_OUT.exists()

    before = snapshot()
    before.to_csv(RUN_DIR / "protected_hashes_before.csv", index=False, encoding="utf-8-sig")

    src = SRC.read_text(encoding="utf-8")
    text = build_final(src)

    captions = [int(x) for x in re.findall(r"\*\*Table (\d+)\.", text)]
    tags = [int(x) for x in re.findall(r"\\tag\{(\d+)\}", text)]
    table_refs = sorted({int(x) for x in re.findall(r"(?<![가-힣])표 (\d+)(?![\d\-])", text)})
    cites = citation_checks(text)

    missing = [s for s in REQUIRED_VALUES if s not in text]
    present_forbidden = [s for s in FORBIDDEN_PHRASES if s in text]

    checks = {
        "edits_applied": len(EDIT_LOG),
        "chars_src": len(src),
        "chars_out": len(text),
        "table_captions_sequential": captions == list(range(1, 14)),
        "table_refs_all_have_caption": set(table_refs) <= set(captions),
        "equation_tags_sequential": tags == list(range(1, len(tags) + 1)),
        "required_values_missing": missing,
        "forbidden_phrases_present": present_forbidden,
        "citations": cites,
    }

    assert not missing, f"Missing required values: {missing}"
    assert not present_forbidden, f"Found forbidden phrases: {present_forbidden}"
    assert checks["table_captions_sequential"]
    assert checks["table_refs_all_have_caption"]
    assert checks["equation_tags_sequential"]
    assert cites["reference_count"] == 24 and not cites["uncited_references"] and not cites["citations_without_reference"]

    OUT.write_text(text, encoding="utf-8")

    after = snapshot()
    after["match_before"] = after["sha256"].values == before["sha256"].values
    after.to_csv(RUN_DIR / "protected_hashes_after.csv", index=False, encoding="utf-8-sig")

    checks["protected_files_checked"] = int(len(after))
    checks["protected_files_modified"] = int((~after["match_before"]).sum())
    checks["edit_log"] = EDIT_LOG

    (RUN_DIR / "a6_1_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    assert checks["protected_files_modified"] == 0

    print("PASS: Draft final created and all checks passed!")
    print(f"Edits applied: {len(EDIT_LOG)}")
    print(f"Protected files checked: {len(after)}, modified: {checks['protected_files_modified']}")


if __name__ == "__main__":
    main()
