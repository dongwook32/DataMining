# 연구 D: 네이버 검색 교차 검증 강건성 QC 보고서 (`news_search_robustness_qc.md`)

- **실행 ID**: `RUN_20261106_161800`
- **기존 `news_search_hac_results.csv` (maxlags=4) 재현 오차**: 상관계수 최대 절대 오차 `0.00e+00`, `hac_p_holm` 최대 절대 오차 `8.33e-17` (100% 수치 일치 확인)
- **HAC 시차 민감도 행 수**: 216행 (3 splits × 3 maxlags[2,4,8] × 8 pairs × 3 lags[-1,0,+1] = 216행, 결측 0건)
- **이동 블록 부트스트랩 행 수**: 72행 (3 splits × 3 block lengths[2,4,8] × 8 pairs = 72행, 각 B=2,000회 반복, seed=42)