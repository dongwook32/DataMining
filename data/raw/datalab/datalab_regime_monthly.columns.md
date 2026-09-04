# datalab_regime_monthly.csv — 컬럼 설명

국면(대분류) 7개의 **월별** 검색 관심도.

| 컬럼 | 설명 |
|------|------|
| date | 해당 월 |
| regime | 국면 이름 (물가, 금리, …) |
| group | 그룹 이름 (대분류 파일에서는 regime과 같음) |
| keywords | 이 그룹에 넣은 검색어들 |
| score | 데이터랩 원점수 (같은 요청 안에서만 비교) |
| anchor_score | 기준 검색어(은행)의 점수 |
| score_rel | score ÷ anchor_score (**분석에 쓰는 값**) |
| period_start | 조회 시작일 |
| period_end | 조회 종료일 |
| time_unit | month = 월간 |
| collected_at | 이 파일을 받은 시각 |
