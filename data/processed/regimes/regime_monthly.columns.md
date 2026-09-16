# regime_monthly.csv — 컬럼 설명

월별 국면 시계열. Step 4는 `month`로 월 패널과 조인한다.

| 컬럼 | 설명 |
|------|------|
| month | 연-월 |
| n_docs | 그달 적합에 들어간 기사 수 (`n_terms=0` 제외) |
| share_{slug} | 그 국면에 매핑된 토픽 비중의 합. slug는 config `regimes.slugs` |
| residual_share | `기타`로 남은 토픽 비중 |
| dominant_regime | 국면 비중 표본 내 z점수 argmax. Step 4 조인에 쓰는 라벨 |
| dominant_share | 그 라벨의 원비중 |
| dominant_z | 그 라벨의 z점수 |
| dominant_raw | 원비중 argmax (참고. 상시 큰 축이 매달 이김) |
| dominant_raw_share | 원비중 최댓값 |
| runner_up | z점수 2위 국면 |
| runner_up_share | 2위 원비중 |
| runner_up_z | 2위 z점수 |

`share_*` 일곱 개와 `residual_share`의 합은 1이다. 우세 라벨은 요약이고,
공존 이슈는 비중 벡터로 본다.
