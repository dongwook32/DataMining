# rq4_corr.csv — 컬럼 설명

같은 국면의 뉴스 비중(`share_{slug}`)과 검색 지표의 월별 상관. n=67.

| 컬럼 | 설명 |
|------|------|
| regime | 국면 라벨 |
| search_kind | `score_rel` · `z` · `share` |
| n | 개월 |
| pearson, spearman | 상관계수. 뉴스 비중 분산 0이면 결측 |
| note | 물가는 뉴스 축이 없어 분산 0 |
