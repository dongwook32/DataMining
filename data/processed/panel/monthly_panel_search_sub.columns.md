# monthly_panel_search_sub.csv — 컬럼 설명

검색 세부 28그룹의 월별 `score_rel`. 대분류 7국면을 쪼갠 것이라
국면 라벨의 강건성 검증(어느 세부 이슈가 국면을 끌고 갔는지)에 쓴다.

| 컬럼 | 설명 |
|------|------|
| month | 연-월. `monthly_panel.csv`와의 조인 키 |
| in_study | 분석 창 여부 |
| 그 외 28열 | 세부 그룹명 = 값은 `score_rel` |

세부 그룹 목록과 각 그룹의 검색어는 `data/raw/datalab/datalab_keywords.md`와
`api/datalab_keyword_sets.py`에 있다.

대분류와 달리 z-점수·점유율·변화율을 미리 만들어 두지 않았다. 세부 그룹은
어떤 조합으로 묶어 볼지가 분석마다 달라서, 파생은 쓰는 쪽에서 만드는 편이 낫다.
