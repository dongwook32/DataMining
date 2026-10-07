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
| active_{slug} | 국면별 z >= 0.5 활성화 여부 이진 플래그 (1 또는 0) |
| n_active | 그달 활성화된 국면 수 (1 ~ 4개) |
| active_regimes | 활성화된 국면 목록 (z점수 내림차순 쉼표 구분) |

`share_*`와 `residual_share`의 합은 1이다. 우세 라벨(`dominant_regime`)은 단일 참고용이고,
본연구의 활성 국면은 표본 내 z점수 임계값(`z >= 0.5`)을 넘긴 다중 국면 집합(`active_*`, `active_regimes`)이다.
