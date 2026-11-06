# Phase 1: 로컬 워크스페이스 전수 감사 및 불변성 기준 명세 (`RUN_20261106_161800`)

- **감사 일시**: 2026-11-06T16:47:29.797200
- **Python 실행 환경**: `C:\Users\CDW\1_Project\DataMining\.venv\Scripts\python.exe` (`Python 3.13.15`)
- **신규 산출물 격리 경로**: `data/processed/reviewer_readiness/RUN_20261106_161800/`
- **점검 대상 핵심 파일 수**: 41개 (누락 파일: 0개)

## 1. Phase 5.6 Strict OOS 아티팩트 무결성 검증

- **기준 아티팩트 경로**: `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/`
- **전체 기사 수**: 931,709건 (학습 2021-01~2024-12: 643,095건 / 테스트 2025-01~2026-07: 288,614건)
- **학습 전용 어휘 사전 크기**: 22,193개 (`vocab_sha256 = 657DCFEDFB5C36F2AA28634A22383A18C4B67B2DCAF4BAADA76927036BA40D96`)
- **NMF 적합 표본**: 144,000건 (월 3,000건 × 48개월, 최대 월 = `2024-12`, `sample_ids_sha256 = 70353E1FCE9FB13C24221FF996425D4312D5C5F3FB34E9F6CB8494849950CA13`)
- **NMF 모델 파라미터 (`models.joblib` 실측)**: `n_components=14`, `init='nndsvd'`, `solver='cd'`, `beta_loss='frobenius'`, `max_iter=400`, `random_state=42`, `tol=0.0001`
- **`nmf_H.npy` vs `models.joblib` H 행렬 최대 절대 오차**: `0.000e+00`
- **`vocab_idf.csv` vs `models.joblib` IDF 벡터 최대 절대 오차**: `4.738e-07`

## 2. 핵심 파일 SHA-256 기준 해시 요약

