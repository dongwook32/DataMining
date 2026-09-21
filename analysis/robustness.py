"""NMF 국면 반응의 강건성 — 2026 제외 · kospi_ret_std 재확인.

  python -m analysis.robustness

본분석은 67개월 전체다. 2026년 코스피 분산이 앞 구간의 다섯 배라
(`panel_qc.md` 5절) 마지막 7개월이 그룹 평균을 흔들 수 있다.
여기서는 2026-01 이후를 뺀 60개월로 같은 KW·반응표를 다시 만들고,
본분석과 유의성(p<0.05)이 뒤집히는지 기록한다.

`kospi_ret_std` 자체는 `measure_reactions` 본분석에도 이미 들어 있다.
이 모듈은 표본을 자른 뒤의 재추정이다.

산출:
  data/processed/reactions/robustness_no2026_reaction.csv
  data/processed/reactions/robustness_no2026_tests.csv
  data/processed/reactions/robustness_compare.csv
  data/processed/reactions/robustness_qc.md
"""

from __future__ import annotations

import pandas as pd

from analysis.measure_reactions import (
    ALL_DEPS,
    PRIMARY_DEPS,
    group_tests,
    load_joined,
    present_regimes,
    reaction_table,
)
from config import load_config, project_root

ROOT = project_root()
OUT_DIR = ROOT / "data" / "processed" / "reactions"

REACT_PATH = OUT_DIR / "robustness_no2026_reaction.csv"
TESTS_PATH = OUT_DIR / "robustness_no2026_tests.csv"
COMPARE_PATH = OUT_DIR / "robustness_compare.csv"
QC_PATH = OUT_DIR / "robustness_qc.md"

CUT = "2026-01"
ALPHA = 0.05


def exclude_2026(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["month"] < CUT].copy().reset_index(drop=True)


