# 데이터 안내

- `raw/`: 데이터 출처별 원자료 위치. 현재 저장소에는 실제 원자료가 모두 포함되어 있지 않습니다.
- `processed/corpus/`, `panel/`, `regimes/`, `reactions/`: 코퍼스, 패널, 국면과 분석 결과. 스크립트에서 직접 사용하는 경로이므로 유지합니다.
- `processed/phase5_6_artifacts/`: 학습된 모델과 분석 당시 산출물.
- `processed/reviewer_readiness/`, `supplemental_validation/`: 심사 대응·추가 검증의 실행별 증거. 파일 내용이 같아도 각 실행의 산출물일 수 있어 보존합니다.
- `processed/exports/`: 엑셀 시각화 결과물 두 개. 생성 코드는 `analysis.visualization`에 있습니다.
- `processed/*_lda/`, `*_bertopic/`: 대체 토픽 모델 산출물.

`.gitignore`에 따라 일부 대용량 원자료와 가공 데이터는 GitHub에 포함되지 않습니다. 따라서 저장소를 내려받은 것만으로 전체 분석이 재현된다고 가정하면 안 됩니다.
