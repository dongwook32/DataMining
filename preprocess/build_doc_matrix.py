"""통합 코퍼스 전량 → 문서×어휘 희소행렬 (토픽모델 입력).

  python -m preprocess.build_doc_matrix              # 기본 설정으로 생성
  python -m preprocess.build_doc_matrix --dry-run    # 어휘 선정만 보고 종료

`mine_keywords --stage topics`는 월별 앞 3,000건만 뽑아 쓴다. parquet 행 순서가
날짜·언론사순이라 그 표본은 월초 기사와 특정 매체로 기울어 있다. 탐색 단계에서는
문제가 없지만 국면 시계열을 확정하는 본분석 입력으로는 쓸 수 없다. 여기서는
표본 없이 코퍼스 전량을 한 번에 행렬로 만든다.

값은 이진(등장 1 / 미등장 0)이다. 빅카인즈 `키워드` 컬럼은 원문 형태소 분석 결과를
중복 없이 나열한 것에 가까워 빈도 정보가 신뢰할 만하지 않다. TF-IDF 가중은 Step 3에서
`TfidfTransformer`로 얹는다.

산출:
  data/processed/corpus/doc_term.npz          CSR 희소행렬 (문서 × 어휘, 이진)
  data/processed/corpus/doc_term_vocab.csv    열 순서대로의 어휘와 코퍼스 내 문서빈도
  data/processed/corpus/doc_term_docs.parquet 행 순서대로의 article_id · month · 어휘수
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import sparse

from preprocess.mine_keywords import BATCH_ROWS, DF_PATH, _tokens

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "processed" / "corpus"
CORPUS = OUT_DIR / "news_corpus.parquet"

MATRIX_PATH = OUT_DIR / "doc_term.npz"
VOCAB_PATH = OUT_DIR / "doc_term_vocab.csv"
DOCS_PATH = OUT_DIR / "doc_term_docs.parquet"


def select_vocab(min_df: int, max_df_ratio: float, top_n: int) -> list[str]:
    """`keyword_df.csv`에서 토픽 어휘를 고른다.

    min_df 미만은 토픽 축을 만들 만큼 반복되지 않고, max_df_ratio를 넘으면
    모든 기사에 깔려 있어 토픽을 구분하지 못한다.
    """
    df = pd.read_csv(DF_PATH)
    keep = df[(df["df"] >= min_df) & (df["df_ratio"] <= max_df_ratio)]
    keep = keep.sort_values("df", ascending=False).head(top_n)
    print(
        f"어휘 {len(keep):,}개 선택 "
        f"(전체 {len(df):,} · df>={min_df} · df_ratio<={max_df_ratio} · 상한 {top_n:,})"
    )
    print(f"  df 범위 {keep['df'].min():,} ~ {keep['df'].max():,}")
    return list(keep["term"])


def build(min_df: int, max_df_ratio: float, top_n: int) -> None:
    vocab = select_vocab(min_df, max_df_ratio, top_n)
    index = {term: i for i, term in enumerate(vocab)}

    col_chunks: list[np.ndarray] = []
    row_len_chunks: list[np.ndarray] = []
    article_ids: list[str] = []
    months: list[str] = []

    n_docs = 0
    reader = pq.ParquetFile(CORPUS)
    for batch in reader.iter_batches(
        batch_size=BATCH_ROWS, columns=["article_id", "month", "keywords"]
    ):
        ids = batch.column("article_id").to_pylist()
        mons = batch.column("month").to_pylist()
        cells = batch.column("keywords").to_pylist()

        cols: list[int] = []
        lengths = np.empty(len(cells), dtype=np.int32)
        for i, cell in enumerate(cells):
            hit = sorted({index[t] for t in _tokens(cell or "") if t in index})
            cols.extend(hit)
            lengths[i] = len(hit)

        col_chunks.append(np.asarray(cols, dtype=np.int32))
        row_len_chunks.append(lengths)
        article_ids.extend(ids)
        months.extend(mons)
        n_docs += len(cells)
        print(f"  {n_docs:,}건 처리 · 누적 비영 {sum(c.size for c in col_chunks):,}", flush=True)

    indices = np.concatenate(col_chunks)
    row_lengths = np.concatenate(row_len_chunks)
    indptr = np.zeros(n_docs + 1, dtype=np.int64)
    np.cumsum(row_lengths, out=indptr[1:])

    matrix = sparse.csr_matrix(
        (np.ones(indices.size, dtype=np.float32), indices, indptr),
        shape=(n_docs, len(vocab)),
    )
    sparse.save_npz(MATRIX_PATH, matrix)

    docs = pd.DataFrame({
        "article_id": article_ids,
        "month": months,
        "n_terms": row_lengths,
    })
    docs.to_parquet(DOCS_PATH, index=False)

    # 코퍼스 내 실제 문서빈도. keyword_df.csv는 필터 이전 값이라 열 합계와 다를 수 있다.
    col_df = np.asarray(matrix.sum(axis=0)).ravel().astype(np.int64)
    pd.DataFrame({"col": np.arange(len(vocab)), "term": vocab, "df": col_df}).to_csv(
        VOCAB_PATH, index=False, encoding="utf-8-sig"
    )

    density = matrix.nnz / (matrix.shape[0] * matrix.shape[1])
    empty = int((row_lengths == 0).sum())
    print("\n=== 문서-어휘 행렬 ===")
    print(f"형태          {matrix.shape[0]:,} × {matrix.shape[1]:,}")
    print(f"비영 원소     {matrix.nnz:,}  (밀도 {density:.5%})")
    print(f"문서당 어휘   평균 {row_lengths.mean():.1f} · 중앙값 {int(np.median(row_lengths))} "
          f"· 최대 {row_lengths.max()}")
    print(f"빈 문서       {empty:,}건  (선택 어휘가 하나도 없음 → Step 3에서 제외 대상)")

    by_month = docs.groupby("month").agg(n=("article_id", "size"), terms=("n_terms", "mean"))
    print(f"\n월 {len(by_month)}개 · 건수 {by_month['n'].min():,} ~ {by_month['n'].max():,}")
    print(f"월별 문서당 어휘수 {by_month['terms'].min():.1f} ~ {by_month['terms'].max():.1f}")

    print(f"\n행렬 → {MATRIX_PATH}")
    print(f"어휘 → {VOCAB_PATH}")
    print(f"문서 → {DOCS_PATH}")


def main() -> None:
    p = argparse.ArgumentParser(description="코퍼스 전량 → 문서-어휘 행렬")
    p.add_argument("--min-df", type=int, default=200, help="최소 문서빈도")
    p.add_argument("--max-df-ratio", type=float, default=0.15, help="이 비율을 넘으면 너무 흔한 말")
    p.add_argument("--top-n", type=int, default=30_000, help="어휘 수 상한")
    p.add_argument("--dry-run", action="store_true", help="어휘 선정만 출력하고 종료")
    a = p.parse_args()

    if a.dry_run:
        select_vocab(a.min_df, a.max_df_ratio, a.top_n)
        return
    build(a.min_df, a.max_df_ratio, a.top_n)


if __name__ == "__main__":
    main()
