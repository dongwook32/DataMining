"""ECOS 월별 경제지표 수집 → data/raw/ecos/ecos_monthly.csv

실행:
  python -m api.collect_ecos
  python -m api.collect_ecos --start 2016-01 --end 2026-07
  python -m api.collect_ecos --indicators CCSI KOSPI
  python -m api.collect_ecos --list-items 511Y002   # 항목코드 확인용

산출:
  data/raw/ecos/ecos_monthly.csv  (date + 지표 컬럼, 병합·회귀용)
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from api.ecos_client import EcosClient
from api.ecos_indicators import BY_NAME, INDICATORS, Indicator
from config import load_config

KST = ZoneInfo("Asia/Seoul")

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "ecos"


def to_yyyymm(value: str) -> str:
    """'2016-01-01' / '2016-01' / '201601' → '201601'."""
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if len(digits) < 6:
        raise ValueError(f"시점 형식을 알 수 없습니다: {value!r}")
    return digits[:6]


def fetch_indicator(client: EcosClient, ind: Indicator, start: str, end: str) -> pd.DataFrame:
    rows = client.statistic_search(
        ind.stat_code, cycle=ind.cycle, start=start, end=end, item_codes=ind.item_codes
    )
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    if ind.expect_item_name and "ITEM_NAME1" in df.columns:
        df = df[df["ITEM_NAME1"] == ind.expect_item_name]

    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["TIME"], format="%Y%m").dt.strftime("%Y-%m-01"),
            "indicator": ind.name,
            "value": pd.to_numeric(df["DATA_VALUE"], errors="coerce"),
        }
    )
    out = out.dropna(subset=["value"]).drop_duplicates(subset=["date"]).sort_values("date")
    return out.reset_index(drop=True)


def main() -> int:
    cfg = load_config()
    period = cfg.get("project", {})
    default_start = period.get("data_buffer_start") or period.get("study_period_start") or "2016-01-01"

    parser = argparse.ArgumentParser(description="ECOS 월별 지표 수집")
    parser.add_argument("--start", default=default_start, help="시작 (YYYY-MM 또는 YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="종료 (기본: 지난달)")
    parser.add_argument(
        "--indicators",
        nargs="*",
        default=None,
        help=f"수집할 지표. 기본 전체: {', '.join(BY_NAME)}",
    )
    parser.add_argument("--list-items", metavar="STAT_CODE", help="통계표의 항목코드 출력 후 종료")
    parser.add_argument(
        "--force",
        action="store_true",
        help="지표 일부만 받을 때도 ecos_monthly.csv를 덮어씀",
    )
    args = parser.parse_args()

    client = EcosClient()

    if args.list_items:
        for row in client.item_list(args.list_items):
            print(
                row.get("GRP_CODE"),
                row.get("ITEM_CODE"),
                "|",
                row.get("ITEM_NAME"),
                "|",
                row.get("CYCLE"),
                row.get("START_TIME"),
                "~",
                row.get("END_TIME"),
            )
        return 0

    start = to_yyyymm(args.start)
    if args.end:
        end = to_yyyymm(args.end)
    else:
        today = date.today()
        end = f"{today.year:04d}{today.month:02d}" if today.month > 1 else f"{today.year - 1:04d}12"

    targets = INDICATORS
    if args.indicators:
        unknown = [n for n in args.indicators if n not in BY_NAME]
        if unknown:
            print(f"알 수 없는 지표: {', '.join(unknown)}", file=sys.stderr)
            return 1
        targets = [BY_NAME[n] for n in args.indicators]

    frames: list[pd.DataFrame] = []
    failed: list[str] = []
    for ind in targets:
        print(f"[{ind.name}] {ind.stat_code} {ind.item_codes} {start}~{end}", flush=True)
        try:
            df = fetch_indicator(client, ind, start, end)
        except Exception as e:  # 한 지표 실패가 나머지를 막지 않게 한다
            print(f"  FAIL: {e}", file=sys.stderr, flush=True)
            failed.append(ind.name)
            continue
        if df.empty:
            print("  (데이터 없음)", flush=True)
            failed.append(ind.name)
            continue
        print(f"  {len(df)}개월  {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}", flush=True)
        frames.append(df)

    if not frames:
        print("수집된 지표가 없습니다.", file=sys.stderr)
        return 1

    # 일부 지표만 받은 결과가 전체 파일을 덮어쓰지 않게 한다
    partial = len(targets) < len(INDICATORS) and not args.force
    out_name = "ecos_monthly_partial.csv" if partial else "ecos_monthly.csv"
    if partial:
        print("\n일부 지표만 수집 → 전체 파일 대신 *_partial.csv 로 저장 (덮어쓰려면 --force)")

    long_df = pd.concat(frames, ignore_index=True).sort_values(["indicator", "date"])
    collected_at = datetime.now(KST).isoformat(timespec="seconds")

    out = long_df.pivot(index="date", columns="indicator", values="value").reset_index()
    out.columns.name = None
    out["collected_at"] = collected_at
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / out_name
    out.to_csv(out_path, index=False, encoding="utf-8-sig")

    n_ind = len(out.columns) - 2  # date, collected_at 제외
    print(f"\n→ {out_path} ({len(out)} rows × {n_ind} indicators)")
    print(f"collected_at = {collected_at}")

    missing = out.isna().sum()
    gaps = {c: int(n) for c, n in missing.items() if c not in ("date", "collected_at") and n}
    if gaps:
        print(f"결측 있는 지표: {gaps}")
    if failed:
        print(f"실패/미수집: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