| 역할 (Role) | 상대 경로 (Relative Path) | 존재 여부 | 크기 (Bytes) | SHA-256 (앞 16자리) |
| :--- | :--- | :---: | ---: | :--- |
| `manuscript_baseline` | `docs/PAPER_DRAFT_JKIICE.md` | YES | 64,066 | `1EF35FF6B8C5CFBE...` |
| `manuscript_pre_study_c_backup` | `docs/PAPER_DRAFT_JKIICE_pre_study_c_removal_20261102.md` | YES | 64,643 | `0F035DB3B8D4C11A...` |
| `manuscript_pre_final_backup` | `docs/PAPER_DRAFT_JKIICE_pre_final_correction_20261101.md` | YES | 40,369 | `D7C773353882769E...` |
| `manuscript_pre_supp_backup` | `docs/PAPER_DRAFT_JKIICE_pre_supplemental_20261101.md` | YES | 45,362 | `1F823B279CC5CF6F...` |
| `audit_reconciliation` | `docs/PAPER_RESULT_RECONCILIATION_20261101.md` | YES | 29,945 | `E7474729DFF780D6...` |
| `audit_final_correction` | `docs/PAPER_FINAL_CORRECTION_AUDIT_20261101.md` | YES | 16,489 | `321F34BF7B5EEEDF...` |
| `audit_human_removal` | `docs/PAPER_HUMAN_VALIDATION_REMOVAL_AUDIT_20261102.md` | YES | 13,369 | `CAC998A3E7C45EBD...` |
| `audit_statistical` | `docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md` | YES | 63,720 | `02A14D2797EB8A30...` |
| `final_research_results` | `docs/FINAL_RESEARCH_RESULTS.md` | YES | 9,478 | `1807143640213823...` |
| `verification_three_final` | `verification_three_analyses_final.md` | YES | 57,191 | `394BAC8139736D09...` |
| `phase5_6_core_meta` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/core_meta.json` | YES | 2,610 | `2A12D70EFFBC54E8...` |
| `phase5_6_vocab_idf` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/vocab_idf.csv` | YES | 665,913 | `B34F0FCA94BDB68F...` |
| `phase5_6_nmf_H` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/nmf_H.npy` | YES | 1,242,936 | `DCF13627CDC3283E...` |
| `phase5_6_models` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/models.joblib` | YES | 1,596,285 | `A29B7DA3FAF2134D...` |
| `phase5_6_fit_sample_ids` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/fit_sample_ids.csv` | YES | 6,080,914 | `094A7F93B806A4E8...` |
| `phase5_6_monthly_topic_share` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/monthly_topic_share.csv` | YES | 20,350 | `15E659EE5324BAC5...` |
| `phase5_6_topic_regime_mapping` | `data/processed/reactions/phase5_6_topic_regime_mapping.csv` | YES | 11,982 | `426DAAD68F92ACA5...` |
| `phase5_6_train_only_regime_monthly` | `data/processed/reactions/phase5_6_train_only_regime_monthly.csv` | YES | 28,528 | `6917D2A9236EA938...` |
| `phase5_6_pipeline_audit` | `data/processed/reactions/phase5_6_pipeline_audit.json` | YES | 12,370 | `6E6B339BA323C56F...` |
| `verification_ols_results` | `data/processed/reactions/verification_ols_results.csv` | YES | 24,488 | `F3343F7E56EC1923...` |
| `verification_corr_lag_results` | `data/processed/reactions/verification_correlation_lag_results.csv` | YES | 58,668 | `4895A02B891003C8...` |
| `verification_warning_results` | `data/processed/reactions/verification_warning_performance_results.csv` | YES | 3,803 | `D1F58EB6DACE355C...` |
| `verification_rate_hike_table` | `data/processed/reactions/verification_rate_hike_event_table.csv` | YES | 7,252 | `492DCABD9696E470...` |
| `study_a_metrics` | `data/processed/supplemental_validation/single_vs_multi_metrics.csv` | YES | 344 | `DE5E169807BCD812...` |
| `study_a_monthly` | `data/processed/supplemental_validation/single_vs_multi_monthly.csv` | YES | 13,865 | `6ED26473C46F1294...` |
| `study_a_combinations` | `data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv` | YES | 912 | `1AAC71E6C07A111E...` |
| `study_b_weekly_panel` | `data/processed/supplemental_validation/news_search_weekly_panel.csv` | YES | 85,321 | `041FC6E8ED0C0E3D...` |
| `study_b_hac_results` | `data/processed/supplemental_validation/news_search_hac_results.csv` | YES | 10,277 | `0B102E2F1DF2152B...` |
| `study_b_anchor_sensitivity` | `data/processed/supplemental_validation/news_search_anchor_sensitivity.csv` | YES | 19,680 | `6D0165B6FEFF84FE...` |
| `news_corpus_parquet` | `data/processed/corpus/news_corpus.parquet` | YES | 873,032,326 | `D351C7807D5CFE89...` |
| `monthly_panel_csv` | `data/processed/panel/monthly_panel.csv` | YES | 106,870 | `B12ADD8D70839538...` |
| `datalab_regime_daily` | `data/raw/datalab/datalab_regime_daily.csv` | YES | 9,650,885 | `25EFAF8586053734...` |
| `datalab_sub_daily` | `data/raw/datalab/datalab_sub_daily.csv` | YES | 19,069,794 | `9ECD83C2E376A546...` |
| `legacy_regime_monthly_do_not_use` | `data/processed/regimes/regime_monthly.csv` | YES | 19,132 | `BD1E3AE7799DCE2A...` |
| `script_phase5_6_v4` | `analysis/validate_strict_oos_forecast_v4.py` | YES | 68,367 | `6CBEB30FAB1B8A9A...` |
| `script_verify_three` | `analysis/verify_three_analyses.py` | YES | 39,931 | `3715D761D4ED0181...` |
| `script_study_a` | `analysis/supplemental_validation/run_study_a.py` | YES | 7,858 | `0B10D96B348708FD...` |
| `script_study_b` | `analysis/supplemental_validation/run_study_b.py` | YES | 16,870 | `21C1340B6DAED2DA...` |
| `script_study_b_hac` | `analysis/supplemental_validation/verify_hac_news_search.py` | YES | 4,955 | `BC5944CD33D9F9E0...` |
| `script_study_b_anchor` | `analysis/supplemental_validation/verify_anchor_sensitivity.py` | YES | 9,639 | `3E54FA4E8A0C9A84...` |
| `script_datalab_keywords` | `api/datalab_keyword_sets.py` | YES | 9,263 | `492751B19086B8DD...` |

## 3. 불변성 및 격리 실행 원칙 확인

1. `analysis/detect_regimes.py` 및 `data/regime_monthly.csv` (과거 8개 국면 Legacy 산출물)는 최종 6개 국면 분석 및 신규 실험의 입력으로 사용하지 않음.
2. 기존 `data/processed/phase5_6_artifacts/`, `data/processed/reactions/`, `data/processed/supplemental_validation/`, `docs/PAPER_DRAFT_JKIICE.md`는 수정하거나 덮어쓰지 않음.
3. 모든 신규 실험 코드는 `analysis/reviewer_readiness/`에, 모든 신규 실험 데이터는 `data/processed/reviewer_readiness/RUN_20261106_161800/`에 격리 저장함.