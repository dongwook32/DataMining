"""Export v4 research results as Excel workbooks.

Use python -m analysis.export_v4_results_to_excel for the stored paper run.
Use the v4 runner's --excel-dir option for a newly computed run.
"""

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from config import project_root

ROOT = project_root()
PROCESSED = ROOT / "data" / "processed"
PAPER = ROOT / "output" / "paper_20261116"
BASELINE = "RUN_PHASE5_6_20261027_184959"
LEARNING = "01_전처리_학습.xlsx"
ANALYSIS = "02_중간_분석_검증.xlsx"
FINAL = "03_최종_결과.xlsx"

# The supplemental scripts do not all emit run IDs. Only use these paths
# with the documented paper run, never with a newly fitted model.
SUPPLEMENTS = (
    ("panel", "monthly_panel", "경제지표와 연구 변수를 월별로 결합한 자료"),
    ("reactions", "verification_ols_results", "코스피 회귀계수와 검정 결과"),
    ("reactions", "verification_correlation_lag_results", "기준금리 변화와 뉴스 국면의 시차별 상관"),
    ("reactions", "verification_warning_performance_results", "조기경보의 적중·오경보·누락 집계"),
    ("supplemental_validation", "single_vs_multi_*", "단일 대표 국면과 다중 활성 국면 비교"),
    ("supplemental_validation", "news_search_*", "주별 뉴스·검색 패널과 상관·HAC 검정"),
    ("reviewer_readiness/RUN_20261106_161800", "literature_comparison_matrix", "선행연구 자료·방법 비교"),
    ("reviewer_readiness/RUN_20261106_161800", "*topic*", "토픽 모델 품질·대표 단어·반복 학습 안정성"),
    ("reviewer_readiness/RUN_20261106_161800", "regime_mapping_stability", "반복 학습에서 동일 국면이 재현된 횟수"),
    ("reviewer_readiness/RUN_20261106_161800", "multi_regime_case_*", "다중 활성 사례의 선정 기준과 근거"),
    ("reviewer_readiness/RUN_20261106_161800", "single_multi_case_comparison", "사례별 단일·다중 국면 비교"),
    ("reviewer_readiness/RUN_20261106_161800", "news_search_*", "검색 결과의 시차 민감도와 신뢰구간"),
    ("reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01", "*", "NMF 학습 반복 상한에 따른 수렴 비교"),
    ("reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01", "*", "수렴 모델로 바꿨을 때 후속 분석의 변화"),
)
FIELD_HELP = {
    "run_id": "이 표를 만든 실행의 식별자",
    "month": "기준 연월",
    "period": "분석 구간. train은 학습, test 또는 eval은 평가, full은 전체",
    "article_id": "학습 표본에 포함된 기사의 식별자. 문자로 보존",
    "order": "학습 표본에 들어간 순서",
    "term": "모델이 사용한 어휘",
    "df_train": "학습 기간에 해당 단어가 나타난 기사 수",
    "idf": "여러 기사에 흔하게 등장하는 단어의 비중을 낮추는 가중치",
    "n_docs": "해당 월 기사 수",
    "n_train": "학습 구간에 포함된 관측값 수",
    "n_test": "테스트 구간에 포함된 관측값 수",
    "n_valid": "토픽 비중을 계산할 수 있는 기사 수",
    "index": "어휘 목록에서 해당 단어의 위치",
    "topic": "모델이 찾은 토픽의 번호",
    "best_slug": "단어 가중치가 가장 많이 겹친 경제 이슈 코드",
    "best_share": "가장 잘 맞는 경제 이슈에 속한 단어 가중치의 비중",
    "mass_ratio": "두 번째로 잘 맞는 이슈의 가중치를 첫 번째 이슈의 가중치로 나눈 값",
    "assigned_slug": "해당 토픽이 배정된 경제 이슈 코드",
    "residual_share": "국면에 배정되지 않은 토픽 점수의 비중 (0~1)",
    "forecast_month": "예측 대상 연월",
    "last_available_obs_month": "해당 예측에 사용할 수 있었던 마지막 연월",
    "actual_kospi_ret": "실제 코스피 월 로그수익률 (%)",
    "actual_base_rate_diff": "실제 기준금리 전월 대비 변화 (%p)",
    "kospi_ret_std": "월 코스피 로그수익률을 과거 변동성으로 나눈 값",
    "n": "분석에 포함된 관측값 수",
    "r": "상관계수. 부호는 방향, 절댓값은 관계의 강도",
    "coef": "다른 조건이 같을 때 분석 변수 1단위 차이에 해당하는 결과의 차이",
    "p_raw": "여러 검정을 한꺼번에 수행한 데 대한 보정 전 p값",
    "p_holm": "여러 검정을 고려해 Holm 방식으로 보정한 p값",
    "lag_month": "두 월별 자료를 비교할 때 적용한 개월 차이",
    "kospi_ret": "코스피 월 로그수익률 (%)",
    "base_rate_diff": "한국은행 기준금리의 전월 대비 변화 (%p)",
    "rmse": "예측 오차를 제곱해 평균 낸 뒤 제곱근을 취한 값",
    "mae": "예측 오차의 절댓값을 평균한 값",
    "tp": "경보를 냈고 실제 하락한 건수",
    "fp": "경보를 냈으나 하락하지 않은 건수",
    "fn": "경보를 내지 않았으나 실제 하락한 건수",
    "tn": "경보를 내지 않았고 하락하지 않은 건수",
    "precision": "발령한 경보 중 실제 하락을 맞힌 비율",
}
DOMAINS = dict(macro="금리·물가", realestate="부동산", hhdebt="가계대출", trade="무역",
               aichip="첨단산업", market="시황", earnings="기업실적", capital="자본거래")
