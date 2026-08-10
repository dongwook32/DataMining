"""
데이터마이닝 가능 여부 확인용 테스트본.

1) 공개 RSS로 경제 뉴스 수집 → data/raw/test_news.csv
2) Yahoo Finance로 KOSPI·원달러 수집 → data/raw/test_indicators.csv
3) 키워드 룰 국면 마이닝 + 지표 merge → data/processed/datamining_test_result.csv

API 키 불필요. 빅카인즈/네이버 무단 수집 없음.
"""
from __future__ import annotations

import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree.ElementTree import Element

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "_archive_pilot" / "rss_test"
PROCESSED = ROOT / "data" / "processed" / "_archive_pilot"

RSS_FEEDS = [
    "https://www.yonhapnewstv.co.kr/category/news/economy/feed/",
    "https://fs.jtbc.co.kr/RSS/economy.xml",
    "https://www.hankyung.com/feed/economy",
]

REGIME_KEYWORDS = {
    "물가": ["물가", "인플레이션", "원자재", "공공요금", "소비자물가", "물가상승", "유가", "기름값", "휘발유"],
    "금리": ["기준금리", "대출", "이자", "긴축", "금리", "한은", "채권"],
    "부동산": ["집값", "전세", "청약", "대출규제", "부동산", "아파트", "주택"],
    "대외": ["환율", "연준", "수출", "지정학", "달러", "무역", "반도체", "관세", "무역수지"],
    "성장": ["성장률", "실적", "고용", "경기", "GDP", "소비", "증시", "주가", "코스피"],
}

UA = "DataMiningFeasibilityTest/1.0 (+local research pilot)"


def ensure_dirs() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)


def http_get(url: str, timeout: int = 20) -> bytes:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()


