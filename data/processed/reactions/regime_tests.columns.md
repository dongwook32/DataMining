# regime_tests.csv — 컬럼 설명

국면 그룹 차이 검정.

| 컬럼 | 설명 |
|------|------|
| dep_var | 종속변수 |
| test | `kruskal` · `anova` · `levene_bf` |
| k_groups | 검정에 넣은 국면 수 (개월 5 미만 제외) |
| n | 사용한 개월 합 |
| statistic | H / F / W |
| p_value | 양측 p |
| effect | KW면 epsilon², ANOVA면 eta² |
| effect_name | 효과크기 이름 |