def compare_kw(full: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    """같은 종속변수 KW p가 표본을 잘랐을 때 어떻게 바뀌는지."""
    a = full[full["test"] == "kruskal"].set_index("dep_var")
    b = sub[sub["test"] == "kruskal"].set_index("dep_var")
    rows = []
    for dep in ALL_DEPS:
        if dep not in a.index or dep not in b.index:
            continue
        p_full = float(a.loc[dep, "p_value"])
        p_sub = float(b.loc[dep, "p_value"])
        sig_full = p_full < ALPHA
        sig_sub = p_sub < ALPHA
        rows.append({
            "dep_var": dep,
            "p_full": p_full,
            "p_no2026": p_sub,
            "sig_full": sig_full,
            "sig_no2026": sig_sub,
            "flipped": sig_full != sig_sub,
            "h_full": float(a.loc[dep, "statistic"]),
            "h_no2026": float(b.loc[dep, "statistic"]),
            "n_full": int(a.loc[dep, "n"]),
            "n_no2026": int(b.loc[dep, "n"]),
        })
    return pd.DataFrame(rows)


def write_qc(
    *,
    df_sub: pd.DataFrame,
    regimes: list[str],
    absent: list[str],
    reaction: pd.DataFrame,
    tests: pd.DataFrame,
    compare: pd.DataFrame,
) -> None:
    lines: list[str] = []
    add = lines.append
    add("# 강건성 점검 (2026 제외)")
    add("")
    add(f"생성: `analysis.robustness` · {pd.Timestamp.now():%Y-%m-%d %H:%M}")
    add("")
    add("## 1. 표본")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 제외 | `{CUT}` 이후 |")
    add(f"| 남은 기간 | {df_sub['month'].iloc[0]} ~ {df_sub['month'].iloc[-1]} ({len(df_sub)}개월) |")
    add(f"| 국면 그룹 | {len(regimes)}개 — {', '.join(regimes)} |")
    add(f"| 라벨 0개월 | {', '.join(absent) if absent else '없음'} |")
    add("")
    add("| 국면 | 개월 |")
    add("|------|------|")
    for r in regimes:
        n = int((df_sub["dominant_regime"] == r).sum())
        add(f"| {r} | {n} |")
    add("")

    add("## 2. 2026 제외 반응 (주 종속변수)")
    add("")
    for dep in PRIMARY_DEPS:
        sub = reaction[reaction["dep_var"] == dep]
        add(f"### `{dep}`")
        add("")
        add("| 국면 | n | 평균 | 표준편차 | 중위수 | 전체평균 차 |")
        add("|------|---|------|----------|--------|-------------|")
        for _, r in sub.iterrows():
            add(f"| {r['regime']} | {int(r['n'])} | {r['mean']:+.3f} | {r['sd']:.3f} | "
                f"{r['median']:+.3f} | {r['mean_minus_overall']:+.3f} |")
        add("")

    add("## 3. KW 비교 (전체 vs 2026 제외)")
    add("")
    add(f"유의 기준 p<{ALPHA}. `flipped`는 유의 여부만 뒤집힌 경우다.")
    add("")
    add("| 종속변수 | p 전체 | p 2026제외 | 유의 전체 | 유의 제외 | 뒤집힘 |")
    add("|----------|--------|------------|-----------|-----------|--------|")
    for _, r in compare.iterrows():
        add(f"| `{r['dep_var']}` | {r['p_full']:.4f} | {r['p_no2026']:.4f} | "
            f"{'예' if r['sig_full'] else '아니오'} | "
            f"{'예' if r['sig_no2026'] else '아니오'} | "
            f"{'예' if r['flipped'] else '아니오'} |")
    add("")
    flips = compare[compare["flipped"]]["dep_var"].tolist()
    add("뒤집힌 종속변수: "
        + (", ".join(f"`{d}`" for d in flips) if flips else "없음"))
    add("")

    add("## 4. 읽는 법")
    add("")
    add("- 본분석 라벨은 바꾸지 않는다. 이 표는 같은 NMF 국면을 다른 표본에서 본 것이다.")
    add("- 주 종속변수(코스피·환율·CCSI)의 KW가 전체에서 약하고 2026 제외에서도 약하면")
    add("  반응 차이 주장은 단일 라벨 그룹 비교만으로는 성립하지 않는다.")
    add("- `kospi_ret_std`는 분산 표준화로 2026 충격을 누른 계열이다. 원계열과 같이 본다.")
    add("")
    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def run() -> dict:
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_joined(labels, slugs)
    df_sub = exclude_2026(df)
    regimes = present_regimes(df_sub, labels)
    absent = [r for r in labels if r not in regimes]

    reaction = reaction_table(df_sub, regimes)
    tests = group_tests(df_sub, regimes)

    full_tests = pd.read_csv(OUT_DIR / "regime_tests.csv")
    compare = compare_kw(full_tests, tests)

    reaction.to_csv(REACT_PATH, index=False, encoding="utf-8-sig")
    tests.to_csv(TESTS_PATH, index=False, encoding="utf-8-sig")
    compare.to_csv(COMPARE_PATH, index=False, encoding="utf-8-sig")
    write_qc(
        df_sub=df_sub, regimes=regimes, absent=absent,
        reaction=reaction, tests=tests, compare=compare,
    )

    print(f"2026 제외 {len(df_sub)}개월 · 그룹 {len(regimes)}")
    print("\n=== KW 전체 vs 2026 제외 ===")
    for _, r in compare.iterrows():
        mark = " FLIP" if r["flipped"] else ""
        print(f"  {r['dep_var']:<14} p_full={r['p_full']:.4f}  p_no2026={r['p_no2026']:.4f}{mark}")
    print(f"\n비교표 → {COMPARE_PATH}")
    print(f"QC     → {QC_PATH}")
    return {
        "df_sub": df_sub, "reaction": reaction, "tests": tests, "compare": compare,
    }


def main() -> None:
    run()


if __name__ == "__main__":
    main()