def _text(el: Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def _parse_rss_date(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (TypeError, ValueError, IndexError):
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw[:19], fmt)
        except ValueError:
            continue
    return None


def collect_news_rss() -> pd.DataFrame:
    rows: list[dict] = []
    for feed in RSS_FEEDS:
        try:
            body = http_get(feed)
            root = ET.fromstring(body)
        except Exception as exc:  # noqa: BLE001 - 피드별 실패 허용
            print(f"[warn] RSS fail: {feed} ({type(exc).__name__}: {exc})")
            continue
        channel = root.find("channel")
        if channel is None:
            continue
        source = _text(channel.find("title")) or feed
        for item in channel.findall("item"):
            title = _text(item.find("title"))
            desc = _text(item.find("description"))
            # CDATA/HTML 대략 제거
            desc = (
                desc.replace("<![CDATA[", "")
                .replace("]]>", "")
                .replace("<br>", " ")
                .replace("<br/>", " ")
            )
            link = _text(item.find("link"))
            pub = _text(item.find("pubDate")) or _text(item.find("pubdate"))
            dt = _parse_rss_date(pub)
            if not title:
                continue
            rows.append(
                {
                    "date": dt.strftime("%Y-%m-%d") if dt else "",
                    "datetime": dt.isoformat(sep=" ") if dt else "",
                    "title": title,
                    "content": desc[:2000],
                    "link": link,
                    "source": source,
                    "feed_url": feed,
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.drop_duplicates(subset=["title"], keep="first")
    df = df.sort_values(["date", "title"], ascending=[False, True]).reset_index(drop=True)
    return df


def collect_yahoo_monthly(symbol: str, indicator: str, range_: str = "2y") -> pd.DataFrame:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?interval=1mo&range={range_}"
    )
    raw = http_get(url)
    payload = json.loads(raw.decode("utf-8"))
    result = payload["chart"]["result"][0]
    timestamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    rows = []
    for ts, val in zip(timestamps, closes):
        if val is None:
            continue
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
        rows.append(
            {
                "date": dt.strftime("%Y-%m-%d"),
                "year_month": dt.strftime("%Y-%m"),
                "indicator": indicator,
                "value": float(val),
                "source": "yahoo_finance",
                "symbol": symbol,
            }
        )
    return pd.DataFrame(rows)


def collect_indicators() -> pd.DataFrame:
    frames = [
        collect_yahoo_monthly("%5EKS11", "KOSPI"),
        collect_yahoo_monthly("KRW%3DX", "USD_KRW"),
    ]
    return pd.concat(frames, ignore_index=True)


def score_regimes(text: str) -> dict[str, int]:
    return {regime: sum(text.count(k) for k in kws) for regime, kws in REGIME_KEYWORDS.items()}


def assign_doc_regime(row: pd.Series) -> tuple[str, int]:
    text = f"{row.get('title', '')} {row.get('content', '')}"
    scores = score_regimes(text)
    best = max(scores, key=scores.get)
    return (best if scores[best] > 0 else "기타"), scores[best]


def mine_article_level(news: pd.DataFrame) -> pd.DataFrame:
    df = news.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    if df.empty:
        return pd.DataFrame()
    assigned = df.apply(assign_doc_regime, axis=1, result_type="expand")
    df["doc_regime"] = assigned[0]
    df["regime_score"] = assigned[1]
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    return df[
        ["date", "year_month", "title", "doc_regime", "regime_score", "source", "link"]
    ].sort_values(["date", "regime_score"], ascending=[False, False])


def mine_regimes(articles: pd.DataFrame) -> pd.DataFrame:
    if articles.empty:
        return pd.DataFrame()
    monthly_counts = articles.groupby(["year_month", "doc_regime"]).size().unstack(fill_value=0)
    share = monthly_counts.div(monthly_counts.sum(axis=1), axis=0)
    share.columns = [f"share_{c}" for c in share.columns]

    def _pick_label(row: pd.Series) -> str:
        # 해석 가능한 국면 우선: '기타'를 제외한 최대 비중 토픽
        candidates = row.drop(labels=["기타"], errors="ignore")
        if not candidates.empty and candidates.max() > 0:
            return str(candidates.idxmax())
        return str(row.idxmax())

    dominant = monthly_counts.apply(_pick_label, axis=1).rename("regime_label")
    out = pd.concat([dominant, share], axis=1).reset_index()
    out["n_articles"] = monthly_counts.sum(axis=1).values
    out["n_labeled"] = (
        monthly_counts.drop(columns=["기타"], errors="ignore").sum(axis=1).values
        if "기타" in monthly_counts.columns
        else monthly_counts.sum(axis=1).values
    )
    out["mining_method"] = "keyword_rule"
    return out


def merge_with_indicators(monthly: pd.DataFrame, indicators: pd.DataFrame) -> pd.DataFrame:
    if monthly.empty or indicators.empty:
        return pd.DataFrame()
    ind = indicators.copy()
    ind["year_month"] = pd.to_datetime(ind["date"], errors="coerce").dt.to_period("M").astype(str)
    wide = (
        ind.sort_values("date")
        .pivot_table(index="year_month", columns="indicator", values="value", aggfunc="last")
        .reset_index()
    )
    return monthly.merge(wide, on="year_month", how="left")


def write_run_summary(
    news: pd.DataFrame,
    indicators: pd.DataFrame,
    result: pd.DataFrame,
    paths: dict[str, Path],
) -> Path:
    summary_path = PROCESSED / "datamining_test_summary.csv"
    news_dates = pd.to_datetime(news["date"], errors="coerce") if not news.empty else pd.Series(dtype="datetime64[ns]")
    ind_dates = pd.to_datetime(indicators["date"], errors="coerce") if not indicators.empty else pd.Series(dtype="datetime64[ns]")
    rows = [
        {"metric": "news_rows", "value": len(news)},
        {"metric": "news_date_min", "value": str(news_dates.min().date()) if news_dates.notna().any() else ""},
        {"metric": "news_date_max", "value": str(news_dates.max().date()) if news_dates.notna().any() else ""},
        {"metric": "news_months", "value": int(news_dates.dt.to_period("M").nunique()) if news_dates.notna().any() else 0},
        {"metric": "indicator_rows", "value": len(indicators)},
        {"metric": "indicator_date_min", "value": str(ind_dates.min().date()) if ind_dates.notna().any() else ""},
        {"metric": "indicator_date_max", "value": str(ind_dates.max().date()) if ind_dates.notna().any() else ""},
        {
            "metric": "indicators",
            "value": ",".join(sorted(indicators["indicator"].unique())) if not indicators.empty else "",
        },
        {"metric": "result_rows", "value": len(result)},
        {"metric": "datamining_ok", "value": int(len(news) > 0 and len(result) > 0)},
        {"metric": "collection_ok", "value": int(len(news) > 0 and len(indicators) > 0)},
        {"metric": "news_csv", "value": str(paths["news"])},
        {"metric": "indicators_csv", "value": str(paths["indicators"])},
        {"metric": "result_csv", "value": str(paths["result"])},
        {"metric": "ran_at", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    ]
    pd.DataFrame(rows).to_csv(summary_path, index=False, encoding="utf-8-sig")
    return summary_path


def main() -> int:
    ensure_dirs()
    print("=== 1) 뉴스 RSS 수집 ===")
    news = collect_news_rss()
    news_path = RAW / "test_news.csv"
    news.to_csv(news_path, index=False, encoding="utf-8-sig")
    print(f"news_rows={len(news)} -> {news_path}")

    print("=== 2) 지표 수집 (Yahoo) ===")
    indicators = collect_indicators()
    ind_path = RAW / "test_indicators.csv"
    indicators.to_csv(ind_path, index=False, encoding="utf-8-sig")
    print(
        f"indicator_rows={len(indicators)} "
        f"indicators={sorted(indicators['indicator'].unique().tolist())} -> {ind_path}"
    )

    print("=== 3) 국면 데이터마이닝 ===")
    articles = mine_article_level(news)
    articles_path = PROCESSED / "datamining_test_articles.csv"
    articles.to_csv(articles_path, index=False, encoding="utf-8-sig")
    print(f"article_rows={len(articles)} -> {articles_path}")
    if not articles.empty:
        print(articles["doc_regime"].value_counts().to_string())

    monthly = mine_regimes(articles)
    result = merge_with_indicators(monthly, indicators)
    if result.empty and not monthly.empty:
        result = monthly.copy()
    result_path = PROCESSED / "datamining_test_result.csv"
    result.to_csv(result_path, index=False, encoding="utf-8-sig")
    print(f"result_rows={len(result)} -> {result_path}")
    if not result.empty:
        cols = [c for c in ["year_month", "regime_label", "n_articles", "KOSPI", "USD_KRW"] if c in result.columns]
        print(result[cols].to_string(index=False))

    summary_path = write_run_summary(
        news,
        indicators,
        result,
        {"news": news_path, "indicators": ind_path, "result": result_path},
    )
    print(f"=== 4) 요약 ===\n{summary_path}")

    labeled = int((articles["doc_regime"] != "기타").sum()) if not articles.empty else 0
    ok = len(news) > 0 and len(indicators) > 0 and len(result) > 0 and labeled > 0
    print(f"labeled_articles={labeled}")
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
