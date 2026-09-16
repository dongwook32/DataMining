"""data/raw/bigkinds 아래 빅카인즈 엑셀 → 같은 이름의 JSON.

  python -m preprocess.bigkinds_to_json

원본 `.xlsx`는 남기고 옆에 `.json`을 함께 둔다. 형식은 `csv_to_json`과 같은
레코드 배열이다.

컬럼은 19개 전부, 원본 이름 그대로 옮긴다. 분석용 정규화(`bigkinds_schema.COLUMN_MAP`)는
적용하지 않는다. 이 산출물은 원본의 형식만 바꾼 사본이고, 컬럼 선별·개명은
`build_corpus.py`가 할 일이다.

전 컬럼을 `dtype=str`로 읽는다. `bigkinds_schema` 모듈 주석대로 `뉴스 식별자`
(`02100311.20210131095312001`)를 dtype 지정 없이 읽으면 pandas가 float으로 해석해
정밀도가 날아간다. 빈 셀은 `null`로 간다.
"""

from __future__ import annotations

import json
import warnings

import pandas as pd

from config import project_root
from preprocess.csv_to_json import same_value, to_records

ROOT = project_root()
BIGKINDS_DIR = ROOT / "data" / "raw" / "bigkinds"


def convert(xlsx_path) -> dict:
    # 빅카인즈 내보내기 파일에는 기본 스타일이 없어 openpyxl이 매번 경고를 낸다.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Workbook contains no default style")
        df = pd.read_excel(xlsx_path, dtype=str)

    records = to_records(df)

    json_path = xlsx_path.with_suffix(".json")
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)

    # 검증: 다시 읽어 행 수·열 이름·값을 대조한다.
    with json_path.open(encoding="utf-8") as f:
        reloaded = json.load(f)

    problems = []
    if len(reloaded) != len(df):
        problems.append(f"행 수 {len(reloaded)} != {len(df)}")
    if reloaded and list(reloaded[0].keys()) != list(df.columns):
        problems.append("열 이름 불일치")
    mismatches = sum(
        1
        for src, dst in zip(records, reloaded)
        for k in src
        if not same_value(src[k], dst.get(k))
    )
    if mismatches:
        problems.append(f"값 불일치 {mismatches}개")

    return {
        "xlsx": xlsx_path,
        "json": json_path,
        "rows": len(df),
        "cols": len(df.columns),
        "xlsx_mb": xlsx_path.stat().st_size / 1024**2,
        "json_mb": json_path.stat().st_size / 1024**2,
        "problems": problems,
    }


def main() -> None:
    paths = sorted(BIGKINDS_DIR.rglob("*.xlsx"))
    if not paths:
        raise SystemExit(f"{BIGKINDS_DIR} 아래에 엑셀이 없다")

    failed = 0
    total_rows = 0
    total_xlsx = 0.0
    total_json = 0.0
    for i, path in enumerate(paths, 1):
        r = convert(path)
        status = "OK" if not r["problems"] else "; ".join(r["problems"])
        failed += bool(r["problems"])
        total_rows += r["rows"]
        total_xlsx += r["xlsx_mb"]
        total_json += r["json_mb"]
        print(
            f"[{i}/{len(paths)}] {r['xlsx'].relative_to(BIGKINDS_DIR)} | "
            f"{r['rows']}행 {r['cols']}열 | "
            f"{r['xlsx_mb']:.3f}MB -> {r['json_mb']:.3f}MB | {status}",
            flush=True,
        )

    print(
        f"\n{len(paths)}개 중 {len(paths) - failed}개 검증 통과 | "
        f"총 {total_rows}행 | {total_xlsx:.1f}MB -> {total_json:.1f}MB"
    )
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
