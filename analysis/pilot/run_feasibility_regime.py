"""
최소 국면 탐지 파일럿 (연구 계획 Step 1 범위).

실데이터가 없으면 합성 샘플로 파이프라인 골격만 검증한다.
방법: 키워드 룰 기반 국면 프록시 (sklearn LDA 미설치 환경 대응).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "_archive_pilot" / "synthetic"
PROCESSED = ROOT / "data" / "processed" / "_archive_pilot"

REGIME_KEYWORDS = {
    "물가": ["물가", "인플레이션", "원자재", "공공요금", "소비자물가"],
    "금리": ["기준금리", "대출", "이자", "긴축", "금리"],
    "부동산": ["집값", "전세", "청약", "대출규제", "부동산"],
    "대외": ["환율", "연준", "수출", "지정학", "달러"],
    "성장": ["성장률", "실적", "고용", "경기", "GDP"],
}


def ensure_dirs() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)


def load_or_build_news() -> tuple[pd.DataFrame, str]:
    path = RAW / "news.csv"
    if path.exists():
        df = pd.read_csv(path)
        return df, "real"
    # 합성: 6개월 × 월별 10건, 월마다 dominant 국면이 바뀌도록 설계
    rng = np.random.default_rng(42)
    months = pd.period_range("2025-01", periods=6, freq="M")
    regimes_cycle = ["물가", "금리", "부동산", "대외", "성장", "금리"]
    rows = []
    for month, regime in zip(months, regimes_cycle):
        seeds = REGIME_KEYWORDS[regime]
        other = [w for r, kws in REGIME_KEYWORDS.items() if r != regime for w in kws]
        for i in range(10):
            main = rng.choice(seeds, size=3, replace=False)
            noise = rng.choice(other, size=1)
            text = f"{' '.join(main)} 관련 경제 뉴스 {noise[0]} 동향 점검"
            day = int(rng.integers(1, 28))
            rows.append(
                {
                    "date": f"{month}-" f"{day:02d}",
                    "title": f"[{regime}] {main[0]} 이슈",
                    "content": text,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df, "synthetic"


def load_or_build_ecos() -> tuple[pd.DataFrame, str]:
    path = RAW / "ecos.csv"
    if path.exists():
        df = pd.read_csv(path)
        return df, "real"
    months = pd.period_range("2025-01", periods=6, freq="M").astype(str)
    rng = np.random.default_rng(7)
    rows = []
    for m in months:
        rows.extend(
            [
                {"date": f"{m}-01", "indicator": "CCSI", "value": float(rng.normal(95, 3))},
                {"date": f"{m}-01", "indicator": "KOSPI", "value": float(rng.normal(2600, 80))},
                {"date": f"{m}-01", "indicator": "USD_KRW", "value": float(rng.normal(1350, 20))},
                {"date": f"{m}-01", "indicator": "BASE_RATE", "value": float(rng.normal(3.0, 0.1))},
            ]
        )
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df, "synthetic"


def score_regimes(text: str) -> dict[str, int]:
    t = text or ""
    return {regime: sum(t.count(k) for k in kws) for regime, kws in REGIME_KEYWORDS.items()}


def assign_doc_regime(row: pd.Series) -> str:
    text = f"{row.get('title', '')} {row.get('content', '')}"
    scores = score_regimes(text)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "기타"
    return best


def build_monthly_regimes(news: pd.DataFrame) -> pd.DataFrame:
    df = news.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["doc_regime"] = df.apply(assign_doc_regime, axis=1)

    monthly = (
        df.groupby(["year_month", "doc_regime"])
        .size()
        .unstack(fill_value=0)
    )
    # 비중
    share = monthly.div(monthly.sum(axis=1), axis=0)
    share.columns = [f"share_{c}" for c in share.columns]
    dominant = monthly.idxmax(axis=1).rename("regime_label")
    out = pd.concat([dominant, share], axis=1).reset_index()
    out["n_articles"] = monthly.sum(axis=1).values
    return out


def merge_ecos_and_reaction(monthly: pd.DataFrame, ecos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    e = ecos.copy()
    e["date"] = pd.to_datetime(e["date"], errors="coerce")
    e = e.dropna(subset=["date"])
    e["year_month"] = e["date"].dt.to_period("M").astype(str)
    wide = e.pivot_table(index="year_month", columns="indicator", values="value", aggfunc="mean")
    wide = wide.reset_index()
    merged = monthly.merge(wide, on="year_month", how="inner")

    value_cols = [c for c in wide.columns if c != "year_month"]
    if not value_cols or merged.empty:
        return merged, pd.DataFrame()

    reaction = merged.groupby("regime_label")[value_cols].agg(["mean", "std"]).reset_index()
    # flatten columns
    reaction.columns = [
        "_".join([str(x) for x in col if x != ""]).strip("_")
        for col in reaction.columns.to_flat_index()
    ]
    return merged, reaction


def main() -> None:
    ensure_dirs()
    news, news_src = load_or_build_news()
    ecos, ecos_src = load_or_build_ecos()

    # 기본 통계
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
    n_rows = len(news)
    dmin, dmax = news["date"].min(), news["date"].max()
    n_months = news["date"].dt.to_period("M").nunique()
    title_null = float(news["title"].isna().mean()) if "title" in news.columns else 1.0
    content_col = "content" if "content" in news.columns else ("description" if "description" in news.columns else None)
    content_null = float(news[content_col].isna().mean()) if content_col else 1.0

    monthly = build_monthly_regimes(news)
    merged, reaction = merge_ecos_and_reaction(monthly, ecos)

    out_path = PROCESSED / "feasibility_regime_monthly.csv"
    monthly.to_csv(out_path, index=False, encoding="utf-8-sig")
    if not reaction.empty:
        reaction.to_csv(PROCESSED / "feasibility_regime_reaction.csv", index=False, encoding="utf-8-sig")

    print("=== FEASIBILITY REGIME PILOT ===")
    print(f"news_source={news_src} rows={n_rows} months={n_months} date_min={dmin.date() if pd.notna(dmin) else None} date_max={dmax.date() if pd.notna(dmax) else None}")
    print(f"title_null_ratio={title_null:.3f} content_null_ratio={content_null:.3f}")
    print(f"ecos_source={ecos_src} indicators={sorted(ecos['indicator'].dropna().unique().tolist()) if 'indicator' in ecos.columns else []}")
    print(f"overlap_months={merged['year_month'].nunique() if not merged.empty else 0}")
    print("--- sample monthly regimes ---")
    print(monthly[["year_month", "regime_label", "n_articles"]].head(12).to_string(index=False))
    if not reaction.empty:
        print("--- regime reaction (mean) ---")
        print(reaction.head(10).to_string(index=False))
    print(f"wrote={out_path}")


if __name__ == "__main__":
    main()
