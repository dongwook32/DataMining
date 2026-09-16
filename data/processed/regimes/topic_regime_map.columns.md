# topic_regime_map.csv — 컬럼 설명

14토픽을 국면 대분류 7개에 접는 표. 여러 토픽이 한 국면에 붙을 수 있다.

| 컬럼 | 설명 |
|------|------|
| topic | 토픽 번호 |
| regime | 배정된 국면 라벨. 키워드 질량이 없으면 `기타` |
| source | `auto` (키워드 겹침) 또는 `manual` (상위 어휘를 보고 덮어씀) |
| score | 그 국면 키워드에 실린 H 질량 |
| score_share | score / 그 토픽 H 행합 |
| second_regime | 질량 2위 국면 |
| second_score | 2위 질량 |
| top_terms | 상위 어휘 (쉼표 구분). 매핑을 사람이 읽을 때 쓴다 |
