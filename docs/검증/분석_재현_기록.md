# 최종 정합성 감사 및 재현 실행 기록 (Reproduction & Integrity Log)

- **실행 일시:** 2026-10-29 (KST)
- **작업 디렉터리:** `c:\Users\CDW\1_Project\DataMining`
- **기준 파이프라인 아티팩트:** `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/`
- **재현성 기록이 입증하는 범위 명시:**
  1. **재실행 재현성 (Re-execution Reproducibility):** 동일한 입력 데이터와 설정으로 `analysis/verify_three_analyses.py`를 다시 실행했을 때 생성되는 결과가 기존 검증 CSV 3종(`verification_ols_results.csv`, `verification_correlation_lag_results.csv`, `verification_warning_performance_results.csv`)에 저장된 각 해당 행(`Legacy_*` 행은 Legacy 입력 기준, `Phase56_*` 행은 Phase 5.6 입력 기준)과 부동소수점 오차($< 3.6 \times 10^{-15}$) 이내로 일치함을 입증한다.
  2. **과거(Legacy) 결과와 Phase 5.6 최종 결과의 비동일성:** 본 기록은 과거 분석 결과(`regime_monthly.csv`, 67개월 전체 적합 8국면)와 Phase 5.6 최종 결과(`phase5_6_train_only_regime_monthly.csv`, 48개월 학습 적합 6국면)가 수치적으로 동일함을 뜻하지 않는다. 두 결과는 NMF 적합 표본, 토픽-국면 매핑(`hhdebt`·`trade` 결측 여부), $z$-score 표준화 모수, 시계열 차분/수익률 변환 및 다중검정 보정, 경고 규칙(`z_macro>=0.5 | z_hhdebt>=0.5` vs `z_macro>=0.5` 단독 대체 규칙)의 차이로 인해 수치와 통계적 유의성이 서로 다르다.

## 1. 실행 명령 및 재현 결과 요약

| 단계 ID | 실행 명령 | 사용 스크립트 / 도구 | 입력 데이터 및 경로 | 실행 결과 및 검증 내역 | 성공 여부 | 미해결 문제 및 비고 |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| REP-01 | `Get-Location; git status --short` | `PowerShell / Git` | `c:/Users/CDW/1_Project/DataMining (workspace)` | Active workspace and modified/untracked files confirmed | **SUCCESS (exit code 0)** | 없음 (초기 googlecloudtools.datacloud_telemetry 훅 오류는 환경 복구 후 완전 해소됨) |
| REP-02 | `python -c "import analysis.verify_three_analyses as vta ..." (임시 디렉터리 출력 대조)` | `analysis/verify_three_analyses.py` | `data/processed/panel/monthly_panel.csv; data/processed/regimes/regime_monthly.csv; data/processed/reactions/phase5_6_train_only_regime_monthly.csv` | [재실행 재현성(Re-execution Reproducibility) 검증] 동일 입력·설정에서 스크립트를 재실행한 출력이 기존 검증 CSV 3종(verification_ols_results.csv max diff 3.55e-15, verification_correlation_lag_results.csv max diff 1.11e-16, verification_warning_performance_results.csv max diff 9.71e-17)의 각 해당 행과 부동소수점 오차 이내로 일치함을 확인 (단, CSV 내 Legacy_* 행과 Phase56_* 행 간의 수치는 모델·표본·규칙 차이로 인해 서로 다름) | **SUCCESS (exit code 0)** | 스크립트 재실행 결과와 CSV 3종은 일치하나, 기존 보고서(verification_three_analyses_report.md) 내 일부 수치 오기 및 '과거 수치와 Phase 5.6 수치가 100% 재현'이라는 모호한 문구가 확인되어 최종 보고서(verification_three_analyses_final.md)에서 재실행 재현성과 과거-최종 결과 차이를 분리하여 정정 완료 |
| REP-03 | `Phase 5.6 아티팩트 및 감사 JSON 무결성 대조` | `analysis/validate_strict_oos_forecast_v4.py 산출물 해시 검증` | `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/*; data/processed/reactions/phase5_6_pipeline_audit.json` | forecast CSV (A317C6129E45...), regime CSV (6917D2A9236E...), mapping CSV (426DAAD68F92...), report MD (22C7FBCBDEEA...) SHA-256 해시 100% 일치 및 원본 불변 확인 | **SUCCESS (exit code 0)** | Phase 5.6 학습 기간 NMF에서 hhdebt 및 trade 국면이 독립 토픽으로 분리되지 않아(unrepresented/NaN) H1(AR(2)+News) 및 기존 2국면 결합 경고 규칙의 Strict OOS 평가는 구조적으로 불가능(INSUFFICIENT EVIDENCE). 새로운 모델을 추가하지 않고 현 상태를 정직하게 보고함 |
| REP-04 | `.\.venv\Scripts\python.exe -m analysis.audit_final_verification` | `analysis/audit_final_verification.py` | `monthly_panel.csv; regime_monthly.csv; phase5_6_train_only_regime_monthly.csv; verification_*_results.csv` | verification_final_audit_log.csv, verification_rate_hike_event_table.csv/.md, verification_reproduction_log.csv/.md 생성 및 원본 파일 SHA-256 불변 검증 완료 | **SUCCESS (exit code 0)** | data/raw/ecos/ecos_monthly.csv에 월별 데이터(YYYY-MM-01)만 수록되어 있어 한국은행 금통위의 일별 의결 시각과 일별 뉴스 발생 시각 간 월 내(intra-month) 선후관계는 원시 데이터 범위 내에서 판정 불가(월 단위 t-1, t-2 기준으로만 판정) |

