# 교수님 검토용 원고 및 수치 근거표

기준 원고는 [PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md](PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.md)이며, 저장소 기준 커밋은 `f55598c`이다. 연구의 핵심 결과는 월별 뉴스에서 함께 부각된 경제 이슈가 단일 대표 국면으로 요약될 때 어느 정도 별도 표시에서 빠지는지 정량화한 것이다. 시장과 검색 지표의 결과는 동시점 연관성으로 해석한다.

## 검토본 정정과 해석 범위

1. **4.4절 경계 주차 민감도 수치.** 82주와 83주 방식에서 8개 동시점 상관계수의 최대 절대 차이를 **0.0127**로 정정했다. 부동산 쌍에서 −0.076816 → −0.064166으로 바뀌어 차이가 0.012650이었다. 주별 패널에서 각 방식에 24개 검정 Holm 보정을 다시 적용했을 때 8개 동시점 쌍의 5% 유의성 판정은 모두 같았다. 아래 감사 CSV는 상관계수 대조에 사용했다. 최종 검토본의 유의성 판정은 주별 패널 재계산에 근거한다. [경계 주차 감사 CSV](../data/processed/reviewer_readiness/RUN_20261106_A3_2_WEEKLY_PERIOD_AUDIT_01/weekly_diff_method_comparison.csv)
2. **수식 출력.** 날짜가 붙은 DOCX와 PDF를 다시 생성했다. 식 (3)은 괄호와 슬래시를 사용한 분수로 표시되며 최댓값 연산자와 HAC 통계 용어도 본문에서 읽을 수 있게 변환했다.
3. **표현 범위.** 시황의 NMF-800 동시점 보정값 0.0508은 기본 HAC 시차 4에서 5% 기준을 충족하지 않는다. 결론에 NMF-400 결과와 함께 표기하면 해석이 명확해진다. NMF-800의 ARX 오차 감소는 19개월 민감도 실험이며, 확장창과 고정창 결과를 함께 보면 창 선택의 영향을 확인할 수 있다.

## 핵심 주장과 근거

| 원고 위치 | 수치와 해석 | 근거 파일과 확인 방식 |
| --- | --- | --- |
| 요약, 3.1~3.2절 | 931,709건, 67개월. 학습 48개월 643,095건, 평가 19개월 288,614건. 적합 144,000건, 어휘 22,193개, 기저 14 × 22,193. | Parquet 월별 집계와 국면 패널 대조. [Phase 5.6 실행 메타데이터](../data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/core_meta.json) · [표본 ID](../data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/fit_sample_ids.csv) |
| 3.2~3.3절, 표 2~3 | NMF와 LDA의 적합 표본은 144,000건, 내부 검증 48,000건. NMF 안정성 분석은 부분표본과 초기화 실험을 포함한다. | 저장 실험표 대조. [모형 비교](../data/processed/reviewer_readiness/RUN_20261106_161800/topic_model_comparison_metrics.csv) · [안정성 실행별 결과](../data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_runs.csv) |
| 3.3절, 표 4 | NMF-400 400회 상한·경고, NMF-800 447회 허용오차 기준 수렴. 재구성 오차 감소율 0.0073%. 코사인 평균 14개 0.9802, 토픽 2 제외 13개 0.9953, 최저 0.7846. | 반복·경고는 실행 기록, 코사인은 저장 기저에서 재계산. [수렴 결과](../data/processed/reviewer_readiness/RUN_20261106_NMF_CONVERGENCE_01/convergence_metrics.csv) |
| 표 5~7, 4.1절 | 학습 48개월의 평균과 표준편차로 표준화. 기준 6국면에서 112개 중 49개(43.75%) 별도 표시 누락. 학습 42/89, 평가 7/23. | 학습 통계와 월별 `z ≥ 0.5` 활성 신호를 재계산. [Phase 5.6 국면 패널](../data/processed/reactions/phase5_6_train_only_regime_monthly.csv) · [집계 코드](../analysis/supplemental_validation/run_study_a.py) |
| 표 8~9 | 사례 월 5개는 규칙 기반 선정. NMF-800 Legacy-6 누락 48/111(43.24%), 6개 부분집합 48/110(43.64%), 7국면 63/125(50.40%). | 저장 사례와 민감도 결과 대조. 7국면 비교에는 후보 국면 수의 영향이 포함된다. [사례 월](../data/processed/reviewer_readiness/RUN_20261106_161800/multi_regime_case_monthly.csv) · [민감도 집계](../data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/multiregime_comparison.csv) |
| 표 10~11 | KOSPI 67개월 동시점 HAC(시차 3), R² 0.161879, 조정 R² 0.078067, F 4.683257, p 0.000573. 금리·물가 β −0.7418, Holm p 0.0024. 자본거래 β −0.5299, Holm p 0.0129. | 월별 국면 CSV와 시장 패널을 월 기준 결합해 기준 모델 재계산. 비교 모델은 저장 결과에서 확인. [시장 패널](../data/processed/panel/monthly_panel.csv) · [회귀 결과](../data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/hac_regression_comparison.csv) |
| 4.3절 | 일반 하락 경보 OOS 17개월에서 TP 0, FP 1, FN 9, TN 7. NMF-800의 KOSPI RMSE는 확장창 15.2825 → 13.8687, 고정창 15.6018 → 15.3919. | 경보는 월별 패널에서 재계산. ARX는 저장된 비교 결과로 확인. 기준 NMF-400의 KOSPI 뉴스 결합 예측 열은 19개월 모두 결측. [기준 예측](../data/processed/reactions/phase5_6_strict_oos_forecast.csv) · [경보 및 ARX 비교](../data/processed/reviewer_readiness/RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01/strict_oos_comparison.csv) |
| 4.4절, 표 12~13 | ISO 원시 292주, 전체 차분 291주, 학습 구간 차분 208주, 평가 구간 차분 82주. 평가 기업실적 r 0.4718, Holm p 0.0011. 시황 r 0.4984, Holm p 0.0432. | 주별 패널에서 평가 구간 차분과 8쌍×3시차 HAC·Holm 재계산. [주별 패널](../data/processed/supplemental_validation/news_search_weekly_panel.csv) · [HAC 시차 민감도](../data/processed/reviewer_readiness/RUN_20261106_161800/news_search_hac_lag_sensitivity.csv) · [블록 부트스트랩](../data/processed/reviewer_readiness/RUN_20261106_161800/news_search_block_bootstrap_ci.csv) |

