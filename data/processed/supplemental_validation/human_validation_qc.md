# 연구 C: 경제 국면 의미 타당성 검증 QC 보고서 (`human_validation_qc.md`)

- **작성 일시:** 2026-11-01
- **평가 대상 표본:** Strict OOS 테스트 기간(2025-01~2026-07, 19개월) 380건 무작위 층화 표본
- **평가 방식:** 완전 블라인드 평가자 2인(평가자 A, B) 독립 라벨링

## 1. 표본 추출 및 블라인드 파일 준비 상태

- **총 표본 수:** 380건 (19개월 x 월별 20건 균등)
- **언론사 분포:** {'한국경제': 131, '매일경제': 128, '서울경제': 121}
- **블라인드 평가 파일:**
  - `human_annotation_batch_A.csv`: 생성 완료 (빈 라벨 템플릿)
  - `human_annotation_batch_B.csv`: 생성 완료 (빈 라벨 템플릿)
  - `human_annotation_codebook.md`: 6대 국면 정의 및 다중 라벨/미형성 국면 지침 작성 완료
  - `human_annotation_join_key.csv`: 원본 기사 매핑키 분리 격리 완료
  - `human_annotation_sample_manifest.csv`: 월별/언론사별 분포 매니페스트 저장 완료

## 2. 평가 현황 및 다음 단계

> [!IMPORTANT]
> **자동화 모델의 사람 라벨 대체 금지 원칙 준수**
> - 본 연구는 LLM이나 휴리스틱 모델이 사람의 판정을 대신하는 것을 엄격히 금지함.
> - 현재 단계는 **실제 인간 평가자 2인의 독립 라벨링 입력 대기 상태(WAITING FOR HUMAN LABELS)**임.
> - 실제 사람이 기사를 직접 읽고 `batch_A.csv`와 `batch_B.csv`를 작성하여 반환한 이후에만 평가자 간 일치도(Cohen's kappa)와 모델의 분류 성능(Precision, Recall, F1)을 공식 계산함.