HEADER_FILL = PatternFill("solid", fgColor="243D56")
HEADER_FONT = Font(name="맑은 고딕", bold=True, color="FFFFFF")
NUMBER = re.compile(r"[+-]?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")


def field_help(field):
    name = field.lower()
    if name in FIELD_HELP:
        return FIELD_HELP[name]
    prefix, _, domain = name.partition("_")
    if domain in DOMAINS and prefix == "share":
        return f"{DOMAINS[domain]} 이슈에 배정된 토픽의 점수 비중 (0~1)"
    if domain in DOMAINS and prefix == "z":
        return f"{DOMAINS[domain]} 비중이 학습 평균에서 표준편차 몇 배만큼 떨어져 있는지 나타내는 점수"
    if domain in DOMAINS and prefix == "status":
        return f"{DOMAINS[domain]} 이슈의 모델 내 표현 및 분석 가능 상태"
    if prefix == "topic" and domain.isdigit():
        return f"모델이 찾은 토픽 {domain}의 월별 점수 비중 (0~1)"
    if name.endswith(("_pred", "_error")) and prefix in {"h1", "h2"}:
        target = "코스피 수익률 (%)" if prefix == "h1" else "기준금리 변화 (%p)"
        kind = "예측값" if name.endswith("_pred") else "예측 오차"
        return f"{target}의 모형별 {kind}. zero는 0 기준, ar은 자기회귀, news는 뉴스 변수 추가"
    return None


def csv_value(field, raw):
    if raw == "":
        return None
    name = field.lower()
    if name == "id" or name.endswith(("_id", "_ids", "_code", "_hash", "_sha256")):
        return raw
    if NUMBER.fullmatch(raw):
        if any(ch in raw for ch in ".eE"):
            number = float(raw)
            return number if math.isfinite(number) else raw
        if len(raw.lstrip("+-")) <= 15:
            return int(raw)
    return raw


def plain_cell(sheet, value):
    if isinstance(value, str):
        if len(value) > 32767:
            raise ValueError(f"{sheet.title}: Excel 셀의 문자 수 한도 초과")
        cell = WriteOnlyCell(sheet, value)
        cell.data_type = "s"
        return cell
    return value


