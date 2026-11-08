# 연구 A-3.2: 주별 데이터 ISO 주차 및 표본 수 감사 QC 보고서 (`RUN_20261106_A3_2_WEEKLY_PERIOD_AUDIT_01`)

- **검증 일시**: `2026-11-06T22:21:02.276213+09:00` (소요 시간: `0.09s`)
- **보호 대상 파일 무결성 검증**: 총 `8`개 파일 SHA-256 사전·사후 대조 결과 **`protected_files_modified = 0` (PASS)**
- **필수 산출물 6종 생성 확인**:
  1. `weekly_iso_index_audit.csv`: 생성 완료 (292 rows) - **PASS**
  2. `weekly_period_count_audit.csv`: 생성 완료 (10 rows) - **PASS**
  3. `weekly_diff_method_comparison.csv`: 생성 완료 (8 rows) - **PASS**
  4. `weekly_duplicate_missing_report.csv`: 생성 완료 (7 rows) - **PASS**
  5. `weekly_period_audit_report.md`: 생성 완료 (11507 bytes) - **PASS**
  6. `weekly_period_audit_qc.md`: 본 QC 보고서 - **PASS**

## 주요 감사 결과 요약
- **ISO 주차 무결성**: 2020-W53부터 2026-W31까지 292개 전수 고유 주차 확인 (중복 0, 결측 0)
- **Train 209주 원인**: 2021-01-01~03(486건 기사)이 ISO 8601 표준에 의해 2020-W53에 배속됨 (1 + 208 = 209주)
- **차분 표본 수 재현**: Full 291주 (2021-W01~2026-W31), Train 208주 (2021-W01~2024-W52), OOS 82주 (2025-W02~2026-W31) 100% 재현 확인
- **차분 방식 비교 (Method B vs C)**: OOS 82주 vs 83주 상관계수 차이 |delta r| <= 0.0045, 유의성 판정 100% 동일. 기존 결과 재계산 불필요
- **환경 사양**: Python 3.13.15 on Windows-11-10.0.26300-SP0