"""RQ4: 뉴스 국면과 네이버 데이터랩 검색의 정합.

  python -m analysis.rq4_search

검색은 국면을 새로 만들지 않는다. 뉴스에서 이미 정한 7축이 검색 관심도와
같은 달에 같이 움직이는지를 본다. 물가는 뉴스 토픽에서 독립 축이 아니지만
검색 시계열은 있으므로, 보조 설명으로만 남긴다.

측정:
  (1) 같은 국면 뉴스 비중 vs 검색 score_rel / z / share 의 월별 상관
  (2) 그달 뉴스 z-우세 라벨 vs 검색 z 최댓값 라벨의 일치율
  (3) 검색이 한 달 앞서는 경우(시차 +1)의 일치율 — 선행 여부는 기술이 아니라 참고

산출:
  data/processed/reactions/rq4_corr.csv
  data/processed/reactions/rq4_concordance.csv
  data/processed/reactions/rq4_monthly.csv
  data/processed/reactions/rq4_qc.md
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.measure_reactions import load_joined
from config import load_config, project_root

ROOT = project_root()
OUT_DIR = ROOT / "data" / "processed" / "reactions"

CORR_PATH = OUT_DIR / "rq4_corr.csv"
CONC_PATH = OUT_DIR / "rq4_concordance.csv"
MONTHLY_PATH = OUT_DIR / "rq4_monthly.csv"
QC_PATH = OUT_DIR / "rq4_qc.md"


def search_argmax(df: pd.DataFrame, labels: list[str], slugs: dict[str, str], suffix: str) -> pd.Series:
    """각 월에서 검색 지표가 가장 큰 국면. suffix 는 '' | '_z' | '_share'."""
    cols = [f"srch_{slugs[r]}{suffix}" for r in labels]
    arr = df[cols].to_numpy(dtype=float)
    # 물가 뉴스 비중이 0이어도 검색은 값이 있다. argmax 에 그대로 넣는다.
    idx = np.nanargmax(arr, axis=1)
    return pd.Series([labels[i] for i in idx], index=df.index)


def corr_table(df: pd.DataFrame, labels: list[str], slugs: dict[str, str]) -> pd.DataFrame:
    rows = []
    for r in labels:
        slug = slugs[r]
        news = df[f"share_{slug}"]
        news_var = float(news.std(ddof=1))
        for kind, col in (
            ("score_rel", f"srch_{slug}"),
            ("z", f"srch_{slug}_z"),
            ("share", f"srch_{slug}_share"),
        ):
            if news_var < 1e-12:
                pearson = spearman = float("nan")
                note = "뉴스 비중 분산 0 (독립 토픽 없음)"
            else:
                pearson = float(news.corr(df[col], method="pearson"))
                spearman = float(news.corr(df[col], method="spearman"))
                note = ""
            rows.append({
                "regime": r, "search_kind": kind, "n": int(len(df)),
                "pearson": pearson, "spearman": spearman, "note": note,
            })
    return pd.DataFrame(rows)


def concordance_table(df: pd.DataFrame, labels: list[str], slugs: dict[str, str]) -> pd.DataFrame:
    news = df["dominant_regime"]
    rows = []
    for name, series in (
        ("search_z", search_argmax(df, labels, slugs, "_z")),
        ("search_share", search_argmax(df, labels, slugs, "_share")),
        ("search_score", search_argmax(df, labels, slugs, "")),
    ):
        same = (news.to_numpy() == series.to_numpy())
        # 시차: 검색 t-1 vs 뉴스 t
        lead = series.shift(1)
        lead_ok = lead.notna()
        lead_same = (news[lead_ok].to_numpy() == lead[lead_ok].to_numpy())
        rows.append({
            "rule": name,
            "n": int(len(df)),
            "match": int(same.sum()),
            "match_rate": float(same.mean()),
            "lead_n": int(lead_ok.sum()),
            "lead_match": int(lead_same.sum()),
            "lead_rate": float(lead_same.mean()) if lead_ok.any() else float("nan"),
        })
    return pd.DataFrame(rows)


def monthly_table(df: pd.DataFrame, labels: list[str], slugs: dict[str, str]) -> pd.DataFrame:
    out = pd.DataFrame({"month": df["month"], "news_regime": df["dominant_regime"]})
    out["search_z"] = search_argmax(df, labels, slugs, "_z")
    out["search_share"] = search_argmax(df, labels, slugs, "_share")
    out["match_z"] = out["news_regime"] == out["search_z"]
    out["match_share"] = out["news_regime"] == out["search_share"]
    for r in labels:
        slug = slugs[r]
        out[f"share_{slug}"] = df[f"share_{slug}"].to_numpy()
        out[f"srch_{slug}_z"] = df[f"srch_{slug}_z"].to_numpy()
    return out


def write_qc(
    *,
    df: pd.DataFrame,
    corr: pd.DataFrame,
    conc: pd.DataFrame,
    labels: list[str],
) -> None:
    lines: list[str] = []
    add = lines.append
    add("# RQ4 검색 정합 점검")
    add("")
    add(f"생성: `analysis.rq4_search` · {pd.Timestamp.now():%Y-%m-%d %H:%M}")
    add("")
    add("## 1. 표본")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 기간 | {df['month'].iloc[0]} ~ {df['month'].iloc[-1]} ({len(df)}개월) |")
    add(f"| 뉴스 라벨 | `dominant_regime` (z-우세) |")
    add(f"| 검색 | 데이터랩 대분류 7축 (`srch_*`) |")
    add("")
    add("검색 최댓값은 7축 전부(물가 포함)에서 고른다. 뉴스 라벨은 물가 0개월이라")
    add("물가가 검색에서 이겨도 뉴스와는 일치하지 않는다. 이는 설계 차이지 오류가 아니다.")
    add("")

    add("## 2. 같은 국면 뉴스 비중 ↔ 검색 상관")
    add("")
    add("| 국면 | 검색 지표 | Pearson | Spearman | 비고 |")
    add("|------|-----------|---------|----------|------|")
    for _, r in corr.iterrows():
        p = "—" if pd.isna(r["pearson"]) else f"{r['pearson']:+.3f}"
        s = "—" if pd.isna(r["spearman"]) else f"{r['spearman']:+.3f}"
        add(f"| {r['regime']} | {r['search_kind']} | {p} | {s} | {r['note']} |")
    add("")

    add("## 3. 라벨 일치율")
    add("")
    add("| 규칙 | n | 일치 | 일치율 | 검색 선행 n | 선행 일치율 |")
    add("|------|---|------|--------|-------------|-------------|")
    for _, r in conc.iterrows():
        lead = "—" if pd.isna(r["lead_rate"]) else f"{r['lead_rate']:.3f}"
        add(f"| {r['rule']} | {int(r['n'])} | {int(r['match'])} | {r['match_rate']:.3f} | "
            f"{int(r['lead_n'])} | {lead} |")
    add("")
    chance = 1.0 / len(labels)
    add(f"7국면 균등 무작위 일치율은 {chance:.3f}다. 이보다 높아야 검색이 뉴스 라벨을 "
        "보조한다고 읽을 여지가 있다. 인과 주장은 하지 않는다.")
    add("")

    add("## 4. 물가")
    add("")
    add("뉴스 `share_prices`는 전 구간 0이다. 검색 물가 축은 2026-03 급등 등 실제 움직임이 있다")
    add("(`panel_qc.md` 6절). RQ4에서 물가는 '뉴스가 못 잡은 관심도'의 보조 신호로만 적는다.")
    add("")
    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def run() -> dict:
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_joined(labels, slugs)
    corr = corr_table(df, labels, slugs)
    conc = concordance_table(df, labels, slugs)
    monthly = monthly_table(df, labels, slugs)

    corr.to_csv(CORR_PATH, index=False, encoding="utf-8-sig")
    conc.to_csv(CONC_PATH, index=False, encoding="utf-8-sig")
    monthly.to_csv(MONTHLY_PATH, index=False, encoding="utf-8-sig")
    write_qc(df=df, corr=corr, conc=conc, labels=labels)

    print("=== RQ4 상관 (뉴스 비중 vs 검색 z) ===")
    sub = corr[corr["search_kind"] == "z"]
    for _, r in sub.iterrows():
        p = "nan" if pd.isna(r["pearson"]) else f"{r['pearson']:+.3f}"
        print(f"  {r['regime']:<8} pearson={p}  {r['note']}")
    print("\n=== 라벨 일치 ===")
    for _, r in conc.iterrows():
        print(f"  {r['rule']:<14} {r['match_rate']:.3f}  (선행 {r['lead_rate']:.3f})")
    print(f"\n상관   → {CORR_PATH}")
    print(f"일치   → {CONC_PATH}")
    print(f"월별   → {MONTHLY_PATH}")
    print(f"QC     → {QC_PATH}")
    return {"df": df, "corr": corr, "conc": conc, "monthly": monthly}


def main() -> None:
    run()


if __name__ == "__main__":
    main()
