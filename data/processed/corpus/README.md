# 코퍼스 산출물

뉴스 통합 파일은 `news_corpus.parquet` (용량이 커서 CSV가 아님).

각 CSV 옆의 `*.columns.md`에 컬럼 짧은 설명이 있습니다.

## 파일

| 파일 | 만든 것 | 용도 |
|------|---------|------|
| `news_corpus.parquet` | `build_corpus` | 기사 931,709건 (2021-01~2026-07) |
| `corpus_monthly_counts.csv` | `build_corpus` | 월별 건수 점검 |
| `keyword_df.csv` | `mine_keywords --stage df` | 어휘별 전체 문서빈도 |
| `keyword_monthly.csv` | `mine_keywords --stage monthly` | 상위 어휘 × 67개월 |
| `keyword_clusters.csv` | `mine_keywords --stage cluster` | 월별 동조성 군집 |
| `topic_monthly_share.csv` | `mine_keywords --stage topics` | NMF 14토픽 월별 비중 (**탐색용**) |
| `doc_term.npz` | `build_doc_matrix` | 문서×어휘 희소행렬 (**본분석 입력**) |
| `doc_term_vocab.csv` | `build_doc_matrix` | 행렬의 열 정의 |
| `doc_term_docs.parquet` | `build_doc_matrix` | 행렬의 행 정의 |

## 탐색용과 본분석용의 차이

`topic_monthly_share.csv`는 월별로 앞 3,000건씩만 뽑은 201,000건 표본으로 만들었습니다.
parquet 행 순서가 날짜·언론사순이라 그 표본은 월초 기사와 특정 매체로 기울어 있습니다.
국면 대분류를 정하는 탐색 단계에서는 문제가 없었지만, 국면 시계열을 확정하는 본분석
입력으로는 쓸 수 없습니다.

Step 3은 표본이 아닌 `doc_term.npz`(전량 931,709건)를 씁니다.

```python
from scipy import sparse
import pandas as pd

X = sparse.load_npz("data/processed/corpus/doc_term.npz")   # 931,709 × 28,343
vocab = pd.read_csv("data/processed/corpus/doc_term_vocab.csv")     # 열 정의
docs = pd.read_parquet("data/processed/corpus/doc_term_docs.parquet")  # 행 정의
```

행렬 값은 이진(등장 1 / 미등장 0)입니다. 빅카인즈 `키워드` 컬럼은 형태소 분석 결과를
중복 없이 나열한 것에 가까워 빈도 정보를 믿기 어렵기 때문입니다. TF-IDF 가중은
`sklearn.feature_extraction.text.TfidfTransformer`로 쓰는 쪽에서 얹습니다.
