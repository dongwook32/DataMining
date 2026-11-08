# 연구 A-3.1: 후속 실증분석 결과 일관성 감사 QC 보고서 (`RUN_20261106_A3_CONSISTENCY_AUDIT_01`)

- **검증 일시**: `2026-11-06T21:47:28.504369+09:00` (소요 시간: `0.11s`)
- **보호 대상 파일 무결성 검증**: 총 `41`개 파일 SHA-256 사전·사후 대조 결과 **`protected_files_modified = 0` (PASS)**
- **감사 필수 산출물 6종 생성 확인**:
  1. `a3_internal_consistency_audit.md`: 생성 완료 (15203 bytes) - **PASS**
  2. `metric_discrepancy_table.csv`: 생성 완료 (8 rows) - **PASS**
  3. `claim_verification_table.csv`: 생성 완료 (8 rows) - **PASS**
  4. `period_definition_audit.csv`: 생성 완료 (11 rows) - **PASS**
  5. `final_approved_numbers.csv`: 생성 완료 (38 rows) - **PASS**
  6. `audit_qc.md`: 본 QC 보고서 - **PASS**

## 주요 감사 판정 결과 요약
- **토픽 유사도 불일치**: A-3 보고서의 '14개 평균 0.9953' 기술은 'Topic 2 제외 13개 평균(0.9953)'의 텍스트 오기임이 규명됨. (A-2 원본 14개 평균 0.9802, 최소 0.7846 승인 확정)
- **5대 불변 국면 상관**: Pearson r 0.9910~0.9998로 수치 완전 일치 (**PASS**)
- **부동산 Legacy-6 합산**: Pearson r 0.9648(Full), 0.9693(OOS)로 수치 완전 일치 (**PASS**)
- **다중 국면 누락 신호**: NMF-400 43.75% vs NMF-800 6국면 43.24%~43.64%, 7국면 50.40% 수치 완전 일치 (**PASS**, 문구 정밀화 확정)
- **HAC 회귀분석**: kospi_ret_std 핵심 계수 부호 및 Holm 유의성 100% 보존 확인 (**PASS**, Adj. R2 병기 확정)
- **Strict OOS 조기경보**: 17개월 혼동행렬 TP=0, FP=1, FN=9, TN=7 100% 일치 (**PASS**)
- **한은 기준금리 인상**: 7/7(100%)은 표본 내 본격 인상기 국한, 전체 7/11(63.6%) 표본 범위 한정 확정 (**PASS**)
- **네이버 주별 교차검증**: 사전 정의 24개 검정 일치 확인, OOS market lag=4 Holm 경계선(0.0508) 투명 보고 확정 (**PASS**)
- **환경 사양**: Python 3.13.15 on Windows-11-10.0.26300-SP0