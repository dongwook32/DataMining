"""Read BigKinds exports, verify their category fields, and emit file-level metadata."""

import csv
import html
import re
from collections import Counter
from datetime import date
from pathlib import Path
from zipfile import ZipFile

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CELL = re.compile(
    rb'<c r="([ABFGH])\d+"([^>]*)>'
    rb'(?:<v>([^<]*)</v>|<is><t(?:\s[^>]*)?>([^<]*)</t></is>)</c>'
)
SHARED = re.compile(rb"<si\b[^>]*>(.*?)</si>", re.S)
TEXT = re.compile(rb"<t(?:\s[^>]*)?>(.*?)</t>", re.S)


def decode(value):
    return html.unescape(value.decode("utf-8"))


def records(workbook):
    with ZipFile(workbook) as archive:
        strings = [
            b"".join(TEXT.findall(item[1]))
            for item in SHARED.finditer(archive.read("xl/sharedStrings.xml"))
        ]
        sheet = archive.read("xl/worksheets/sheet1.xml")
    row = {}
    count = 0
    for field, attrs, value, inline in CELL.findall(sheet):
        if field == b"A":
            if row and row[b"A"] != "뉴스 식별자":
                yield row
                count += 1
            row = {}
        row[field] = decode(strings[int(value)] if b't="s"' in attrs else value or inline or b"")
    if row:
        yield row
        count += 1
    if count != sheet.count(b"<row ") - 1:
        raise ValueError(f"Worksheet row count mismatch: {workbook.name}")


def main():
    corpus = pq.read_table(
        ROOT / "data/processed/corpus/news_corpus.parquet",
        columns=["article_id", "category1", "category2"],
    )
    expected = {
        row["article_id"]: (row["category1"] or "", row["category2"] or "")
        for row in corpus.to_pylist()
    }
    matched = {}
    manifest = []
    for path in sorted((ROOT / "data/raw/bigkinds").rglob("*.xlsx")):
        counts = Counter()
        start = date.max
        end = date.min
        for row in records(path):
            day = date.fromisoformat(row[b"B"])
            start, end = min(start, day), max(end, day)
            categories = tuple(row.get(key, "") for key in (b"F", b"G", b"H"))
            roots = [item.strip().split(">", 1)[0] for item in categories]
            economic = "경제" in roots
            mixed = economic and any(root not in ("경제", "") for root in roots)
            counts["rows"] += 1
            counts["economic"] += economic
            counts["mixed"] += mixed
            counts["economic_only_in_category3"] += economic and "경제" not in roots[:2]
            counts["no_economic"] += not economic
            article_id = row[b"A"]
            if expected.get(article_id) == categories[:2]:
                previous = matched.setdefault(article_id, tuple(roots))
                if previous != tuple(roots):
                    raise ValueError("Conflicting classification for a matched article")
        manifest.append({
            "file": path.relative_to(ROOT).as_posix(),
            "actual_start": start.isoformat(),
            "actual_end": end.isoformat(),
            **{key: counts[key] for key in (
                "rows", "economic", "mixed", "economic_only_in_category3", "no_economic"
            )},
        })
    total = sum(row["rows"] for row in manifest)
    no_economic = sum(row["no_economic"] for row in manifest)
    final_mixed = sum("경제" in row and any(root not in ("", "경제") for root in row)
                      for row in matched.values())
    final_category3 = sum(row[2] == "경제" and "경제" not in row[:2]
                          for row in matched.values())
    actual = (len(manifest), total, no_economic, len(matched), final_mixed, final_category3)
    if actual != (61, 998020, 0, 931709, 390130, 41174) or any(
        "경제" not in row for row in matched.values()
    ):
        raise ValueError(f"S1 reference totals differ: {actual}")
    with (HERE / "S1_bigkinds_manifest.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)
    print(f"S1 PASS {actual}")


if __name__ == "__main__":
    main()
