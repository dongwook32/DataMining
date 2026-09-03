"""네이버 데이터랩 검색어 트렌드 수집 (앵커 정규화 방식).

  python -m api.collect_datalab --calibrate     # 앵커 후보 비교
  python -m api.collect_datalab                 # 월간 + 일간 수집
  python -m api.collect_datalab --unit month

산출:
  data/raw/datalab/datalab_regime_{monthly,daily}.csv   대분류 7개
  data/raw/datalab/datalab_sub_{monthly,daily}.csv      세부 28개
  data/raw/datalab/datalab_keywords.md                  검색어 세트 기록

## 왜 요청마다 그룹을 하나만 보내는가

데이터랩 지수는 요청에 포함된 그룹·기간 전체에서 검색량이 가장 큰 지점을 100으로 두는
상대값이다. 검색량 차이가 큰 그룹을 한 요청에 섞으면 작은 그룹이 소수점 아래로 눌려
유효숫자를 잃는다. 그룹을 하나씩 보내면 그 그룹의 피크가 100이 되어 해상도를 다 쓴다.

대신 요청이 달라지면 100의 기준도 달라져 서로 비교할 수 없다. 그래서 모든 요청에
공통 앵커 그룹을 하나 더 넣는다. 같은 요청 안의 두 그룹 비율은 실제 검색량 비율이므로
`score_rel = score / anchor_score`가 요청을 가로질러 비교 가능한 값이 된다.

## 왜 종료일을 config에서 읽는가

지수가 구간 상대값이라 종료일이 하루만 달라져도 전 구간 숫자가 바뀐다.
직전 버전은 종료일을 `date.today()`로 잡아 재실행할 때마다 결과가 달라졌다.
이제 `config.yaml`의 `study_period_end`로 고정한다.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import requests

KST = ZoneInfo("Asia/Seoul")

from api.datalab_keyword_sets import (
    ANCHOR_CANDIDATES,
    ANCHOR_GROUP,
    KEYWORD_SETS,
    regime_groups,
    sub_groups,
)
from api.naver_client import NaverClient
from config import load_config

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "datalab"

REQUEST_SLEEP_SEC = 0.4


def fetch(
    client: NaverClient,
    *,
    start: str,
    end: str,
    time_unit: str,
    groups: list[dict[str, Any]],
    retries: int = 3,
) -> dict[str, Any]:
    last: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return client.datalab_search(
                start_date=start, end_date=end, time_unit=time_unit, keyword_groups=groups
            )
        except requests.HTTPError as e:
            last = e
            print(f"    retry {attempt}/{retries}: {e}", flush=True)
            time.sleep(1.5 * attempt)
    assert last is not None
    raise last


def payload_to_series(payload: dict[str, Any]) -> dict[str, pd.Series]:
    """응답을 그룹명 → (날짜 인덱스, ratio) 시리즈로."""
    out: dict[str, pd.Series] = {}
    for result in payload.get("results") or []:
        points = result.get("data") or []
        s = pd.Series(
            [p.get("ratio") for p in points],
            index=[p.get("period") for p in points],
            dtype="float64",
        )
        out[result.get("title") or ""] = s
    return out


def collect_level(
    client: NaverClient,
    *,
    groups: list[tuple[str, dict[str, Any]]],
    time_unit: str,
    start: str,
    end: str,
) -> pd.DataFrame:
    """(대분류, 그룹) 목록을 그룹당 1요청 + 앵커로 수집."""
    frames: list[pd.DataFrame] = []
    anchor_name = ANCHOR_GROUP["groupName"]

    for regime, group in groups:
        name = group["groupName"]
        payload = fetch(
            client,
            start=start,
            end=end,
            time_unit=time_unit,
            groups=[group, ANCHOR_GROUP],
        )
        series = payload_to_series(payload)
        target, anchor = series.get(name), series.get(anchor_name)
        if target is None or anchor is None:
            raise RuntimeError(f"{name}: 응답에 그룹이 없습니다 ({list(series)})")

        df = pd.DataFrame({"score": target, "anchor_score": anchor})
        # 데이터랩은 검색량이 공개 임계 미만인 날짜를 응답에서 통째로 뺀다.
        # 결측이 아니라 "거의 0"이라는 뜻이라 0으로 채운다. 앵커는 항상 값이 있어 기준이 된다.
        missing = int(df["score"].isna().sum())
        df["score"] = df["score"].fillna(0.0)
        df["score_rel"] = df["score"] / df["anchor_score"].where(df["anchor_score"] > 0)
        df = df.reset_index(names="date")
        df.insert(1, "regime", regime)
        df.insert(2, "group", name)
        df.insert(3, "keywords", "|".join(group["keywords"]))
        frames.append(df)
        note = f", 임계미달 {missing}일 0처리" if missing else ""
        print(f"  {regime}/{name}: {len(df)}행 "
              f"(peak {df['score'].max():.1f}, anchor 대비 중앙값 {df['score_rel'].median():.2f}{note})",
              flush=True)
        time.sleep(REQUEST_SLEEP_SEC)

    out = pd.concat(frames, ignore_index=True)
    out["period_start"] = start
    out["period_end"] = end
    out["time_unit"] = time_unit
    out["collected_at"] = datetime.now(KST).isoformat(timespec="seconds")
    return out


def calibrate(client: NaverClient, start: str, end: str) -> None:
    """앵커 후보를 서로 비교한다. 변동이 작고 추세가 평평한 쪽이 좋다.

    후보가 5개를 넘으면 요청을 나눠야 하는데, 요청이 다르면 100의 기준도 달라진다.
    그래서 첫 후보를 모든 배치에 넣어 기준으로 삼고 그것으로 나눠 이어 붙인다.
    """
    names = list(ANCHOR_CANDIDATES)
    ref = names[0]
    rest = names[1:]
    batches = [rest[i : i + 4] for i in range(0, len(rest), 4)] or [[]]
    print(f"앵커 후보 {len(names)}개 · 기준 '{ref}' · {len(batches)}개 요청 ({start} ~ {end})\n")

    collected: dict[str, pd.Series] = {}
    for batch in batches:
        groups = [
            {"groupName": n, "keywords": ANCHOR_CANDIDATES[n]} for n in [ref, *batch]
        ]
        series = payload_to_series(
            fetch(client, start=start, end=end, time_unit="month", groups=groups)
        )
        base = series[ref]
        for name, s in series.items():
            if name == ref and ref in collected:
                continue
            # 기준 대비 비율로 바꿔 배치가 달라도 같은 축에 놓는다.
            collected[name] = s / base.replace(0, pd.NA)
        time.sleep(REQUEST_SLEEP_SEC)

    rows = []
    for name, s in collected.items():
        rows.append({
            "후보": name,
            f"{ref} 대비 중앙값": round(s.median(), 3),
            "변동계수": round(s.std() / s.mean(), 3),
            "추세(후반24개월/전반24개월)": round(s.tail(24).mean() / s.head(24).mean(), 2),
        })
    table = pd.DataFrame(rows).sort_values("변동계수")
    print(table.to_string(index=False))
    print(f"\n('{ref}' 자신은 정의상 변동계수 0)")
    print("변동계수가 작고 추세가 1에 가까울수록 앵커로 안정적입니다.")
    print("고른 뒤 api/datalab_keyword_sets.py의 ANCHOR_GROUP을 바꾸세요.")


def write_keyword_doc(path: Path, start: str, end: str) -> None:
    lines = [
        "# 데이터랩 검색어 세트",
        "",
        f"- 조회 구간 **{start} ~ {end}** 고정 (config.yaml)",
        f"- 앵커 그룹 `{ANCHOR_GROUP['groupName']}` = {', '.join(ANCHOR_GROUP['keywords'])}",
        "- 요청 1건 = 대상 그룹 1개 + 앵커 1개. `score_rel = score / anchor_score`로 비교한다.",
        "- 분류 근거는 `api/datalab_keyword_sets.py` 상단 주석 참고 (빅카인즈 코퍼스 토픽 마이닝).",
        "",
    ]
    for regime, subs in KEYWORD_SETS.items():
        lines.append(f"## {regime}")
        lines.append("")
        for sub in subs:
            lines.append(f"- **{sub['groupName']}**: {', '.join(sub['keywords'])}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="데이터랩 검색어 트렌드 수집")
    parser.add_argument("--unit", choices=("month", "date", "both"), default="both")
    parser.add_argument("--calibrate", action="store_true", help="앵커 후보 비교만 하고 종료")
    args = parser.parse_args()

    cfg = load_config()
    start = cfg["project"]["data_buffer_start"]
    end = cfg["project"]["study_period_end"]
    client = NaverClient()

    if args.calibrate:
        calibrate(client, start, end)
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_keyword_doc(OUT_DIR / "datalab_keywords.md", start, end)
    print(f"검색어 문서 → {OUT_DIR / 'datalab_keywords.md'}\n")

    units = ["month", "date"] if args.unit == "both" else [args.unit]
    levels = {
        "regime": [(g["groupName"], g) for g in regime_groups()],
        "sub": sub_groups(),
    }

    for unit in units:
        suffix = "monthly" if unit == "month" else "daily"
        for level, groups in levels.items():
            print(f"[{unit}] {level} — {len(groups)}개 그룹")
            df = collect_level(client, groups=groups, time_unit=unit, start=start, end=end)
            path = OUT_DIR / f"datalab_{level}_{suffix}.csv"
            df.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"  → {path} ({len(df)}행)\n")


if __name__ == "__main__":
    main()
