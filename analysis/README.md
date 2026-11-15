# 분석 코드 안내

- `run_pipeline.py`, `detect_regimes.py`, `measure_reactions.py`, `robustness.py`, `rq4_search.py`: 주 분석 파이프라인과 반응·강건성 분석.
- `validate_*`, `verify_*`, `audit_final_verification.py`: 선행성·표본 외 예측·결과 검증. 버전별 스크립트는 연구 이력과 비교를 위해 보존합니다.
- `reviewer_readiness/`: 논문 수치, 심사 대응 및 모델 안정성 점검.
- `supplemental_validation/`: 추가 실증 분석.
- `visualization/`: 그림, 엑셀 및 요약 페이지 생성. 모듈 경로가 변경되었으므로 예를 들어 `python -m analysis.visualization.export_indicators_to_excel`로 실행합니다.
- `fallback_topics.py`, `fallback_bertopic.py`: 대체 토픽 모델.

[데이터 구조](../data/README.md)와 [문서 안내](../docs/자료_정리_안내.md)도 참고하세요. 전체 실행에는 원자료와 `requirements.txt`의 패키지가 필요합니다.
