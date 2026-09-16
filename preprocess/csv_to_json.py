"""data/raw 아래 CSV → 같은 이름의 JSON.

  python -m preprocess.csv_to_json

원본 CSV는 남기고 옆에 `.json`을 함께 둔다. 형식은 레코드 배열
(`[{"col": val, ...}, ...]`)이다.

부동소수점은 양쪽 끝에서 손실이 난다. 읽을 때는 `read_csv`의 기본 파서가 정확
반올림을 하지 않아 `score_rel`에서 1 ULP씩 어긋나므로 `float_precision="round_trip"`을
쓴다. 쓸 때는 `DataFrame.to_json`의 기본 `double_precision=10`이 16자리 값을
잘라내므로 `json.dumps`로 파이썬 float repr을 그대로 쓴다. 결측은 `null`로 간다.

변환 후 JSON을 다시 읽어 원본 CSV와 행 수·열 이름·값을 대조한다.
"""

from __future__ import annotations

import json
import math

import pandas as pd

from config import project_root

ROOT = project_root()
RAW_DIR = ROOT / "data" / "raw"


def to_records(df: pd.DataFrame) -> list[dict]:
    """numpy 스칼라와 NaN을 JSON이 아는 파이썬 타입으로 바꾼다."""
    columns = {}
    for col in df.columns:
        s = df[col]
        na = s.isna()
        if pd.api.types.is_bool_dtype(s):
            cast = bool
        elif pd.api.types.is_integer_dtype(s):
            cast = int
        elif pd.api.types.is_float_dtype(s):
            cast = float
        else:
            cast = str
        columns[col] = [
            None if is_na else cast(v) for v, is_na in zip(s, na)
        ]
    names = list(df.columns)
    return [dict(zip(names, row)) for row in zip(*columns.values())]


def same_value(original, restored) -> bool:
    if original is None or restored is None:
        return original is None and restored is None
    if isinstance(original, float) and isinstance(restored, float):
        return original == restored or (math.isnan(original) and math.isnan(restored))
    return original == restored


def convert(csv_path) -> dict:
    df = pd.read_csv(csv_path, float_precision="round_trip")
    records = to_records(df)

    json_path = csv_path.with_suffix(".json")
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)

    # 검증: 다시 읽어 행 수·열 이름·값을 원본과 대조한다.
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
        "csv": csv_path,
        "json": json_path,
        "rows": len(df),
        "cols": len(df.columns),
        "csv_mb": csv_path.stat().st_size / 1024**2,
        "json_mb": json_path.stat().st_size / 1024**2,
        "problems": problems,
    }


def main() -> None:
    paths = sorted(RAW_DIR.rglob("*.csv"))
    if not paths:
        raise SystemExit(f"{RAW_DIR} 아래에 CSV가 없다")

    failed = 0
    for path in paths:
        r = convert(path)
        status = "OK" if not r["problems"] else "; ".join(r["problems"])
        failed += bool(r["problems"])
        print(
            f"{r['csv'].relative_to(ROOT)} -> {r['json'].name} | "
            f"{r['rows']}행 {r['cols']}열 | "
            f"{r['csv_mb']:.3f}MB -> {r['json_mb']:.3f}MB | {status}"
        )

    print(f"\n{len(paths)}개 중 {len(paths) - failed}개 검증 통과")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