## 2. 원본 산출물 무결성 보존 검증 (SHA-256 해시 대조)

감사 전·후 기존 파일들이 덮어써지거나 변경되지 않았음을 SHA-256 해시로 증명한다.

| 파일명 | 감사 전 SHA-256 | 감사 후 SHA-256 | 보존 판정 |
| :--- | :--- | :--- | :---: |
| `verification_three_analyses_report.md` | `7DE0DC0F47E5E266A719675B215B68DB3086E737BFDE9E401954E6EB34785EAC` | `7DE0DC0F47E5E266A719675B215B68DB3086E737BFDE9E401954E6EB34785EAC` | **PASS (불변)** |
| `verification_ols_results.csv` | `F3343F7E56EC19234DC8BEB351428F72170348928E925B225A4D5A2A1A91E95D` | `F3343F7E56EC19234DC8BEB351428F72170348928E925B225A4D5A2A1A91E95D` | **PASS (불변)** |
| `verification_correlation_lag_results.csv` | `4895A02B891003C84612C8B34E5301C10E901290CCF8B365AEE536DE1FA852C3` | `4895A02B891003C84612C8B34E5301C10E901290CCF8B365AEE536DE1FA852C3` | **PASS (불변)** |
| `verification_warning_performance_results.csv` | `D1F58EB6DACE355C47B04A2656F6D4F50B61A787D2DAB17DF6EBFD6F851E3E06` | `D1F58EB6DACE355C47B04A2656F6D4F50B61A787D2DAB17DF6EBFD6F851E3E06` | **PASS (불변)** |
| `phase5_6_strict_oos_forecast.csv` | `A317C6129E45111C4F54436B9DD6062186F2FC73CDF253A9DEBD49C354A08590` | `A317C6129E45111C4F54436B9DD6062186F2FC73CDF253A9DEBD49C354A08590` | **PASS (불변)** |
| `phase5_6_train_only_regime_monthly.csv` | `6917D2A9236EA938C2519321590BBE066E96D8882AE4B8BB314F46B3E0209850` | `6917D2A9236EA938C2519321590BBE066E96D8882AE4B8BB314F46B3E0209850` | **PASS (불변)** |
| `phase5_6_topic_regime_mapping.csv` | `426DAAD68F92ACA545F1701A00FE30B37204E587D0AFB77F3D4881DC31209E26` | `426DAAD68F92ACA545F1701A00FE30B37204E587D0AFB77F3D4881DC31209E26` | **PASS (불변)** |
| `phase5_6_strict_oos_forecast.md` | `22C7FBCBDEEA2CECA25C7C6F0D56FCB10968C9B0F37BE5505917C2FF102B904A` | `22C7FBCBDEEA2CECA25C7C6F0D56FCB10968C9B0F37BE5505917C2FF102B904A` | **PASS (불변)** |
| `phase5_6_pipeline_audit.json` | `6E6B339BA323C56FE4C5C3CDB8F87F9C55DC58791B0292FC93A849637BE542C6` | `6E6B339BA323C56FE4C5C3CDB8F87F9C55DC58791B0292FC93A849637BE542C6` | **PASS (불변)** |
