# datalab_sub_monthly.csv — 컬럼 설명

국면 안 세부 이슈 28개의 **월별** 검색 관심도.

| 컬럼 | 설명 |
|------|------|
| date | 해당 월 |
| regime | 소속 국면 (물가, 금리, …) |
| group | 세부 그룹 이름 (예: 기준금리, 청약분양) |
| keywords | 이 세부 그룹에 넣은 검색어들 |
| score | 데이터랩 원점수 |
| anchor_score | 기준 검색어(은행)의 점수 |
| score_rel | score ÷ anchor_score (**분석에 쓰는 값**) |
| period_start | 조회 시작일 |
| period_end | 조회 종료일 |
| time_unit | month = 월간 |
| collected_at | 이 파일을 받은 시각 |