def write_table(book, title, headers, rows, *, widths=None):
    sheet = book.create_sheet(title[:31])
    sheet.freeze_panes = "A2"
    for index, header in enumerate(headers, 1):
        width = widths[index - 1] if widths else max(16, min(37, len(header) + 4))
        sheet.column_dimensions[get_column_letter(index)].width = width
    heading = [plain_cell(sheet, h) for h in headers]
    for cell in heading:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    sheet.append(heading)
    count = 1
    for row in rows:
        if count == 1048576:
            raise ValueError(f"{title}: Excel 시트의 행 수 한도 초과")
        sheet.append([plain_cell(sheet, value) for value in row])
        count += 1
    return sheet.title


def json_rows(value, prefix=""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from json_rows(item, f"{prefix}.{key}" if prefix else str(key))
    else:
        if isinstance(value, (list, tuple)):
            value = json.dumps(value, ensure_ascii=False)
        elif isinstance(value, float) and not math.isfinite(value):
            value = None
        yield prefix, value


def display_path(path):
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def write_workbook(path, run_id, sources, extra=()):
    workbook = Workbook(write_only=True)
    overview = workbook.create_sheet("파일 안내")
    guide = workbook.create_sheet("항목 설명")
    overview.column_dimensions["A"].width = 33
    overview.column_dimensions["B"].width = 75
    overview.column_dimensions["C"].width = 96
    guide.column_dimensions["A"].width = 34
    guide.column_dimensions["B"].width = 34
    guide.column_dimensions["C"].width = 93
    overview.freeze_panes = "A4"
    guide.freeze_panes = "A2"
    overview.append(["기준 실행", run_id])
    overview.append(["값 읽기", "식별자와 15자리를 넘는 정수는 문자로 표시합니다. 실수는 Excel 숫자 정밀도로 표시합니다."])
    overview.append(["시트", "내용", "근거 파일"])
    guide.append(["시트", "열 이름", "한국어 설명"])

    for source, description in sources:
        if source.suffix == ".csv":
            with source.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.reader(handle)
                headers = next(reader)
                rows = (tuple(csv_value(key, val) for key, val in zip(headers, row, strict=True))
                        for row in reader)
                sheet = write_table(workbook, source.stem, headers, rows)
        elif source.suffix == ".npy":
            matrix = np.load(source, allow_pickle=False)
            headers = ["어휘 인덱스", *[f"topic_{i}" for i in range(matrix.shape[0])]]
            rows = ((i, *map(float, row)) for i, row in enumerate(matrix.T))
            sheet = write_table(workbook, source.stem, headers, rows)
        else:
            data = read_json(source)
            headers = ["항목", "값"]
            sheet = write_table(workbook, source.stem, headers, json_rows(data), widths=(60, 75))
        overview.append([sheet, description, display_path(source)])
        for header in headers:
            guide.append([sheet, header, field_help(header) or ""])

    for name, headers, rows, description in extra:
        sheet = write_table(workbook, name, headers, rows)
        overview.append([sheet, description, "v4 실행 중 계산"])
        for header in headers:
            explanation = field_help(header)
            if explanation:
                guide.append([sheet, header, explanation])
    workbook.save(path)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def checked_path(path, digest, *, allow_text_eol=False):
    with path.open("rb") as handle:
        actual = hashlib.file_digest(handle, "sha256").hexdigest()
    expected = digest.casefold()
    if actual == expected:
        return path
    # Git can check out archived CSV/JSON with different line endings.
    if allow_text_eol and path.suffix in {".csv", ".json"}:
        lf = path.read_bytes().replace(b"\r\n", b"\n")
        if any(hashlib.sha256(data).hexdigest() == expected for data in (lf, lf.replace(b"\n", b"\r\n"))):
            return path
    raise ValueError(f"기준 실행의 해시와 일치하지 않습니다: {path}")


def baseline_sources():
    start = [
        (PAPER / "replication/S1_bigkinds_manifest.csv", "입력 파일별 기사 행 수와 수집 기간"),
        (PROCESSED / "corpus/corpus_monthly_counts.csv", "전처리를 거친 기사 수의 월별 집계"),
    ]
    analysis = [(PAPER / "replication/S5_domain_dictionary.csv", "토픽을 경제 이슈로 분류한 사전")]
    for folder, stem, description in SUPPLEMENTS:
        files = sorted((PROCESSED / folder).glob(stem + ".csv"))
        if not files:
            raise FileNotFoundError(PROCESSED / folder / (stem + ".csv"))
        analysis.extend((path, description) for path in files)
    return start, analysis


def export_results(artifact_dir, audit_path, destination, *, paper_run=False, study=None, metrics=None):
    audit = read_json(audit_path)
    run_id = audit["run_id"]
    if read_json(artifact_dir / "core_meta.json")["run_id"] != run_id:
        raise ValueError("학습 자료와 분석 결과의 실행 ID가 다릅니다.")
    if paper_run and run_id != BASELINE:
        raise ValueError("논문 최종표와 별도 검증표는 기준 실행에서만 사용할 수 있습니다.")

    learning, supplemental = baseline_sources() if paper_run else ([], [])
    for name, description in (
        ("core_meta.json", "전처리 단계별 건수와 학습 설정"),
        ("fit_sample_ids.csv", "학습에 사용한 기사 표본과 추출 순서"),
        ("vocab_idf.csv", "학습 어휘, 문서 빈도, IDF 가중치"),
        ("nmf_H.npy", "어휘별 토픽 가중치. 어휘 인덱스는 vocab_idf 참고"),
    ):
        source = checked_path(artifact_dir / name, audit["artifacts"][name], allow_text_eol=paper_run)
        learning.append((source, description))

    topic = checked_path(artifact_dir / "monthly_topic_share.csv", audit["artifacts"]["monthly_topic_share.csv"],
                         allow_text_eol=paper_run)
    analysis = [(topic, "모델이 찾은 개별 토픽의 월별 점수 비중")]
    for key, description in (
        ("mapping", "토픽과 경제 이슈의 대응"),
        ("regime", "경제 이슈의 월별 비중과 표준화 점수"),
        ("forecast", "예측 월별 실제값, 모형별 예측값 및 오차"),
    ):
        item = audit["deliverables"][key]
        source = checked_path(audit_path.parent / item["path"], item["sha256"], allow_text_eol=paper_run)
        analysis.append((source, description))
    analysis.append((audit_path, "분석 설정, 입력과 산출물 식별 정보, 검산 결과"))
    analysis.extend(supplemental)
    extra = []
    if study is not None:
        extra.append(("예측 입력 패널", list(study.columns),
                      study.astype(object).where(study.notna(), None).itertuples(index=False, name=None),
                      "모형 예측에 사용한 월별 결합 자료"))

    destination.mkdir(parents=True, exist_ok=True)
    outputs = [destination / name for name in (LEARNING, ANALYSIS, FINAL)]
    with TemporaryDirectory(prefix=".v4-excel-", dir=destination) as directory:
        staging = Path(directory)
        write_workbook(staging / LEARNING, run_id, learning)
        write_workbook(staging / ANALYSIS, run_id, analysis, extra)
        if paper_run:
            shutil.copyfile(PAPER / "results/논문_v4_최종_결과.xlsx", staging / FINAL)
        else:
            summary = [
                ("예측 평가", ["항목", "값"], json_rows(metrics or {}), "이번 실행의 모형별 예측 평가"),
                ("실행 검산", ["항목", "값"], json_rows(audit["checks"]), "이번 실행의 검산 항목과 판정"),
            ]
            write_workbook(staging / FINAL, run_id, [], summary)
        for output in outputs:
            (staging / output.name).replace(output)
    return outputs


def main():
    parser = argparse.ArgumentParser(description="저장된 논문 v4 기준 결과를 엑셀 3개로 저장합니다.")
    parser.add_argument("--output-dir", type=Path, default=PAPER / "results" / "excel_export" / BASELINE)
    args = parser.parse_args()
    outputs = export_results(
        PROCESSED / "phase5_6_artifacts" / BASELINE,
        PROCESSED / "reactions" / "phase5_6_pipeline_audit.json",
        args.output_dir,
        paper_run=True,
    )
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