## 출력본 대조 범위

- [DOCX](PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.docx)의 논문 표 13개 **848셀**은 변환기가 원고에서 읽은 기대값과 공백 및 강조 표기 차이를 제외하고 전부 일치했다.
- [PDF](PAPER_DRAFT_JKIICE_DRAFT_FINAL_20261107.pdf) 19쪽과 Word에서 렌더링한 DOCX 24쪽을 훑었다. 두 출력물의 추출 텍스트에서 4.4절의 정정값 0.0127, 표 제목 1~13번, 참고문헌 24개를 확인했고 남은 LaTeX 명령은 발견되지 않았다. PDF의 셀 단위 대조는 수행하지 않았다.
- 이번 정정은 날짜가 붙은 검토본 세 파일에 반영했다. 일반 이름, 투고용 이름 및 블라인드본은 기존 파일이다.

## 재현에 필요한 로컬 자료

- Git 외부 입력은 `data/raw/bigkinds/`, `data/raw/ecos/ecos_monthly.csv`, `data/raw/datalab/datalab_*_daily.csv`이다. 경량 검산의 주요 입력은 `data/processed/corpus/news_corpus.parquet`, `data/processed/panel/monthly_panel.csv`, `data/processed/reactions/phase5_6_*` 및 위의 주별 패널이다. 세부 경로와 해시는 [작업공간 파일 목록](../data/processed/reviewer_readiness/RUN_20261106_161800/workspace_baseline_manifest.csv)에 있다.
- 로컬 검산 환경은 Windows, Python 3.13.15, pandas 3.0.5, NumPy 2.5.1, scikit-learn 1.9.0, statsmodels 0.15.0, PyArrow 25.0.1이다. [과거 실행 환경 명세](../data/processed/reviewer_readiness/RUN_20261106_161800/workspace_environment_spec.json)
- 교수님 검토 시 핵심 한계는 독립 기사 라벨링 미수행, 다중 표시의 실질 효용 미검증, 검색 API 상대지수의 조회 기간 의존성이다. 이번 점검은 기존 산출물과 경량 재계산을 근거로 하며 원자료부터 모델을 다시 적합하는 전 과정은 포함하지 않는다.
