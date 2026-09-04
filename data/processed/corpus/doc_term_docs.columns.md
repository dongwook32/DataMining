# doc_term_docs.parquet — 컬럼 설명

`doc_term.npz` 행렬의 **행** 정의. 행 순서는 `news_corpus.parquet`와 정확히 같다.

| 컬럼 | 설명 |
|------|------|
| article_id | 기사 식별자. `news_corpus.parquet`와 조인하는 키 |
| month | 그 기사의 연-월. 토픽 비중을 월별로 집계할 때 쓴다 |
| n_terms | 그 기사에서 선택 어휘에 걸린 어휘 수 (= 해당 행의 비영 원소 수) |

`n_terms == 0`인 행이 6건 있다. 선택 어휘가 하나도 없는 기사라 토픽 비중이 정의되지
않으므로 모델을 돌리기 전에 빼야 한다.
