# JKIICE 논문 수치 충돌 해소 및 원본 대조 확정 보고서 (`PAPER_RESULT_RECONCILIATION_20261101.md`)

- **작성 일시:** 2026-11-01
- **작성 목적:** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md), [`docs/PAPER_REVISION_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_REVISION_AUDIT_20261101.md), [`docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md) 및 기존 Phase 5.6 최종 검증 보고서([`verification_three_analyses_final.md`](file:///c:/Users/CDW/1_Project/DataMining/verification_three_analyses_final.md)) 간에 발생한 수치 충돌의 원인을 실제 분석 코드와 CSV 원본 대조를 통해 규명하고, 최종 논문에 사용할 확정 수치를 결정한다.

---

## 1. Phase 5.6 OLS 회귀분석 결과 수치 충돌 해소 (작업 지시 2.1절)

### 1.1 충돌 현상 요약

- **기존 Phase 5.6 최종 검증 결과 ([`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv#L29-L35) 및 현행 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md#L173-L190) 표 3):**
  - $R^2 = 0.161879$ (`16.19%`), $\text{Adjusted } R^2 = 0.078067$ (`7.81%`), Newey-West HAC $F = 4.683257$ (`4.6833`), $p = 0.000573$ (`0.00057254`), $\text{Wald } \chi^2 = 28.099544$
- **직전 감사 보고서 ([`docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md#L194-L202) 5절) 기재 수치:**
  - $R^2 = 0.3712$, $\text{Adjusted } R^2 = 0.3083$, $F = 5.9027$, $p = 0.000073$ (종속변수를 `kospi_ret_sum`으로 표기)

### 1.2 10대 필수 비교 항목 전수 대조표

[`analysis/verify_three_analyses.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/verify_three_analyses.py#L88-L235)와 [`data/processed/reactions/verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv)의 전 행(70행, 9개 모형)을 대조한 결과는 다음과 같다.

| 비교 항목 | ① 기존 Phase 5.6 최종 보고 모형 (`Phase56_StrictOOS_ret_std_67m`) | ② 직전 감사 보고서 5절 기재 수치 (`R² = 0.3712`) | ③ 참고: [`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv) 내 기타 8개 실존 모형 |
| :--- | :--- | :--- | :--- |
| **1. 종속변수** | `kospi_ret_std` (직전 12개월 월간 수익률 표준편차로 정규화한 당월 코스피 로그수익률) | `kospi_ret_sum`으로 기재되었으나, 프로젝트 내 어떤 CSV나 스크립트에도 `kospi_ret_sum` 열은 존재하지 않음 | • `kospi_ret_std` (Legacy 67m, P5.6 Train 48m)<br>• `kospi_ret` (Legacy 67m, P5.6 67m, P5.6 Train 48m)<br>• `kospi_vol12` (Legacy 67m, P5.6 67m, P5.6 Train 48m) |
| **2. 독립변수 및 회귀식** | 상수항(`const`) + Phase 5.6 유효 6개 국면 $z$-score (`z_macro`, `z_realestate`, `z_aichip`, `z_market`, `z_earnings`, `z_capital`) | 6개 국면 $z$-score로 기재되었으나 실제 코드·CSV에 대응 모형 없음 | • Legacy 모형: 8개 국면 $z$-score (`hhdebt`, `trade` 포함)<br>• Phase 5.6 모형: 6개 국면 $z$-score (`hhdebt`, `trade`는 `unrepresented/NaN`으로 제외) |
| **3. 표본 기간 및 표본 수** | `2021-01 ~ 2026-07` (**$N = 67$개월**, $df_{\text{model}}=6, df_{\text{resid}}=60$) | $N=67$로 기재되었으나 실존하지 않는 통계량 | • 전체 기간: $N=67$ (`2021-01~2026-07`)<br>• 학습 기간: $N=48$ (`2021-01~2024-12`) |
| **4. 결측치 처리 방식** | `data.dropna(subset=x_cols + [y_col])` — 유효 6개 국면과 `kospi_ret_std`는 67개월 전 구간 결측치 0건 (완전 관측) | 해당 없음 (미존재) | 모든 9개 모형에서 `dropna` 후 결측 0건 ($N=67$ 또는 $N=48$) |
| **5. 변수 변환 방식** | • 종속변수: $\text{kospi\_ret}_t / \text{kospi\_vol12}_{t-1}$<br>• 독립변수: 학습 48개월(`2021-01~2024-12`) 평균·표준편차(`ddof=1`)로 고정 표준화한 $z_{d,t}$ | 해당 없음 (미존재) | • Legacy: 67개월 전체 평균·표준편차(`ddof=1`) 표준화<br>• Phase 5.6: 학습 48개월 평균·표준편차(`ddof=1`) 고정 표준화 |
| **6. HAC 적용 여부 및 `maxlags`** | `sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})` (Newey-West HAC, Bartlett 커널, `maxlags=3`) | 일반 OLS F 및 DW 통계량 형태로 잘못 기재됨 | 9개 모형 모두 동일하게 `cov_type="HAC", cov_kwds={"maxlags": 3}` 적용 |
| **7. $F$ 통계량의 종류** | Newey-West HAC 견고 결합 검정 통계량 `model.fvalue = 4.683257` ($p = 0.000573$), `wald_statistic = f_val * 6 = 28.099544` | 비실존 수치 ($F = 5.9027$) | • `Legacy_Replication_ret_std`: $R^2=0.2275, F=4.7544$<br>• `Phase56_StrictOOS_ret_67m`: $R^2=0.1103, F=3.0199$<br>• `Phase56_StrictOOS_vol12_67m`: $R^2=0.6276, F=6.9632$ |
| **8. Holm 보정 대상 및 $p$-값 산출** | 상수항(`const`)을 제외한 **6개 국면 회귀계수**의 양측 HAC $z$-검정 원시 $p$-값(`p_value_raw`)에 대해 Holm-Bonferroni 단계적 보정(`holm_bonferroni`) 수행 | 비실존 수치 (`z_macro` `-0.0252`, `z_capital` `+0.0265` 등 부호와 스케일 자체가 실제 데이터와 무관함) | • `z_macro`: $\hat{\beta}=-0.7418$, $p_{\text{raw}}=0.000395$, **$p_{\text{holm}}=0.002371$ (`0.0024`)**<br>• `z_capital`: $\hat{\beta}=-0.5299$, $p_{\text{raw}}=0.002572$, **$p_{\text{holm}}=0.012859$ (`0.0129`)** |
| **9. 실제 계산 스크립트** | [`analysis/verify_three_analyses.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/verify_three_analyses.py#L118-L193) | **존재하지 않음** (코드베이스 전수 검색 확인) | [`analysis/verify_three_analyses.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/verify_three_analyses.py#L95-L160) |
| **10. 근거 CSV** | [`data/processed/reactions/verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv#L29-L35) (29~35행) | **존재하지 않음** | [`data/processed/reactions/verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv#L2-L70) |

### 1.3 판정 및 논문 반영 결론

- **원인 규명:** [`docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md) 5절(194~202행)에 기재된 `R² = 0.3712, Adj. R² = 0.3083, F = 5.9027` 수치는 실제 CSV나 스크립트에 존재하지 않는 **감사 보고서 작성 과정의 오기(Hallucinated/Unverified Audit Entry)**였다.
- **논문 확정 값:** 반면 현행 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 4.3절 표 3(173~190행)과 초록(12행, 21행)에 수록된 수치는 [`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv)(29~35행, `Phase56_StrictOOS_ret_std_67m`)의 실측값(**$R^2 = 16.19\%$, $\text{Adj-}R^2 = 7.81\%$, Newey-West HAC $F = 4.6833, p = 0.000573$, `z_macro` $\hat{\beta} = -0.7418 [p_{\text{raw}}=0.0004, p_{\text{holm}}=0.0024]$, `z_capital` $\hat{\beta} = -0.5299 [p_{\text{raw}}=0.0026, p_{\text{holm}}=0.0129]$**)과 **소수점 넷째 자리까지 100% 일치**한다. 따라서 논문 표 3은 현행 `Phase56_StrictOOS_ret_std_67m` 실측값을 그대로 유지한다.

---

## 2. 조기경보 성능 결과 수치 충돌 해소 (작업 지시 2.2절)

### 2.1 충돌 현상 요약

- **직전 감사 보고서 ([`docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md#L207-L209) 5절 208행) 기재 수치:**
  - 주별 `weekly_agg_all` Recall `57.1%` (`4/7`), 월별 `monthly_macro_only` Recall `14.3%` (`1/7`), Precision `50.0%` (`1/2`), $F_1 = 0.222$, $\text{MCC} = +0.167$.
- **기존 Phase 5.6 최종 검증 결과 ([`verification_warning_performance_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_warning_performance_results.csv) 및 [`verification_three_analyses_final.md`](file:///c:/Users/CDW/1_Project/DataMining/verification_three_analyses_final.md#L130-L187) 3절):**
  - `z_macro >= 0.5` 단독 대체 규칙의 Strict OOS 테스트 기간(17개월, `2025-01~2026-05`) 일반 하락 경고: 경고 1건(`2026-03`) 발생, 실제 하락 적중 0건($TP=0, FP=1, FN=9, TN=7$, Precision `0.0%`, Recall `0.0%`).

### 2.2 조기경보·사건 포착 모형별 평가 기준 전수 비교표

코드베이스 전수 검색 및 [`verification_warning_performance_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_warning_performance_results.csv), [`phase5_6_strict_oos_forecast.md`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_strict_oos_forecast.md), [`verify_three_analyses.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/verify_three_analyses.py#L445-L853) 대조 결과, `weekly_agg_all Recall = 57.1% (4/7)` 및 `Recall = 14.3% (1/7), Precision = 50.0% (1/2)`는 **실제 CSV나 스크립트에 존재하지 않는 감사 보고서 5절의 오기**임이 확인되었다(참고로 `57.1%`라는 수치는 [`phase5_6_strict_oos_forecast.md`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_strict_oos_forecast.md#L107) 107행에서 뉴스 변수가 없는 순수 기준선 `[고정창] AR(2)` 모형의 방향 분류 균형 정확도[Balanced Accuracy `57.1%`]에만 등장한다).

실제 검증 CSV([`verification_warning_performance_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_warning_performance_results.csv))에 존재하는 조기경보 분석의 정확한 구분은 다음과 같다.

| 분석 구분 (`pipeline` / `analysis_type`) | 목표 사건 정의 및 임계값 | 단위 및 예측 지평 | 경고 규칙 및 임계값 | 평가 기간 ($N$) | 혼동행렬 ($TP / FP / FN / TN$) | Precision / Recall / Specificity | $F_1$ / $\text{MCC}$ / 자연발생률 대비 우위 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **1-A. 일반 하락 경고 (원래 2국면 규칙)**<br>`Legacy_Dual_Warning` / `General_Drop_Warning` | 향후 1~2개월 내 코스피 하락 발생<br>($\text{kospi\_ret}_{t+1} < 0\%$ $\lor$ $\text{kospi\_ret}_{t+2} < 0\%$) | 월별 ($t$월 경고 $\rightarrow$ $t+1, t+2$월 2개월 창) | Legacy 8국면 중<br>`z_macro >= 0.5 \| z_hhdebt >= 0.5`<br>*(Phase 5.6에서는 `hhdebt` 결측으로 구성 불가)* | 전체 평가 가능 기간<br>`2021-01 ~ 2026-05`<br>($N=65$개월; 마지막 2개월은 $t+1, t+2$ 미관측으로 제외) | $19 / 9 / 26 / 11$<br>(경고 28개월, 사건창 45개월) | • Precision: **`67.86%`** (`19/28`)<br>• Recall: **`42.22%`** (`19/45`)<br>• Specificity: **`55.00%`** (`11/20`) | • $F_1 = 0.5205$<br>• $\text{MCC} = -0.0260$<br>• 자연발생률(`69.23%`) 대비 **`-1.37%p`** (변별력 없음) |
| **1-B. 일반 하락 경고 (Phase 5.6 전체)**<br>`Phase5.6_StrictOOS_MacroOnly` / `StrictOOS_Full_Drop_Warning` | 향후 1~2개월 내 코스피 하락 발생<br>($\text{kospi\_ret}_{t+1} < 0\%$ $\lor$ $\text{kospi\_ret}_{t+2} < 0\%$) | 월별 ($t+1, t+2$월 2개월 창) | Phase 5.6 대체 규칙<br>`z_macro >= 0.5` 단독<br>(`hhdebt` 미형성 결측에 따른 축소 규칙) | 전체 평가 가능 기간<br>`2021-01 ~ 2026-05`<br>($N=65$개월) | $9 / 4 / 36 / 16$<br>(경고 13개월, 사건창 45개월) | • Precision: **`69.23%`** (`9/13`)<br>• Recall: **`20.00%`** (`9/45`)<br>• Specificity: **`80.00%`** (`16/20`) | • $F_1 = 0.3103$<br>• $\text{MCC} = 0.0000$<br>• 자연발생률(`69.23%`) 대비 **`0.00%p`** |
| **1-C. 일반 하락 경고 (Phase 5.6 학습)**<br>`Phase5.6_StrictOOS_MacroOnly` / `StrictOOS_Train_Drop_Warning` | 향후 1~2개월 내 코스피 하락 발생<br>($\text{kospi\_ret}_{t+1} < 0\%$ $\lor$ $\text{kospi\_ret}_{t+2} < 0\%$) | 월별 ($t+1, t+2$월 2개월 창) | Phase 5.6 대체 규칙<br>`z_macro >= 0.5` 단독 | • 경계 포함 학습: `2021-01~2024-12` ($N=48$)<br>• 순수 학습 완결: `2021-01~2024-10` ($N=46$) | • 48m: $9 / 3 / 27 / 9$<br>• 46m: $9 / 2 / 26 / 9$ | • 48m Precision **`75.00%`**, Recall **`25.00%`**<br>• 46m Precision **`81.82%`**, Recall **`25.71%`** | • 48m: 자연발생률(`75.00%`) 대비 **`0.00%p`**<br>• 46m: 자연발생률(`76.09%`) 대비 **`+5.73%p`** (비유의) |
| **1-D. 일반 하락 경고 (Phase 5.6 테스트 OOS)**<br>`Phase5.6_StrictOOS_MacroOnly` / `StrictOOS_Test_Drop_Warning` | 향후 1~2개월 내 코스피 하락 발생<br>($\text{kospi\_ret}_{t+1} < 0\%$ $\lor$ $\text{kospi\_ret}_{t+2} < 0\%$) | 월별 ($t+1, t+2$월 2개월 창) | Phase 5.6 대체 규칙<br>`z_macro >= 0.5` 단독 | **Strict OOS 테스트 평가 가능 기간**<br>`2025-01 ~ 2026-05`<br>(**$N=17$개월**; 전체 테스트 19개월 중 마지막 2개월 제외) | **$0 / 1 / 9 / 7$**<br>(경고 1개월[`2026-03`], 실제 사건창 9개월) | • Precision: **`0.00%`** (`0/1`)<br>• Recall: **`0.00%`** (`0/9`)<br>• Specificity: **`87.50%`** (`7/8`) | • $F_1 = 0.0000$<br>• $\text{MCC} = -0.2582$<br>• 자연발생률(`52.94%`) 대비 **`-52.94%p`** |
| **2-A. 급락 경고 창 정밀도**<br>`Crash_Warning_Precision_Window` | 향후 1~2개월 내 코스피 급락 발생<br>($\text{kospi\_ret}_{t+1} \le -3.0\%$ $\lor$ $\text{kospi\_ret}_{t+2} \le -3.0\%$) | 월별 ($t+1, t+2$월 2개월 창) | • Legacy 2국면 (`z_macro>=0.5 \| z_hhdebt>=0.5`)<br>• Phase 5.6 `z_macro>=0.5` 단독 | 전체 평가 가능 기간<br>`2021-01 ~ 2026-05`<br>($N=65$개월, 급락창 27개월 [`41.54%`]) | • Legacy: $14 / 14 / 13 / 24$<br>• Phase 5.6: $6 / 7 / 21 / 31$<br>• Phase 5.6 Test(17m): $0 / 1 / 5 / 11$ | • Legacy: Precision **`50.00%`**, Recall **`51.85%`**<br>• P5.6(65m): Precision **`46.15%`**, Recall **`22.22%`**<br>• P5.6 Test(17m): **`0.00%` / `0.00%`** | • Legacy: 자연발생률 대비 **`+8.46%p`**<br>• P5.6(65m): **`+4.62%p`**<br>• P5.6 Test(17m): **`-29.41%p`** |
| **2-B. 급락 사건 재현율**<br>`Crash_Event_Recall` | 당월 코스피 급락 사건<br>($\text{kospi\_ret}_t \le -3.0\%$, 전체 16건: 학습 13건, 테스트 3건) | 월별 사건 기준 (직전 $t-1$ 또는 $t-2$월에 경고 점등 여부) | • Legacy 2국면<br>• Phase 5.6 `z_macro>=0.5` 단독 | 전체 67개월<br>`2021-01 ~ 2026-07`<br>(급락 사건 총 **16건**) | • Legacy: 적중 11건, 미탐지 5건<br>• Phase 5.6: 적중 3건, 미탐지 13건 (테스트 3건 중 0건 적중) | • Legacy 사건 Recall: **`68.75%`** (`11/16`)<br>• Phase 5.6 사건 Recall: **`18.75%`** (`3/16`), 테스트 **`0.00%`** (`0/3`) | `hhdebt` 결측으로 인해 Phase 5.6 단독 규칙에서는 2022년 3건(`2022-06, 09, 12`)만 포착됨 |
| **3. 기준금리 인상 사건 포착**<br>`Rate_Hike_Capture_Full_Sample` | 당월 한국은행 기준금리 인상<br>($\text{base\_rate\_diff}_t > 0$, 총 11건: 학습 10건, 테스트 1건) | 월별 사건 기준 (직전 $t-1$ 또는 $t-2$월에 `z_macro >= 0.5` 점등 여부) | `z_macro >= 0.5` | 전체 67개월<br>`2021-01 ~ 2026-07`<br>(금리 인상 총 **11건**) | 적중 7건(`2022-04~2023-01`), 미탐지 4건(초기 `2021-08, 2021-11, 2022-01` 3건 + 테스트 `2026-07` 1건) | • 전체 사건 Recall: **`63.64%`** (`7/11`)<br>• 연속 인상기(`2022-04~2023-01`): `7/7` (`100%`)<br>• 전환점 첫 인상: **`0.00%`** (`0/4`) | 연속 인상기 내부에서는 직전 인상의 사후 보도($h=-2$)와 차기 인상 사전 경고창이 중첩됨 |

### 2.3 판정 및 논문 반영 결론

- 감사 보고서 5절(208행)에 적혔던 `주별 Recall 57.1%, 월별 Recall 14.3%, Precision 50.0%`는 실존하지 않는 오기이므로 폐기한다.
- 현행 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md)는 과장된 조기경보 주장을 이미 본문에서 배제하고 있으나, 독자의 명확한 이해와 검증 투명성을 위해 4.3절(또는 5.2절 한계)에 **표본 외 예측 및 조기경보 탐색의 한계(원래 2국면 규칙은 Phase 5.6에서 `hhdebt` 미형성으로 표본 외 평가가 불가하며, `z_macro >= 0.5` 단독 대체 규칙은 평가 가능 테스트 기간 17개월[`2025-01~2026-05`]에서 경고 1건[`2026-03`], 적중 0건[$TP=0, FP=1, FN=9, TN=7$]을 기록하여 본 연구가 뉴스 국면 지표를 사전 예측 도구가 아닌 동행 설명 및 교차 검증 지표로 위치시킨 근거)**를 정확한 수치로 명시한다.

---

## 3. 시차 상관의 종속변수 및 수치 확인 (작업 지시 2.3절)

### 3.1 충돌 현상 및 원인 규명

- 직전 감사 보고서([`docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md#L203-L206) 5절 204~206행)는 `verification_correlation_lag_results.csv` 요약으로 `z_macro h=0: r=-0.5204`, `z_macro h=+1: r=-0.3712`, `z_capital h=0: r=+0.4832`를 기재하였다.
- 그러나 [`data/processed/reactions/verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv)(총 249행)를 전수 확인한 결과, 해당 상관계수(`-0.5204`, `-0.3712`, `+0.4832`)는 CSV 내 어느 행에도 존재하지 않는 **감사 보고서 5절의 오기**였다.

### 3.2 실제 [`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv)의 정확한 변수·시차·표본 수·상관계수

[`analysis/verify_three_analyses.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/verify_three_analyses.py#L240-L385)가 산출한 Phase 5.6 월별 시차 상관분석(`Phase5.6_StrictOOS`)의 정확한 사양과 결과는 다음과 같다.

1. **분석 대상 변수:**
   - **뉴스 국면 변수 (6개):** `share_macro`, `share_realestate`, `share_aichip`, `share_market`, `share_earnings`, `share_capital` (학습 48개월 모수로 선형 변환된 `z_*`와 상관계수 $r$은 100% 동일함).
   - **거시·금융 지표 (정상성 확보를 위한 차분/수익률 변환 4개):**
     1. `kospi_ret`: 코스피 월간 로그수익률 ($\%$)
     2. `base_rate_diff`: 한국은행 기준금리 월간 변화폭 ($\Delta \text{BASE\_RATE}_t$, $\%p$)
     3. `ccsi_diff`: 소비자심리지수 월간 변화분 ($\Delta \text{CCSI}_t$, $\text{p}$)
     4. `usdkrw_ret`: 원/달러 환율 월간 로그수익률 ($\%$)
2. **시차($h$) 정의 및 표본 수 (`2021-01 ~ 2026-07`, 총 67개월):**
   - $h = -2$ ($N = 65$): $\text{Corr}(\text{News}_{d,t}, \text{Indicator}_{t-2})$ — 경제지표가 뉴스 국면보다 **2개월 선행**
   - $h = -1$ ($N = 66$): $\text{Corr}(\text{News}_{d,t}, \text{Indicator}_{t-1})$ — 경제지표가 뉴스 국면보다 **1개월 선행**
   - $h = 0$ ($N = 67$): $\text{Corr}(\text{News}_{d,t}, \text{Indicator}_{t})$ — **동월 동행**
   - $h = +1$ ($N = 66$): $\text{Corr}(\text{News}_{d,t}, \text{Indicator}_{t+1})$ — 뉴스 국면이 경제지표보다 **1개월 선행**
   - $h = +2$ ($N = 65$): $\text{Corr}(\text{News}_{d,t}, \text{Indicator}_{t+2})$ — 뉴스 국면이 경제지표보다 **2개월 선행**
3. **다중검정 보정 범위 및 실제 수치:**
   - 6개 국면 $\times$ 4개 지표 $\times$ 5개 시차 = **총 120개 검정 패밀리**에 대해 단일 Holm-Bonferroni 보정을 수행하였다.
   - **`macro` ↔ `kospi_ret` 실제 상관계수 ([`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv#L10-L14) 10~14행):**
     - $h = -2$ ($N=65$): $r = -0.0921$ ($p_{\text{raw}} = 0.4656, p_{\text{holm}} = 1.0000$)
     - $h = -1$ ($N=66$): $r = -0.1774$ ($p_{\text{raw}} = 0.1542, p_{\text{holm}} = 1.0000$)
     - $h = 0$ ($N=67$): $r = -0.1598$ ($p_{\text{raw}} = 0.1965, p_{\text{holm}} = 1.0000$)
     - $h = +1$ ($N=66$): $r = +0.0734$ ($p_{\text{raw}} = 0.5583, p_{\text{holm}} = 1.0000$)
     - $h = +2$ ($N=65$): $r = -0.0150$ ($p_{\text{raw}} = 0.9058, p_{\text{holm}} = 1.0000$)
     - *(참고: `kospi_ret`과의 단일 변수 상관은 120개 검정 Holm 보정 시 전 국면·전 시차에서 $p_{\text{holm}} \ge 0.4304$로 비유의하며, 과거 변동성으로 정규화한 `kospi_ret_std`를 종속변수로 두고 6개 국면을 동시에 통제한 다중회귀[표 3]에서만 `z_macro`[$\hat{\beta}=-0.7418, p_{\text{holm}}=0.0024$]와 `z_capital`[$\hat{\beta}=-0.5299, p_{\text{holm}}=0.0129$]의 당월 동행 설명력이 유의하게 확인된다.)*
   - **120개 검정 중 Holm 보정 후 유의한($p_{\text{holm}} < 0.05$) 유일한 4개 조합 ([`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv#L15-L117) 15, 17, 18, 117행):**
     1. `macro` ↔ `base_rate_diff` ($h = -2, N = 65$): **$r = +0.4886$** ($p_{\text{raw}} = 3.63 \times 10^{-5}$, **$p_{\text{holm}} = 0.0044$**) — 기준금리 변동 2개월 선행 (최대 피크)
     2. `macro` ↔ `base_rate_diff` ($h = +1, N = 66$): **$r = +0.4749$** ($p_{\text{raw}} = 5.60 \times 10^{-5}$, **$p_{\text{holm}} = 0.0067$**) — 금리·물가 뉴스 1개월 선행
     3. `macro` ↔ `base_rate_diff` ($h = 0, N = 67$): **$r = +0.4580$** ($p_{\text{raw}} = 9.74 \times 10^{-5}$, **$p_{\text{holm}} = 0.0115$**) — 동월 동행
     4. `capital` ↔ `base_rate_diff` ($h = 0, N = 67$): **$r = -0.4260$** ($p_{\text{raw}} = 3.25 \times 10^{-4}$, **$p_{\text{holm}} = 0.0380$**) — 동월 동행 (금리 인상 시 자본거래 뉴스 위축)

---

## 4. AI·반도체 국면(`aichip`) 토픽 12 매핑 근거 추적 및 평가 (작업 지시 2.4절)

### 4.1 원본 매핑 규칙 및 세부 그룹 추적

[`api/datalab_keyword_sets.py`](file:///c:/Users/CDW/1_Project/DataMining/api/datalab_keyword_sets.py#L157-L174), [`analysis/validate_strict_oos_forecast_v4.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/validate_strict_oos_forecast_v4.py#L95-L111), [`data/processed/reactions/phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv#L10-L14), [`data/processed/reactions/phase5_6_strict_oos_forecast.md`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_strict_oos_forecast.md#L45-L78)를 추적한 결과는 다음과 같다.

1. **사전 설계 구조 (`KEYWORD_SETS["AI반도체"]`):**
   - [`api/datalab_keyword_sets.py`](file:///c:/Users/CDW/1_Project/DataMining/api/datalab_keyword_sets.py#L157-L174)(157~174행)는 첨단 기술·신산업 대분류인 `"AI반도체"`(`DOMAIN_SPEC["aichip"]`) 산하에 다음 **4개의 세부 그룹( 총 20개 키워드)**을 묶어 정의하였다:
     - `인공지능`: `["인공지능", "챗GPT", "생성형AI", "AI서비스", "LLM"]`
     - `반도체`: `["반도체", "HBM", "메모리반도체", "파운드리", "반도체주가"]`
     - `빅테크인프라`: `["엔비디아", "데이터센터", "클라우드", "빅테크", "슈퍼컴퓨터"]`
     - `전기차배터리`: `["전기차", "이차전지", "배터리", "충전소", "전기차보조금"]`
2. **Phase 5.6 자동 매핑 규칙 (`map_topics` in [`validate_strict_oos_forecast_v4.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/validate_strict_oos_forecast_v4.py#L216-L250)):**
   - 학습 구간 NMF 기저 행렬 $H_{\text{train}}$($14 \times 22,193$)의 각 토픽 $k \in \{0, \dots, 13\}$에 대해 도메인별 사전 매칭 어휘 질량 합(`masses`)을 구한 뒤:
     - 1위 도메인 질량 점유율 `best_share < 0.01` (`MIN_MAP_SHARE`)이면 **`residual`**(잔차),
     - 2위/1위 도메인 질량 비율 `mass_ratio >= 0.90` (`MASS_TIE_RATIO`)이면 **`ambiguous`**(모호·경합),
     - 두 기준을 모두 통과하면 1위 도메인으로 **`assigned`**(할당) 판정한다.
3. **학습 구간 14개 토픽 중 기술·산업 관련 4개 토픽(토픽 8, 9, 11, 12)의 실제 판정 결과 ([`phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv#L10-L14)):**
   - **토픽 8 (반도체·제조·수출):** 상위 단어 `공장, 수출, 중국, 제조, 반도체, 확보, 유럽, 체결, 국가, 소재, 일본, 현지, 진출, 계약, 설비, 해외, 핵심, 달러, 에너지, 장비, 설립, 건설, 부품, 경쟁력, 배터리`. 1위 도메인 `trade`(`0.0139`), 2위 도메인 `aichip`(`0.0132`)으로 **2위/1위 질량비가 `0.9509 >= 0.90`**이어서 **`ambiguous` (미할당)** 처리됨.
   - **토픽 9 (해외 빅테크·글로벌 증시):** 상위 단어 `현지시간, 마켓, 글로벌마켓, 한경, 게재, 정보, 달러, 플랫폼, 해외, CEO, 주가, 경영자, CNBC, 테슬라, 뉴욕, 하락, 블룸버그, 증시, 마감, 애플, 마켓워치, 최고경영자, 비트코인, 머스크, S&P`. 1위 도메인 `aichip`(`0.0115`, 우세 그룹 `빅테크인프라`), 2위 도메인 `market`(`0.0104`)으로 **2위/1위 질량비가 `0.9061 >= 0.90`**이어서 **`ambiguous` (미할당)** 처리됨.
   - **토픽 11 (AI·혁신·스타트업):** 상위 단어 `분야, AI, 협력, 혁신, 인공지능, 구축, 역량, 교육, 스타트업, 프로그램, 참여, 디지털, 전문, 플랫폼, 발굴, 업무, 창업, 육성, 협약, 인재, 데이터, 솔루션, 선정, 공동, 인력`. 1위 도메인 `aichip`(우세 그룹 `인공지능`), 2위 도메인 `trade`로 경합 비율은 `0.0836`으로 매우 낮았으나, 사전 키워드에 영문 `"AI"` 단일 토큰이 포함되지 않고 `"인공지능"` 등 한글 키워드 위주로 구성되어 **1위 도메인 질량 점유율이 `0.0088 < 0.01`로 기준선(`0.01`)에 근소하게 미달하여 `residual` (미할당)** 처리됨.
   - **토픽 12 (전기차·모빌리티·배터리):** 상위 단어 `차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, SUV, 성능, 기아, 충전, 배터리, 전기, 현대자동차, 디자인, 완성, 차종, 장착, 엔진, 하이브리드, 판매량, 운전자, 브랜드, 공개`. 1위 도메인 `aichip`(**`best_share = 0.0125 >= 0.01`**), 2위 도메인 `macro`(`0.0003`, **`mass_ratio = 0.0269 < 0.90`**, 신뢰도 `0.9731`), **우세 세부 그룹 `전기차배터리`**(매칭 상위 어휘: `전기차, 배터리, 충전소, 인공지능, 반도체, 수소전기차`)로 유일하게 **`assigned`** 판정을 받음.
4. **Phase 5.6 파이프라인의 자체 진단 기록 확인:**
   - 실제로 [`validate_strict_oos_forecast_v4.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/validate_strict_oos_forecast_v4.py#L109-L110)(109~110행)와 [`phase5_6_strict_oos_forecast.md`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_strict_oos_forecast.md#L74)(74행)는 이러한 현상을 감지하여 `aichip`의 지원 상태를 일반 `supported`가 아니라 **`supported_ev_battery_only` ("지지 근거가 사전의 전기차배터리 그룹뿐이며 AI·반도체 직접 근거는 아님")**로 명시해 두고 있다.

### 4.2 의미적 일치성 평가 및 논문 반영 방침

1. **사후적 매핑 변경 금지 원칙 준수:**
   - Phase 5.6 Strict OOS 파이프라인의 핵심 원칙은 사전 고정된 매핑 규칙(`MIN_MAP_SHARE = 0.01`, `MASS_TIE_RATIO = 0.90`, `KEYWORD_SETS`)을 결과를 보고 사후적으로 수정하지 않는 것이다. 따라서 원본 매핑이나 아티팩트 CSV는 변경하지 않는다.
2. **명칭 병기 및 한계 명시:**
   - 토픽 12의 실제 상위 키워드는 자동차·전기차·배터리 중심이므로, 논문에서 이를 `(AI, 인공지능, 반도체, 엔비디아, HBM)`으로 적었던 기존 서술은 명백한 사실 오류이다.
   - 따라서 논문 3.3절, 4.1절(표 1), 4.4절(연구 B), 5.2절(한계)에서 다음 세 가지를 투명하게 반영한다:
     1. **3.3절 토픽 12 키워드 정정 및 매핑 메커니즘 설명:** 토픽 12의 실제 상위 단어(`차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, SUV, 기아, 충전, 배터리`)를 정확히 기재하고, 사전 내 `AI반도체` 대분류의 4개 세부 그룹 중 `전기차배터리` 그룹을 통해 할당(`supported_ev_battery_only`)된 반면 순수 AI 토픽(토픽 11, 점유율 `0.88% < 1.0%`)과 반도체·수출 토픽(토픽 8, `trade`와 경합비 `0.951 >= 0.90`)은 임계 규칙에 의해 미할당되었음을 명시한다.
     2. **국면 명칭의 실질 내용 병기:** 논문 내 `aichip` 국면 표기 시 코드 슬러그(`aichip`)와 사전 대분류명(`AI·반도체`)은 유지하되, 실질 포착 내용이 전기차·배터리·모빌리티임을 나타내기 위해 **`AI·반도체(전기차·배터리 중심, aichip)`**로 병기한다.
     3. **연구 B(네이버 검색 교차 검증) 해석과의 연결:** 4.4절에서 `aichip` 뉴스 비중과 네이버 `AI반도체` 검색 지수 간 주별 1차 차분 상관이 비유의($r = +0.0609, \text{HAC } p_{\text{holm}} = 1.000$)하게 나타난 핵심 원인 역시, 뉴스의 `aichip` 할당 토픽(토픽 12)이 전기차·배터리 중심인 반면 검색 지수는 AI·반도체 전반을 포괄하는 **비지도 매핑의 범위 불일치(`supported_ev_battery_only`)**에 기인함을 명확히 설명한다.

