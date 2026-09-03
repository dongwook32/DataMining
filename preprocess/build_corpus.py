"""빅카인즈 엑셀 → 통합 뉴스 코퍼스.

  python -m preprocess.build_corpus --audit   # 투입 상태 점검만 (파일 안 씀)
  python -m preprocess.build_corpus           # 코퍼스 생성

산출:
  data/processed/corpus/news_corpus.parquet       기사 단위 (분석 창 안, 중복 제거 후)
  data/processed/corpus/corpus_monthly_counts.csv 월별 건수 점검용

중복 제거는 URL을 1순위 키로 쓰고, URL이 비었으면 `일자|언론사|제목`으로 대체한다.
`뉴스 식별자`는 쓰지 않는다 — 엑셀에서 float으로 읽히면 정밀도가 날아가 같은 기사가
서로 다른 값이 되기 때문이다(2022-11 중복 구간에서 5,221건 중 89건만 일치했다).
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from config import load_config
from preprocess.bigkinds_schema import (
    COLUMN_MAP,
    CONTENT_TRUNCATION_LEN,
    EXCLUDE_TOKENS,
    EXPORT_ROW_CAP,
    USECOLS,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "bigkinds"
OUT_DIR = ROOT / "data" / "processed" / "corpus"

# 빅카인즈 엑셀에는 기본 스타일이 없어 openpyxl이 매 파일 경고를 낸다.
warnings.filterwarnings("ignore", message="Workbook contains no default style")


def iter_files() -> list[Path]:
    return sorted(RAW_DIR.rglob("*.xlsx"), key=lambda p: (p.parent.name, p.name))


def read_raw(path: Path) -> pd.DataFrame:
    """엑셀 한 개를 정규화된 컬럼명으로 읽는다. 전 컬럼 문자열."""
    df = pd.read_excel(path, usecols=USECOLS, dtype=str)
    return df.rename(columns=COLUMN_MAP)


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], format="%Y%m%d", errors="coerce")
    for col in ("source", "title", "url", "keywords", "features", "content"):
        out[col] = out[col].fillna("").str.strip()
    out["exclude_flag"] = out["exclude_flag"].fillna("")
    out["month"] = out["date"].dt.to_period("M").astype(str)
    return out


def dedup_key(df: pd.DataFrame) -> pd.Series:
    url = df["url"].str.strip().str.lower()
    fallback = df["date"].dt.strftime("%Y%m%d") + "|" + df["source"] + "|" + df["title"]
    return url.where(url.str.startswith("http"), fallback)


def is_excluded(flag: pd.Series) -> pd.Series:
    """빅카인즈가 '예외'/'중복'으로 표시한 행."""
    return flag.apply(lambda s: any(tok in s for tok in EXCLUDE_TOKENS))


def audit() -> None:
    files = iter_files()
    print(f"{len(files)}개 파일\n")
    header = f"{'file':<44}{'rows':>7}{'cap':>5}{'사':>4}{'경제%':>7}{'제외%':>7}{'절삭%':>7}  기간"
    print(header)
    print("-" * len(header))

    total = 0
    all_sources: set[str] = set()
    months: dict[str, int] = {}
    for path in files:
        df = normalize(read_raw(path))
        total += len(df)
        all_sources.update(df["source"].unique())
        for m, n in df["month"].value_counts().items():
            months[m] = months.get(m, 0) + int(n)
        econ = df["category1"].fillna("").str.startswith("경제").mean()
        excl = is_excluded(df["exclude_flag"]).mean()
        trunc = (df["content"].str.len() >= CONTENT_TRUNCATION_LEN).mean()
        cap = "HIT" if len(df) == EXPORT_ROW_CAP else ""
        span = f"{df['date'].min():%Y-%m-%d}~{df['date'].max():%Y-%m-%d}"
        print(
            f"{path.parent.name + '/' + path.name:<44}{len(df):>7}{cap:>5}"
            f"{df['source'].nunique():>4}{econ:>7.1%}{excl:>7.1%}{trunc:>7.1%}  {span}"
        )

    print(f"\n합계 {total:,}건 · 언론사 {len(all_sources)}개: {sorted(all_sources)}")
    s = pd.Series(months).sort_index()
    print(f"월 커버리지 {s.index.min()}~{s.index.max()} ({len(s)}개월)")
    expected = pd.period_range(s.index.min(), s.index.max(), freq="M").astype(str)
    missing = sorted(set(expected) - set(s.index))
    print(f"빠진 달: {missing or '없음'}")
    print(f"월 건수 min/median/max: {s.min():,} / {int(s.median()):,} / {s.max():,}")


def build() -> None:
    cfg = load_config()
    start = pd.Timestamp(cfg["project"]["study_period_start"])
    end = pd.Timestamp(cfg["project"]["study_period_end"])
    print(f"분석 창 {start:%Y-%m-%d} ~ {end:%Y-%m-%d}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "news_corpus.parquet"

    keep_cols = [
        "article_id",
        "date",
        "month",
        "source",
        "title",
        "category1",
        "category2",
        "keywords",
        "features",
        "content",
        "url",
    ]

    seen: set[str] = set()
    writer: pq.ParquetWriter | None = None
    stats = {"read": 0, "out_of_range": 0, "excluded": 0, "duplicate": 0, "no_text": 0, "kept": 0}

    try:
        for path in iter_files():
            df = normalize(read_raw(path))
            stats["read"] += len(df)

            in_range = df["date"].between(start, end)
            stats["out_of_range"] += int((~in_range).sum())
            df = df[in_range]

            excluded = is_excluded(df["exclude_flag"])
            stats["excluded"] += int(excluded.sum())
            df = df[~excluded]

            # 토픽모델링 입력이 되는 키워드가 비면 문서로 쓸 수 없다.
            empty = df["keywords"].str.len() == 0
            stats["no_text"] += int(empty.sum())
            df = df[~empty]

            keys = dedup_key(df)
            fresh = ~keys.duplicated() & ~keys.isin(seen)
            stats["duplicate"] += int((~fresh).sum())
            df = df[fresh]
            seen.update(keys[fresh])

            stats["kept"] += len(df)
            table = pa.Table.from_pandas(df[keep_cols], preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(out_path, table.schema, compression="zstd")
            writer.write_table(table)
            print(f"  {path.parent.name}/{path.name}  +{len(df):,}  (누적 {stats['kept']:,})", flush=True)
    finally:
        if writer is not None:
            writer.close()

    print("\n=== 투입 요약 ===")
    print(f"원본            {stats['read']:>9,}")
    print(f"- 분석창 밖     {stats['out_of_range']:>9,}")
    print(f"- 빅카인즈 제외 {stats['excluded']:>9,}  (예외/중복 플래그)")
    print(f"- 키워드 없음   {stats['no_text']:>9,}")
    print(f"- 중복          {stats['duplicate']:>9,}")
    print(f"= 코퍼스        {stats['kept']:>9,}")

    corpus = pd.read_parquet(out_path, columns=["month", "source", "date"])
    counts = (
        corpus.groupby("month")
        .agg(n=("date", "size"), sources=("source", "nunique"))
        .reset_index()
    )
    counts.to_csv(OUT_DIR / "corpus_monthly_counts.csv", index=False, encoding="utf-8-sig")
    print(f"\nparquet → {out_path}")
    print(f"월별 건수 → {OUT_DIR / 'corpus_monthly_counts.csv'}")
    print(f"월 {len(counts)}개, 건수 min/median/max "
          f"{counts['n'].min():,} / {int(counts['n'].median()):,} / {counts['n'].max():,}")

    thin = counts[counts["n"] < cfg["analysis"]["min_articles_per_month"]]
    if not thin.empty:
        print(f"경고: 최소 건수 미달 월 {list(thin['month'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="빅카인즈 엑셀 → 통합 코퍼스")
    parser.add_argument("--audit", action="store_true", help="투입 상태만 점검하고 종료")
    args = parser.parse_args()
    audit() if args.audit else build()


if __name__ == "__main__":
    main()
