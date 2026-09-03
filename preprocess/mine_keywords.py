"""통합 코퍼스에서 국면 후보 키워드를 뽑는다.

  python -m preprocess.mine_keywords --stage df       # 1) 전체 문서빈도
  python -m preprocess.mine_keywords --stage monthly  # 2) 상위어의 월별 문서빈도
  python -m preprocess.mine_keywords --stage cluster  # 3) 월별 시계열 동조성으로 군집

입력은 빅카인즈 `키워드` 컬럼이다. 이 컬럼은 원문 전체를 형태소 분석한 결과라
200자로 잘린 `본문`과 달리 기사 전체 내용을 담고 있다.

3단계 군집은 "국면"을 데이터로 정의하기 위한 것이다. 같은 국면에 속하는 어휘라면
월별 등장 빈도가 함께 오르내릴 것이라는 가정에 따라, 월별 문서빈도 시계열의
상관을 거리로 삼아 어휘를 묶는다. 사람이 미리 정한 분류를 코퍼스에 맞추는 것이 아니라
코퍼스가 만든 묶음에 이름을 붙이는 방향이다.

산출:
  data/processed/corpus/keyword_df.csv        어휘별 전체 문서빈도
  data/processed/corpus/keyword_monthly.csv   상위 어휘 × 67개월 문서빈도
  data/processed/corpus/keyword_clusters.csv  군집 배정 결과
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.cluster import AgglomerativeClustering

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "processed" / "corpus" / "news_corpus.parquet"
OUT_DIR = ROOT / "data" / "processed" / "corpus"

DF_PATH = OUT_DIR / "keyword_df.csv"
MONTHLY_PATH = OUT_DIR / "keyword_monthly.csv"
CLUSTER_PATH = OUT_DIR / "keyword_clusters.csv"

# 신문사·취재 관용어처럼 주제와 무관하게 깔리는 어휘.
# 빈도 상한(--max-df)으로 대부분 걸러지지만, 상한을 넘지 않으면서도 무의미한 것들을 따로 뺀다.
BOILERPLATE = {
    "기자", "관계자", "서울경제", "매일경제", "한국경제", "서울경제신문", "매경",
    "연합뉴스", "뉴스", "신문", "특파원", "사진", "제공", "무단", "전재", "재배포",
    "금지", "저작권", "이메일", "구독", "기사", "보도", "인터뷰", "설명", "밝혔",
    "이날", "지난해", "올해", "내년", "지난달", "이번", "최근", "당시", "현재",
    "대표", "사장", "회장", "부회장", "이사", "위원장", "장관", "차관", "청장",
    "오전", "오후", "이상", "이하", "가운데", "경우", "부분", "상황", "가능성",
}

# 절기·회계일정 어휘. 국면이 아니라 달력을 따라 오르내려서 군집을 통째로 삼킨다.
CALENDAR = {
    "상반기", "하반기", "연초", "연말", "연중", "새해", "명절", "설날", "추석",
    "연휴", "겨울", "여름", "가을", "성수기", "비수기", "정기", "총회", "주주총회",
    "동기", "당기", "잠정", "지난", "임기", "선임", "신임", "의결", "안건", "승진",
}

# 날짜·수량 토큰: '3일', '2022년', '1분기', '0.5%', '2차' 등.
NUMERIC_TOKEN = re.compile(r"^\d+(?:\.\d+)?\s*(?:일|월|년|분기|주|차|%|명|건|원|억|조)?$")

MIN_TOKEN_LEN = 2
BATCH_ROWS = 50_000


def _tokens(cell: str) -> set[str]:
    out = set()
    for raw in cell.split(","):
        tok = raw.strip()
        if len(tok) < MIN_TOKEN_LEN or tok in BOILERPLATE or tok in CALENDAR:
            continue
        if NUMERIC_TOKEN.match(tok):
            continue
        out.add(tok)
    return out


def stage_df() -> None:
    """문서빈도 1패스. 한 기사에서 같은 어휘가 여러 번 나와도 1로 센다."""
    counter: Counter[str] = Counter()
    n_docs = 0
    reader = pq.ParquetFile(CORPUS)
    for batch in reader.iter_batches(batch_size=BATCH_ROWS, columns=["keywords"]):
        col = batch.column("keywords").to_pylist()
        n_docs += len(col)
        for cell in col:
            counter.update(_tokens(cell or ""))
        print(f"  {n_docs:,}건 처리 · 어휘 {len(counter):,}", flush=True)

    df = pd.DataFrame(counter.items(), columns=["term", "df"]).sort_values("df", ascending=False)
    df["df_ratio"] = df["df"] / n_docs
    df.to_csv(DF_PATH, index=False, encoding="utf-8-sig")
    print(f"\n문서 {n_docs:,} · 고유 어휘 {len(df):,} → {DF_PATH}")
    print(df.head(40).to_string(index=False))


def stage_monthly(top_n: int, min_df: int, max_df_ratio: float) -> None:
    """상위 어휘의 월별 문서빈도 행렬."""
    vocab_df = pd.read_csv(DF_PATH)
    keep = vocab_df[(vocab_df["df"] >= min_df) & (vocab_df["df_ratio"] <= max_df_ratio)]
    vocab = list(keep.head(top_n)["term"])
    index = {t: i for i, t in enumerate(vocab)}
    print(f"어휘 {len(vocab):,}개 선택 (df>={min_df}, df_ratio<={max_df_ratio})")

    # 2022년 파일은 32일 블록이라 한 달이 여러 파일에 걸쳐 나온다.
    # 행 순서를 믿지 말고 월을 키로 누적한다.
    acc: dict[str, np.ndarray] = {}
    doc_counts: Counter[str] = Counter()

    reader = pq.ParquetFile(CORPUS)
    for batch in reader.iter_batches(batch_size=BATCH_ROWS, columns=["month", "keywords"]):
        for month, cell in zip(batch.column("month").to_pylist(), batch.column("keywords").to_pylist()):
            vec = acc.get(month)
            if vec is None:
                vec = acc[month] = np.zeros(len(vocab), dtype=np.int32)
            doc_counts[month] += 1
            for tok in _tokens(cell or ""):
                pos = index.get(tok)
                if pos is not None:
                    vec[pos] += 1
        print(f"  ...{month}", flush=True)

    months = sorted(acc)
    mat = pd.DataFrame(np.vstack([acc[m] for m in months]), index=months, columns=vocab)
    mat.insert(0, "_n_docs", [doc_counts[m] for m in months])
    mat.index.name = "month"
    mat.to_csv(MONTHLY_PATH, encoding="utf-8-sig")
    print(f"\n{mat.shape[0]}개월 × {len(vocab):,}어 → {MONTHLY_PATH}")


def stage_cluster(n_clusters: int, min_cv: float) -> None:
    """월별 점유율 시계열의 상관으로 어휘를 묶는다."""
    mat = pd.read_csv(MONTHLY_PATH, index_col="month")
    n_docs = mat.pop("_n_docs")
    share = mat.div(n_docs, axis=0)

    # 시간에 따라 거의 변하지 않는 어휘는 국면을 구분하지 못한다.
    cv = share.std() / share.mean()
    vocab = cv[cv >= min_cv].index
    print(f"변동계수 {min_cv} 이상 어휘 {len(vocab):,} / {share.shape[1]:,}")

    z = ((share[vocab] - share[vocab].mean()) / share[vocab].std()).T
    model = AgglomerativeClustering(n_clusters=n_clusters, metric="cosine", linkage="average")
    labels = model.fit_predict(z.values)

    out = pd.DataFrame({
        "term": vocab,
        "cluster": labels,
        "df": mat[vocab].sum().values,
        "cv": cv[vocab].values,
    }).sort_values(["cluster", "df"], ascending=[True, False])
    out.to_csv(CLUSTER_PATH, index=False, encoding="utf-8-sig")

    print(f"\n군집 {n_clusters}개 → {CLUSTER_PATH}\n")
    for cid, grp in out.groupby("cluster"):
        top = grp.head(30)["term"].tolist()
        peak = z.loc[grp["term"]].mean().idxmax()
        print(f"[{cid}] {len(grp):,}어 · 피크 {peak}")
        print(f"    {', '.join(top)}\n")


def stage_topics(n_topics: int, top_n: int, min_df: int, max_df_ratio: float, per_month: int) -> None:
    """문서 표본에 NMF를 걸어 주제 축을 본다.

    3단계 군집이 "함께 움직이는 어휘"를 찾는다면 여기서는 "함께 등장하는 어휘"를 찾는다.
    앞의 것은 국면(시간 축), 뒤의 것은 주제(내용 축)라서 데이터랩 키워드 그룹을 짤 때
    둘을 겹쳐 봐야 한다. 문서 수가 많아 월별로 같은 수만큼 뽑아 시기 편향을 없앤다.
    """
    from sklearn.decomposition import NMF
    from sklearn.feature_extraction.text import TfidfVectorizer

    vocab_df = pd.read_csv(DF_PATH)
    keep = vocab_df[(vocab_df["df"] >= min_df) & (vocab_df["df_ratio"] <= max_df_ratio)]
    vocab = list(keep.head(top_n)["term"])

    by_month: dict[str, list[str]] = {}
    reader = pq.ParquetFile(CORPUS)
    for batch in reader.iter_batches(batch_size=BATCH_ROWS, columns=["month", "keywords"]):
        for month, cell in zip(batch.column("month").to_pylist(), batch.column("keywords").to_pylist()):
            bucket = by_month.setdefault(month, [])
            if len(bucket) < per_month:
                bucket.append(cell or "")
    docs, doc_months = [], []
    for month in sorted(by_month):
        docs.extend(by_month[month])
        doc_months.extend([month] * len(by_month[month]))
    print(f"표본 {len(docs):,}건 ({len(by_month)}개월 × 최대 {per_month:,}) · 어휘 {len(vocab):,}")

    vec = TfidfVectorizer(vocabulary=vocab, analyzer=lambda s: list(_tokens(s)))
    x = vec.fit_transform(docs)
    model = NMF(n_components=n_topics, init="nndsvd", random_state=42, max_iter=400)
    w = model.fit_transform(x)
    terms = np.array(vocab)

    weights = pd.DataFrame(w, index=pd.Index(doc_months, name="month"))
    monthly = weights.groupby("month").mean()
    monthly = monthly.div(monthly.sum(axis=1), axis=0)

    print()
    for k in range(n_topics):
        top = terms[np.argsort(model.components_[k])[::-1][:22]]
        series = monthly[k]
        print(f"[{k:>2}] 비중 {series.mean():.1%} · 피크 {series.idxmax()} ({series.max():.1%})"
              f" · 저점 {series.idxmin()}")
        print(f"     {', '.join(top)}\n")

    monthly.to_csv(OUT_DIR / "topic_monthly_share.csv", encoding="utf-8-sig")
    print(f"월별 토픽 비중 → {OUT_DIR / 'topic_monthly_share.csv'}")


def main() -> None:
    p = argparse.ArgumentParser(description="코퍼스 키워드 마이닝")
    p.add_argument("--stage", choices=("df", "monthly", "cluster", "topics"), required=True)
    p.add_argument("--top-n", type=int, default=3000, help="monthly 단계에서 남길 어휘 수")
    p.add_argument("--min-df", type=int, default=500, help="monthly 단계 최소 문서빈도")
    p.add_argument("--max-df-ratio", type=float, default=0.15, help="이 비율을 넘으면 너무 흔한 말")
    p.add_argument("--clusters", type=int, default=12)
    p.add_argument("--min-cv", type=float, default=0.35, help="cluster 단계 최소 변동계수")
    p.add_argument("--topics", type=int, default=14)
    p.add_argument("--per-month", type=int, default=3000, help="topics 단계 월별 표본 수")
    a = p.parse_args()

    if a.stage == "df":
        stage_df()
    elif a.stage == "monthly":
        stage_monthly(a.top_n, a.min_df, a.max_df_ratio)
    elif a.stage == "cluster":
        stage_cluster(a.clusters, a.min_cv)
    else:
        stage_topics(a.topics, a.top_n, a.min_df, a.max_df_ratio, a.per_month)


if __name__ == "__main__":
    main()
