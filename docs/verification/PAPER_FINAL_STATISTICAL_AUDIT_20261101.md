# JKIICE 논문 개정본 최종 통계·논리 정합성 감사 보고서 (`PAPER_FINAL_STATISTICAL_AUDIT_20261101.md`)

- **감사 일시:** 2026-11-01
- **감사 대상 문서:**
  - [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) (현행 개정 논문 본문, 272행)
  - [`docs/PAPER_REVISION_AUDIT_20261101.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_REVISION_AUDIT_20261101.md) (1차 개정 감사 로그, 68행)
- **대조 기준 아티팩트 및 스크립트:**
  - Phase 5.6 Strict OOS 원본 산출물: [`phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv), [`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv), [`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv), [`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv), [`verification_warning_performance_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_warning_performance_results.csv)
  - 추가 실증 연구 A(다중 국면): [`run_study_a.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_a.py), [`single_vs_multi_metrics.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_metrics.csv), [`single_vs_multi_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_monthly.csv), [`single_vs_multi_regime_combinations.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv)
  - 추가 실증 연구 B(뉴스-검색 교차 검증): [`run_study_b.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_b.py), [`verify_hac_news_search.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_hac_news_search.py), [`news_search_weekly_panel.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_weekly_panel.csv), [`news_search_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_lag_results.csv), [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv), [`verify_anchor_sensitivity.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_anchor_sensitivity.py), [`news_search_anchor_sensitivity.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_anchor_sensitivity.csv)
  - 추가 실증 연구 C(블라인드 평가 설계): [`run_study_c_setup.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_c_setup.py), [`human_annotation_batch_A.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_batch_A.csv), [`human_annotation_batch_B.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_batch_B.csv), [`human_annotation_codebook.md`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_codebook.md), [`human_annotation_join_key.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_join_key.csv), [`human_annotation_sample_manifest.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_sample_manifest.csv)
- **감사 원칙 준수 현황:** 본 감사에서는 원본 데이터, Phase 5.6 아티팩트, 기존 검증 CSV 및 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md)를 일절 수정하지 않고 독립 재계산 및 대조 감사만 수행하였다.

---

## 0. 감사 총평 요약 (Executive Summary)

독립 재계산 및 원본 CSV 전수 대조 결과, 기존 Phase 5.6 회귀/상관/경보 결과(표 3, 4.5절)와 연구 A의 총괄 집계 지표(표 2)는 원본 CSV와 정확히 일치하나, **[`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 본문 및 표 1·표 4에서 학술지 투고 전 반드시 바로잡아야 할 중대한 수치 불일치 4건과 해석·표현 보정 사항 3건**이 확인되었다.

1. **[중대 오류 1 — 표 1 국면별 평균 비중·표준편차·활성 월수 오기 (4.1절, 129~140행)]:**
   - 표 1의 `학습 구간 평균 비중(%)` 열(`29.94`, `6.87`, `4.72`, `2.22`, `1.89`, `1.25`)은 월별 문서 토픽 비중([`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv))이 아니라 토픽-국면 매핑 표([`phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv))의 NMF 단어 행렬($H$) 내 사전 단어 점유율(`best_share`)을 잘못 옮겨 적은 값이다. 또한 국면별 활성 월수(`18/12/6`, `23/20/3` 등)도 실제 월별 데이터(`25/16/9`, `18/16/2` 등)와 불일치한다.
2. **[중대 오류 2 — 토픽 12(`aichip`) 대표 키워드 사실 불일치 (3.3절, 106행)]:**
   - 본문 106행은 `AI·반도체(aichip)`에 할당된 토픽 12의 상위 단어를 `(AI, 인공지능, 반도체, 엔비디아, HBM)`으로 기술하였으나, 실제 [`phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv)에서 토픽 12의 상위 단어는 `차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, SUV, 성능, 기아, 충전, 배터리, 전기`이다(사전 내 `전기차배터리` 세부 그룹을 통해 `aichip`에 매핑됨). 반면 실제 AI 토픽(토픽 11)은 `residual`(`best_share=0.0088 < 0.01`), 반도체·수출 토픽(토픽 8)은 `ambiguous`로 분류되었다.
3. **[중대 오류 3 — 연구 A 동시 출현 국면 쌍 오기 및 '통계적 누락/정보 손실률' 표현 (4.2절, 164~165행 등)]:**
   - 본문 165행은 2022~2023년 긴축기에 `macro;capital` 조합이 빈번히 동시 출현했다고 기술했으나, 실제로는 2022~2023년 중 `macro`와 `capital`이 동시에 활성화된 달은 **0개월**이다(전체 67개월 중 유일한 동시 활성화는 `2024-12`의 `macro;market;capital` 1개월뿐임). 실제 빈번한 2국면 조합은 `market;earnings`(5개월), `aichip;capital`(4개월), `macro;realestate`(3개월, 모두 2022년), `realestate;capital`(3개월), `earnings;capital`(3개월)이다. 또한 `43.75%`를 "통계적으로 누락" 또는 "유효 활성 거시 정보의 절단·누락"으로 서술한 문구는 정확한 조작적 정의("단일 대표 국면 방식으로 표현을 제한할 경우 별도 국면으로 표현되지 않는 활성 국면 신호의 비율")로 수정해야 한다.
4. **[중대 오류 4 — 표 4 시차($h=\pm 1$) 수치 복사 오류 및 테스트 구간 `금리` 검색 유의성 과장 (4.4절, 203~224행 및 초록·결론)]:**
   - 표 4에서 `시황 ↔ 국내증시`의 $h=+1$ 행이 $h=-1$의 상관계수(`-0.2448`, `-0.3461`, `-0.2822`)를 그대로 중복 복사했고, $h=-1$의 괄호 안 $p$-값도 실제 [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) 수치와 다르다.
   - `기업실적 ↔ 기업실적`의 $h=-1$ 및 $h=+1$ 행에는 CSV에 존재하지 않는 임의 수치(`+0.0421`, `-0.1873`, `+0.0125`)가 동일하게 기입되어 있다.
   - `금리·물가 ↔ 금리 검색`($h=0$)은 테스트 구간(`Eval OOS`, $N=82$)에서 $r = +0.3397$, Newey-West HAC 원시 $p = 0.0170$이나 **24개 검정 Holm 보정 후 $\text{HAC } p_{\text{holm}} = 0.3575 > 0.05$**이다. 그럼에도 표 4의 `HAC p_holm` 열에 원시 $p$-값(`0.017*`)을 기입하고 초록·본문·결론에서 테스트 구간에서도 다중검정 보정 후 통계적으로 유의한 것처럼 서술하였다.

---

## 1. 연구 A: 다중 국면 정보 보존성 재검증 결과

### 1.1 원본 파일 및 스크립트 대조 검증

[`analysis/supplemental_validation/run_study_a.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_a.py) 및 [`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv), [`single_vs_multi_metrics.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_metrics.csv), [`single_vs_multi_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_monthly.csv), [`single_vs_multi_regime_combinations.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv)를 독립 재계산하여 다음 8개 항목을 검증하였다.

| 검증 항목 | 검증 정의 및 산출 공식 | 전체 구간 (67개월, `2021-01~2026-07`) | 학습 구간 (48개월, `2021-01~2024-12`) | 테스트 구간 (19개월, `2025-01~2026-07`) | CSV 및 논문 표 2 일치 여부 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **1. 활성 국면 신호 총수** | $\sum_{t} \sum_{d=1}^{6} \mathbb{I}(z_{d,t} \ge 0.5)$ | **112건** (월평균 `1.672`개) | **89건** (월평균 `1.854`개) | **23건** (월평균 `1.211`개) | **100% 일치** |
| **2. 단일 국면 표현 신호 수** | $\sum_{t} \mathbb{I}(\max_d z_{d,t} \ge 0.5)$ | **63건** (월 최대 1개) | **47건** (월 최대 1개) | **16건** (월 최대 1개) | **100% 일치** |
| **3. 별도 미표현 활성 신호 수** | $\sum_{t} \max(0, k_t - 1)$ ($k_t$: 월 활성 국면 수) | **49건** (`112 - 63 = 29×1 + 10×2`) | **42건** (`89 - 47 = 22×1 + 10×2`) | **7건** (`23 - 16 = 7×1 + 0×2`) | **100% 일치** |
| **4. 미표현 활성 신호 비율** | $\text{미표현 신호} / \text{전체 활성 신호}$ | **43.75%** (`49 / 112`) | **47.19%** (`42 / 89`) | **30.43%** (`7 / 23`) | **100% 일치** |
| **5. 월별 활성 국면 수 분포** | $k_t = 0 / 1 / 2 / 3 / \ge 4$개월 수 | `4 / 24 / 29 / 10 / 0`개월 | `1 / 15 / 22 / 10 / 0`개월 | `3 / 9 / 7 / 0 / 0`개월 | **100% 일치** |
| **6. 다중 활성화($k_t \ge 2$) 비율** | $\text{Count}(k_t \ge 2) / T$ | **58.21%** (`39 / 67`개월) | **66.67%** (`32 / 48`개월) | **36.84%** (`7 / 19`개월) | **100% 일치** |
| **7. 무제약 Argmax vs Hurdle Argmax** | $\max_d z_{d,t} < 0.5$인 무활성 달 처리 차이 | 무제약: 67개월 강제 할당 (4개월 과잉 할당)<br>Hurdle: 63개월 할당, **4개월(`5.97%`) `none`** | 무제약: 48개월 할당<br>Hurdle: 47개월 할당, **1개월(`2.08%`, `2021-07`) `none`** | 무제약: 19개월 할당<br>Hurdle: 16개월 할당, **3개월(`15.79%`, `2025-05, 2026-04, 2026-06`) `none`** | **100% 일치** |
| **8. 학습 전용 표준화($z \ge 0.5$) 정합성** | $z_{d,t} = (s_{d,t} - \mu_{d,\text{train}}) / \sigma_{d,\text{train}}$ (`ddof=1`) | 48개월 학습 모수 고정 적용 확인 (최대 오차 `0.00e+00`) | 평균 `0.0000`, 표준편차 `1.0000` (`ddof=1`) | 학습 모수 외삽 적용 (미래 정보 누수 없음) | **100% 일치** |

### 1.2 연구 A 관련 발견된 문제점 및 수정 권고

1. **표 1(4.1절, 129~140행) 국면별 평균 비중·표준편차·활성 월수 수치 오류:**
   - 논문 표 1은 각 국면의 활성 월수 합계가 112건(`18+23+13+19+22+17=112`)이 되도록 작성되었으나, 개별 국면의 활성 월수와 평균·표준편차가 실제 [`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv)와 전혀 다르다.
   - 실제 [`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv)에서 산출된 정확한 국면별 통계량은 다음과 같다(합계: 전체 `18+22+13+25+16+18 = 112건`, 학습 `16+17+12+16+14+14 = 89건`, 테스트 `2+5+1+9+2+4 = 23건`):
     - `부동산 (realestate)`: 학습 평균 **`12.54%`**, 학습 표준편차 **`0.70%p`**, $z \ge 0.5$ 컷오프 **`12.89%`**, 활성 월수 **`18 / 16 / 2`**
     - `자본거래 (capital)`: 학습 평균 **`8.66%`**, 학습 표준편차 **`0.71%p`**, $z \ge 0.5$ 컷오프 **`9.02%`**, 활성 월수 **`22 / 17 / 5`**
     - `금리·물가 (macro)`: 학습 평균 **`6.67%`**, 학습 표준편차 **`1.26%p`**, $z \ge 0.5$ 컷오프 **`7.30%`**, 활성 월수 **`13 / 12 / 1`**
     - `시황 (market)`: 학습 평균 **`6.16%`**, 학습 표준편차 **`0.37%p`**, $z \ge 0.5$ 컷오프 **`6.35%`**, 활성 월수 **`25 / 16 / 9`**
     - `AI·반도체 (aichip)`: 학습 평균 **`6.05%`**, 학습 표준편차 **`0.42%p`**, $z \ge 0.5$ 컷오프 **`6.26%`**, 활성 월수 **`16 / 14 / 2`**
     - `기업실적 (earnings)`: 학습 평균 **`5.63%`**, 학습 표준편차 **`1.13%p`**, $z \ge 0.5$ 컷오프 **`6.19%`**, 활성 월수 **`18 / 14 / 4`**
     - `잔차 비중 (residual)`: 학습 평균 **`54.30%`**, 학습 표준편차 **`1.27%p`**
2. **동시 출현 국면 조합 서술 오류 (4.2절, 165행):**
   - 논문 165행은 *"특히 2022~2023년 고물가·금리 인상 국면에서는 `금리·물가(macro)`와 `자본거래(capital)` 또는 `부동산(realestate)`이 동시에 활성화되는 빈도가 높았으며"*라고 기술하였다.
   - 그러나 [`single_vs_multi_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_monthly.csv) 및 [`single_vs_multi_regime_combinations.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv) 확인 결과, 2022~2023년 중 `macro`와 `capital`이 동시에 활성화된 달은 **단 한 달도 없다(0개월)**. 오히려 금리 인상기에는 IPO·M&A(자본거래)가 위축되어 `macro`와 `capital`은 역(-)의 시계열 추이를 보였다.
   - 실제 2022~2023년 긴축기에 `macro`와 빈번히 동시 활성화된 국면은 **` 부동산(realestate)`**(2022년 중 5개월 동시 활성: 단일 2국면 조합 `macro;realestate` 3개월[`2022-05, 2022-07, 2022-11`] + 3국면 조합 2개월[`2022-06, 2022-10`])과 **`시황(market)`**(2022~2023년 중 5개월 동시 활성: `macro;market` 2개월[`2022-09, 2023-09`] + 3국면 조합 3개월[`2022-06, 2022-10, 2023-08`])이다.
   - 전체 67개월에서 가장 빈번한 2국면 정확 조합은 `market;earnings`(5개월: 학습 3, 테스트 2), `aichip;capital`(4개월: 학습 4), `macro;realestate`(3개월: 학습 3), `realestate;capital`(3개월: 학습 3), `earnings;capital`(3개월: 학습 2, 테스트 1) 순이다.
3. **'통계적으로 누락' / '경제 정보의 43.75% 손실' 표현의 엄밀화 (초록 12행, 1절 35행, 4.2절 164행, 5.1절 245행):**
   - `43.75%(49/112)`는 객관적인 외부 경제 정보의 절대적 손실률이 아니라, **"$z_{d,t} \ge 0.5$ 기준 다중 국면 방식에서 관측된 활성 국면 신호(112건) 중, 월별 단일 대표 국면(1개) 방식으로 표현을 제한할 경우 별도 국면으로 표현되지 않는 활성 국면 신호(49건)의 비율"**이다. 따라서 "통계적으로 누락", "유효 활성 거시 정보의 43.75%를 절단·누락" 등의 표현은 위 정의에 부합하는 서술로 교체해야 한다.

---

## 2. 연구 B: 주별 뉴스-검색 교차 검증 및 HAC 통계 재검증 결과

### 2.1 HAC 회귀모형 사양 및 시차·표본 수 검증

[`analysis/supplemental_validation/run_study_b.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_b.py)와 [`analysis/supplemental_validation/verify_hac_news_search.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_hac_news_search.py)의 코드 및 산출물을 대조한 결과는 다음과 같다.

1. **표본 수(ISO 주차 수) 및 1차 차분 처리:**
   - [`news_search_weekly_panel.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_weekly_panel.csv)는 총 **292개 ISO 주차**(`2020-W53 ~ 2026-W31`)로 구성되며, 학습 구간(`period == "train"`, `2020-W53 ~ 2024-W52`) **209주**, 테스트 구간(`period == "eval"`, `2025-W01 ~ 2026-W31`) **83주**이다.
     - *참고:* `2021-01-01 ~ 2021-01-03`(금~일, 3일간 기사 486건)은 ISO 8601 달력 기준 `2020-W53`으로 부여되어 첫 주차에 포함되었다.
   - [`verify_hac_news_search.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_hac_news_search.py)(38~55행)는 각 구간(`Full`, `Train`, `Eval OOS`)을 먼저 분리한 뒤 구간 내부에서 1차 차분(`diff()`)을 취하므로, 학습-테스트 경계(`2024-W52` $\rightarrow$ `2025-W01`) 간 차분 누수가 발생하지 않는다.
   - 따라서 1차 차분 후 유효 표본 수는 다음과 같다:
     - **동행($h=0$):** 전체 **$N=291$**, 학습 **$N=208$**, 테스트 **$N=82$**
     - **시차($h=\pm 1$):** 전체 **$N=290$**, 학습 **$N=207$**, 테스트 **$N=81$**
2. **시차($h$) 부호의 정확한 정의 ([`run_study_b.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_b.py) 191~194행, [`verify_hac_news_search.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_hac_news_search.py) 46~55행):**
   - $h = 0$: $\text{Corr}(\Delta \text{News}_{r,t}, \Delta \text{Search}_{g,t})$ — **동주(동행) 반응**
   - $h = +1$: $\text{Corr}(\Delta \text{News}_{r,t}, \Delta \text{Search}_{g,t+1})$ (`xv = dx[1:-1], yv = dy[2:]`) — **$t$주 뉴스 변동 $\rightarrow$ $t+1$주 검색 변동 (뉴스 1주 선행)**
   - $h = -1$: $\text{Corr}(\Delta \text{News}_{r,t}, \Delta \text{Search}_{g,t-1})$ (`xv = dx[2:], yv = dy[1:-1]`) — **$t-1$주 검색 변동 $\rightarrow$ $t$주 뉴스 변동 (검색 1주 선행)**
   - 논문 3.6절(121행)의 시차 정의 설명은 코드와 정확히 일치한다.
3. **Newey-West HAC 추정 사양 ([`verify_hac_news_search.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_hac_news_search.py) 68~78행):**
   - 각 구간 내 유효 표본에서 $\Delta x$와 $\Delta y$를 표본 표준편차(`ddof=1`)로 표준화한 $z_x, z_y$에 대해 `sm.OLS(zy, sm.add_constant(zx)).fit(cov_type="HAC", cov_kwds={"maxlags": 4})`를 적합하였다.
   - 두 변수가 모두 `ddof=1`로 표준화되었으므로 OLS 기울기 계수 $\hat{\beta}_1$은 표본 Pearson 상관계수 $r$과 대수적으로 정확히 일치한다($\hat{\beta}_1 \equiv r$). 즉, HAC 보정은 상관계수 $r$ 자체를 바꾸는 것이 아니라, 자기상관·이분산성을 반영한 표준오차(`hac_se`)와 검정통계량 $t_{\text{HAC}} = r / \text{SE}_{\text{HAC}}$ 및 $p$-값을 보정한다.
   - `statsmodels` 기본 옵션이 적용되어 커널은 **Bartlett 커널**(`weights_bartlett`), 시차 절단값은 **`maxlags=4`**(4주), 소표본 보정은 `use_correction=False`, 양측 검정 $p$-값은 정규분포(`use_t=False`) 기준으로 계산되었다.
4. **다중검정 보정(Holm-Bonferroni) 범위:**
   - 각 분석 구간(`Full`, `Train`, `Eval OOS`)별로 **8개 사전 지정 뉴스-검색 쌍 $\times$ 3개 시차($h \in \{-1, 0, +1\}$) = 총 24개 검정 패밀리($M=24$)**에 대해 Holm-Bonferroni 단계적 보정이 적용되었다.

### 2.2 [`news_search_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_lag_results.csv) 대 [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) 전체 8개 쌍 동행($h=0$) 비교표

| 뉴스-검색 매칭 쌍 ($h=0$) | 구간 | $N$ | Pearson $r$ | 일반 Pearson $p_{\text{raw}}$ | 일반 Pearson $p_{\text{holm}}$ (24개) | HAC $\text{SE}$ | HAC $t$ | HAC $p_{\text{raw}}$ | **HAC $p_{\text{holm}}$ (24개)** | HAC Holm $p < 0.05$ 판정 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. 금리·물가 ↔ 금리 검색** | Train | 208 | `+0.5511` | `6.12e-18` | `1.47e-16` | `0.0680` | `+8.1072` | `5.18e-16` | **`1.24e-14`** (`2.57e-13`*) | **유의** |
| | Eval OOS | 82 | `+0.3397` | `0.0018` | `0.0377` | `0.1424` | `+2.3861` | `0.0170` | **`0.3575`** | **비유의 ($>0.05$)** |
| | Full | 291 | `+0.5026` | `5.32e-20` | `1.28e-18` | `0.0628` | `+7.9977` | `1.27e-15` | **`3.04e-14`** (`1.29e-13`*) | **유의** |
| **2. 금리·물가 ↔ 금리+물가 검색** | Train | 208 | `+0.4978` | `2.18e-14` | `4.80e-13` | `0.0672` | `+7.4050` | `1.31e-13` | **`3.29e-11`** | **유의** |
| | Eval OOS | 82 | `+0.2254` | `0.0418` | `0.7939` | `0.1404` | `+1.6056` | `0.1084` | **`1.0000`** | 비유의 |
| | Full | 291 | `+0.3217` | `1.97e-08` | `4.14e-07` | `0.0598` | `+5.3775` | `7.55e-08` | **`5.07e-06`** | **유의** |
| **3. 시황 ↔ 국내증시 검색** | Train | 208 | `+0.6478` | `4.46e-26` | `1.07e-24` | `0.1071` | `+6.0482` | `1.46e-09` | **`1.14e-07`** | **유의** |
| | Eval OOS | 82 | `+0.4984` | `1.89e-06` | `4.54e-05` | `0.1723` | `+2.8935` | `0.0038` | **`0.0432`** | **유의 (양 구간 재현)** |
| | Full | 291 | `+0.4868` | `1.04e-18` | `2.39e-17` | `0.1046` | `+4.6542` | `3.25e-06` | **`9.06e-05`** | **유의** |
| **4. 기업실적 ↔ 기업실적 검색** | Train | 208 | `+0.2160` | `0.0017` | `0.0310` | `0.0626` | `+3.4526` | `0.00056` | **`0.0143`** | **유의** |
| | Eval OOS | 82 | `+0.4718` | `7.54e-06` | `0.00017` | `0.1160` | `+4.0660` | `4.78e-05` | **`0.0011`** | **유의 (양 구간 재현)** |
| | Full | 291 | `+0.2795` | `1.32e-06` | `2.65e-05` | `0.0569` | `+4.9096` | `9.13e-07` | **`3.48e-05`** | **유의** |
| **5. 금리·물가 ↔ 물가 검색** | Train | 208 | `+0.0658` | `0.3452` | `1.0000` | `0.0757` | `+0.8693` | `0.3847` | **`1.0000`** | 비유의 |
| | Eval OOS | 82 | `+0.1355` | `0.2248` | `1.0000` | `0.1112` | `+1.2189` | `0.2229` | **`1.0000`** | 비유의 |
| | Full | 291 | `+0.0776` | `0.1869` | `1.0000` | `0.0669` | `+1.1604` | `0.2459` | **`1.0000`** | 비유의 |
| **6. 부동산 ↔ 부동산 검색** | Train | 208 | `+0.1288` | `0.0638` | `0.8926` | `0.0793` | `+1.6248` | `0.1042` | **`1.0000`** | 비유의 |
| | Eval OOS | 82 | `-0.0768` | `0.4926` | `1.0000` | `0.1292` | `-0.5948` | `0.5520` | **`1.0000`** | 비유의 |
| | Full | 291 | `+0.1008` | `0.0861` | `1.0000` | `0.0748` | `+1.3471` | `0.1779` | **`1.0000`** | 비유의 |
| **7. AI·반도체 ↔ AI반도체 검색** | Train | 208 | `-0.0357` | `0.6085` | `1.0000` | `0.0537` | `-0.6656` | `0.5056` | **`1.0000`** | 비유의 |
| | Eval OOS | 82 | `+0.1417` | `0.2042` | `1.0000` | `0.1846` | `+0.7675` | `0.4428` | **`1.0000`** | 비유의 |
| | Full | 291 | `+0.0609` | `0.3005` | `1.0000` | `0.1160` | `+0.5250` | `0.5996` | **`1.0000`** | 비유의 |
| **8. 자본거래 ↔ 공모주 검색** | Train | 208 | `+0.1437` | `0.0383` | `0.6132` | `0.0837` | `+1.7176` | `0.0859` | **`1.0000`** | 비유의 |
| | Eval OOS | 82 | `+0.1658` | `0.1366` | `1.0000` | `0.1365` | `+1.2146` | `0.2245` | **`1.0000`** | 비유의 |
| | Full | 291 | `+0.1348` | `0.0214` | `0.3430` | `0.0672` | `+2.0074` | `0.0447` | **`0.9527`** | 비유의 |

> [!IMPORTANT]
> **표 4(4.4절, 203~211행) 및 본문 해석에서 발견된 3가지 핵심 오류:**
> 1. **`시황 ↔ 국내증시`($h=-1, +1$) 수치 오기 (204~205행):** 논문 표 4는 $h=+1$ 행에 $h=-1$의 상관계수(`-0.2448`, `-0.3461`, `-0.2822`)를 중복 기입하였다. 실제 [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv)에서 $h=+1$의 값은 학습 `-0.1338 (1.000)`, 테스트 `+0.0442 (1.000)`, 전체 `-0.0144 (1.000)`이며, $h=-1$의 정확한 `hac_p_holm`은 학습 `-0.2448 (0.178)`, 테스트 `-0.3461 (0.024*)`, 전체 `-0.2822 (0.003**)`이다.
> 2. **`기업실적 ↔ 기업실적`($h=-1, +1$) 미검증 수치 기입 (207~208행):** 논문 표 4는 $h=-1$과 $h=+1$ 모두에 CSV에 존재하지 않는 `+0.0421 (1.000) | -0.1873 (1.000) | +0.0125 (1.000)`을 동일하게 적어 넣었다. 실제 [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) 값은 $h=-1$이 `-0.1654 (0.160) | +0.0444 (1.000) | -0.1160 (0.703)`이고, $h=+1$이 `-0.0638 (1.000) | -0.2033 (1.000) | -0.0968 (1.000)`이다.
> 3. **`금리·물가 ↔ 금리 검색`($h=0$)의 테스트 구간 유의성 과장 (209~211행 및 초록 12·21행, 본문 221행, 결론 247행):** 테스트 구간(`Eval OOS`, $N=82$)에서 `금리·물가 ↔ 금리 검색`($h=0$)은 $r = +0.3397$이며 일반 Pearson 기준으로는 $p_{\text{raw}}=0.0018, p_{\text{holm}}=0.0377$이나, 논문 표 4의 기준인 **Newey-West HAC 보정 기준으로는 원시 $p_{\text{raw}} = 0.0170$, 24개 검정 Holm 보정 $p_{\text{holm}} = 0.3575 > 0.05$**이다. 표 4에서 `HAC p_holm` 열에 원시 $p$-값(`0.017*`)을 혼입하여 유의한 것으로 표기한 것은 통계 보고 원칙 위반이므로, **학습 및 전체 구간에서 HAC Holm 보정 후에도 강건하게 유의($p_{\text{holm}} < 10^{-12}$)하고 테스트 구간($N=82$)에서는 양(+)의 방향성($r=+0.3397$, $\text{HAC } p_{\text{raw}}=0.0170$)을 유지하나 24개 다중검정 HAC Holm 보정 후에는 유의수준을 충족하지 못함($\text{HAC } p_{\text{holm}}=0.3575$)**으로 정정해야 한다. 즉, 학습과 테스트 양 구간 모두에서 24개 검정 HAC Holm 보정($p_{\text{holm}} < 0.05$)을 통과한 국면 쌍은 **`시황 ↔ 국내증시 검색`**과 **`기업실적 ↔ 기업실적 검색`** 2개이다.

---

## 3. 네이버 데이터랩 공통 분모(`anchor_score`) 영향 감사 결과

### 3.1 `score_rel` 산출 구조 및 공통 분모 확인

[`data/raw/datalab/README.md`](file:///c:/Users/CDW/1_Project/DataMining/data/raw/datalab/README.md), [`datalab_keywords.md`](file:///c:/Users/CDW/1_Project/DataMining/data/raw/datalab/datalab_keywords.md), [`datalab_regime_daily.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/raw/datalab/datalab_regime_daily.csv), [`datalab_sub_daily.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/raw/datalab/datalab_sub_daily.csv)를 확인한 결과:

1. 네이버 데이터랩 API 호출 시 모든 검색어 그룹(7개 국면 그룹 및 28개 세부 그룹)은 고정 기간(`2016-01-01 ~ 2026-07-31`) 동안 **단일 앵커 키워드 `'은행'`**과 1:1로 묶여 호출되었다.
2. 각 일자의 상대 검색지수 `score_rel`은 다음과 같이 계산되었다:
   $$\text{score\_rel}_{g,d} = \frac{\text{score}_{g,d}}{\text{anchor\_score}_{g,d}}$$
3. 모든 그룹이 동일한 `'은행'` 키워드를 분모로 공유하므로, 그룹 간 일별 `anchor_score` 시계열의 상관계수는 **$r = 1.000000$**이다(각 API 호출 내 최대값 $M_g$ 스케일링 상수만 다름).
4. **기존 코드 감사 결과:** [`run_study_b.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_b.py)와 [`verify_hac_news_search.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_hac_news_search.py)는 `score_rel`의 주간 평균에 대해 1차 차분만 수행했을 뿐, **공통 분모 `anchor_score`를 통제하거나 제거한 별도의 민감도 분석을 실행하지 않았다.** 따라서 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 224행의 *"앵커 키워드 변동의 영향을 점검한 결과, 주간 1차 차분 시 앵커 지수의 단기 변동은 전체 추세에 왜곡을 주지 않음을 확인하였다"*라는 문장은 작성 시점 기준 **코드로 뒷받침되지 않은 미검증 서술**이었다.

### 3.2 독립 민감도 검정 실행 결과 ([`verify_anchor_sensitivity.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_anchor_sensitivity.py))

본 감사에서는 각 API 호출이 단일 기간(`2016-01-01 ~ 2026-07-31`) 내 1개 타깃 그룹 + 1개 앵커만 포함하므로 **분자 `score` 자체가 시변 분모(`anchor_score`)로 나누지 않은 해당 그룹의 순수 상대 검색량(그룹별 고정 상수 $100/M_g$ 비례)**이라는 점에 착안하여, 독립 검증 스크립트 [`analysis/supplemental_validation/verify_anchor_sensitivity.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/verify_anchor_sensitivity.py)를 작성·실행하고 [`data/processed/supplemental_validation/news_search_anchor_sensitivity.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_anchor_sensitivity.csv)를 생성하였다.

| 뉴스-검색 매칭 쌍 ($h=0$) | 구간 ($N$) | ① 기존 $\Delta \text{score\_rel}$ $r$ (`HAC p_holm`) | ② **분모 제거 순수 분자 $\Delta \text{score}$ $r$ (`HAC p_holm`)** | ③ **$\Delta \text{anchor}$ 통제 부분회귀 $\hat{\beta}$ (`HAC p_holm`)** | ④ 뉴스-앵커($\Delta \text{news}, \Delta \text{anchor}$) 상관 $r$ (`HAC p_raw`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **금리·물가 ↔ 금리 검색** | Full (291) | `+0.5026` (`1.29e-13`) | **`+0.5290` (`3.95e-16`)** | **`+0.5198` (`3.51e-15`)** | `+0.0994` (`0.144`) |
| | Train (208) | `+0.5511` (`2.57e-13`) | **`+0.5746` (`4.23e-16`)** | **`+0.5706` (`5.54e-15`)** | `+0.1138` (`0.138`) |
| | Eval (82) | `+0.3397` (`0.3575`) | **`+0.3461` (`0.1615`)** | **`+0.3499` (`0.2567`)** | `+0.0548` (`0.712`) |
| **금리·물가 ↔ 금리+물가** | Full (291) | `+0.3217` (`5.07e-06`) | **`+0.3651` (`1.30e-08`)** | **`+0.3468` (`8.49e-07`)** | `+0.0994` (`0.144`) |
| | Train (208) | `+0.4978` (`3.29e-11`) | **`+0.5547` (`8.12e-16`)** | **`+0.5346` (`1.15e-14`)** | `+0.1138` (`0.138`) |
| | Eval (82) | `+0.2254` (`1.0000`) | **`+0.2185` (`1.0000`)** | **`+0.2382` (`1.0000`)** | `+0.0548` (`0.712`) |
| **시황 ↔ 국내증시 검색** | Full (291) | `+0.4868` (`9.06e-05`) | **`+0.5330` (`1.92e-05`)** | **`+0.4775` (`0.00021`)** | `-0.0533` (`0.395`) |
| | Train (208) | `+0.6478` (`1.14e-07`) | **`+0.6605` (`5.84e-08`)** | **`+0.6332` (`1.60e-07`)** | `-0.0645` (`0.452`) |
| | Eval (82) | `+0.4984` (`0.0432`) | **`+0.5355` (`0.0327`)** | **`+0.4916` (`0.0713`)** | `-0.0324` (`0.674`) |
| **기업실적 ↔ 기업실적 검색** | Full (291) | `+0.2795` (`3.48e-05`) | **`+0.3464` (`8.26e-08`)** | **`+0.2951` (`5.97e-06`)** | `+0.0404` (`0.536`) |
| | Train (208) | `+0.2160` (`0.0143`) | **`+0.2864` (`0.00022`)** | **`+0.2374` (`0.0019`)** | `+0.0540` (`0.504`) |
| | Eval (82) | `+0.4718` (`0.0011`) | **`+0.5508` (`0.00016`)** | **`+0.4725` (`0.0047`)** | `+0.0019` (`0.984`) |

- **감사 결론:**
  1. 주간 1차 차분된 공통 분모($\Delta \text{anchor\_score}$, `'은행'`)와 6대 뉴스 국면 비중 1차 차분 간의 상관은 전체 구간($N=291$)에서 모두 비유의하다($|r| \le 0.1122, p_{\text{raw}} \ge 0.097$).
  2. 공통 분모(`anchor_score`)로 나누지 않은 순수 분자($\Delta \text{score}$)를 사용할 경우, 분모 변동 노이즈가 제거되어 **유의한 4개 쌍의 동행 상관계수 $r$이 오히려 $+0.026 \sim +0.079$ 상승**한다(예: 전체 구간 `시황 ↔ 국내증시` $r: +0.4868 \rightarrow +0.5330$, `기업실적 ↔ 기업실적` $r: +0.2795 \rightarrow +0.3464$; 테스트 구간 `기업실적 ↔ 기업실적` $r: +0.4718 \rightarrow +0.5508$).
  3. 따라서 논문 4.4절에는 막연한 서술 대신 위 민감도 검증 수치(순수 분자 $\Delta \text{score}$ 및 $\Delta \text{anchor\_score}$ 통제 결과)를 명시하여 방법론적 방어력을 확보할 것을 권고한다.

---

## 4. 연구 C: 블라인드 인간 평가 설계 감사 결과

[`analysis/supplemental_validation/run_study_c_setup.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/supplemental_validation/run_study_c_setup.py) 및 생성된 5개 파일을 점검한 결과는 다음과 같다.

1. **표본 추출 및 층화 구조 ([`human_annotation_sample_manifest.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_sample_manifest.csv)):**
   - Strict OOS 테스트 기간(`2025-01 ~ 2026-07`, 19개월, 288,614건)에서 난수 시드 `SEED = 20261101`로 **월별 정확히 20건씩 총 380건**(`19 × 20 = 380`)을 층화 무작위 추출하였다.
   - 언론사별 분포는 `한국경제 131건(34.5%)`, `매일경제 128건(33.7%)`, `서울경제 121건(31.8%)`으로 균등하게 배분되었다(월별 20건을 3개 언론사로 나눌 때 `7 + 7 + 6 = 20`건 배분).
2. **블라인드 격리 상태 ([`human_annotation_batch_A.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_batch_A.csv), [`human_annotation_batch_B.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_batch_B.csv), [`human_annotation_join_key.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_join_key.csv)):**
   - 평가자 파일(`batch_A.csv`, `batch_B.csv`)은 `ann_id`(`ANN_0001 ~ ANN_0380`), `date`, `source`, `title`, `keywords` 및 빈 입력 열(`macro, realestate, aichip, market, earnings, capital, other, unclear, notes`)로만 구성되어 있으며, 모델의 NMF 토픽 가중치나 예측 국면 라벨이 **100% 배제(완전 블라인드)**되어 있다. 원본 `article_id`는 [`human_annotation_join_key.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_join_key.csv)에 별도 격리되어 있다.
3. **논문 내 미완료 상태 기술 정합성:**
   - [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 3.7절(123~125행), 4.5절(237행), 5.3절(258행) 모두 인간 평가가 아직 수행되지 않은 설계 단계임을 명시하고 있으며, 가짜 일치도($\kappa$)나 F1 점수를 기재하지 않았다.
4. **향후 평가 수행 전 보완해야 할 설계상 유의점 2가지:**
   - **개별 기사 단위 모델 예측 규칙의 사전 명세 필요:** 본 논문의 다중 국면 활성화 규칙($z_{d,t} \ge 0.5$)은 **월별 집계 비중($s_{d,t}$)**에 정의된 규칙이다. 향후 인간 평가자의 기사 단위 다중 라벨과 모델 예측을 비교할 때는 월별 $z \ge 0.5$를 개별 기사에 그대로 대입할 수 없으므로, 개별 기사 $i$의 NMF 가중치 벡터 $W_{i,1..28}$로부터 국면별 점유율 $s_{i,d} = \sum_{k \in \mathcal{T}_d} W_{i,k} / \sum_{k=1}^{28} W_{i,k}$를 산출한 뒤 어떤 임계값(예: 학습 구간 분포 기반 문서 단위 임계값 또는 상대 비중 기준)으로 단일/다중 국면을 판정할지 평가 전에 사전 확정해야 한다.
   - **코드북(`aichip`)과 Phase 5.6 토픽 12 매핑 간 괴리:** [`human_annotation_codebook.md`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/human_annotation_codebook.md)(30행)는 `aichip`을 `"인공지능(AI), 메모리/시스템 반도체, HBM, GPU"`로 정의하고 있으나, 실제 Phase 5.6 모델에서 `aichip`으로 매핑된 유일한 토픽인 토픽 12는 전기차·배터리·모빌리티(`차량, 전기차, 모델, 자동차... 배터리`) 토픽이다. 따라서 실제 인간 라벨링 완료 시 `aichip` 국면에서 모델과 인간 라벨 간 불일치가 발생할 구조적 원인이 존재하며, 이를 한계점에 투명하게 기술해야 한다.

---

## 5. 기존 Phase 5.6 회귀·상관·경보 결과와의 일관성 감사

[`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv), [`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv), [`verification_warning_performance_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_warning_performance_results.csv)와 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 표 3 및 4.3절·4.5절을 대조한 결과, **모든 수치가 소수점 넷째 자리까지 100% 일치함**을 확인하였다.

1. **표 3 다중회귀분석 (`kospi_ret_sum ~ 6개 국면 z-score`, 전체 $N=67$개월):**
   - 모형 적합도: $R^2 = 0.3712$, $\text{Adj. } R^2 = 0.3083$, $F(6, 60) = 5.9027$, 모형 유의확률 $p = 0.000073$ (`7.33e-05`), $\text{DW} = 1.9838$.
   - 개별 회귀계수 및 6개 변수 Holm 보정 $p$-값:
     - `z_macro` (금리·물가): $\hat{\beta} = -0.0252$, $\text{SE} = 0.0067$, $t = -3.7760$, $p_{\text{raw}} = 0.000368$, **$p_{\text{holm}} = 0.0022$** ($95\% \text{ CI } [-0.0385, -0.0118]$) — 유의
     - `z_capital` (자본거래): $\hat{\beta} = +0.0265$, $\text{SE} = 0.0084$, $t = +3.1627$, $p_{\text{raw}} = 0.002452$, **$p_{\text{holm}} = 0.0123$** ($95\% \text{ CI } [+0.0097, +0.0432]$) — 유의
     - `z_aichip` (AI·반도체): $\hat{\beta} = +0.0189$, $\text{SE} = 0.0085$, $t = +2.2266$, $p_{\text{raw}} = 0.029750$, **$p_{\text{holm}} = 0.1190$** — 보정 후 비유의
     - `z_earnings` (기업실적): $\hat{\beta} = -0.0082$, $\text{SE} = 0.0067$, $t = -1.2130$, $p_{\text{raw}} = 0.2299$, **$p_{\text{holm}} = 0.6897$** — 비유의
     - `z_realestate` (부동산): $\hat{\beta} = +0.0033$, $\text{SE} = 0.0079$, $t = +0.4150$, $p_{\text{raw}} = 0.6796$, **$p_{\text{holm}} = 1.0000$** — 비유의
     - `z_market` (시황): $\hat{\beta} = -0.0017$, $\text{SE} = 0.0082$, $t = -0.2030$, $p_{\text{raw}} = 0.8398$, **$p_{\text{holm}} = 1.0000$** — 비유의
   - *참고:* 논문 본문 190행에서 `AI·반도체(aichip)`에 대해 원시 $p=0.0298$이나 Holm 보정 후 $p_{\text{holm}}=0.1190$으로 통계적 유의성을 상실한다고 정직하게 명시한 점은 감사 기준에 완벽히 부합한다.
2. **월별 시차 상관분석 (`verification_correlation_lag_results.csv`, $N=67$개월):**
   - `z_macro` 동행($h=0$): $r = -0.5204$ ($p_{\text{raw}} = 6.32\times 10^{-6}$, 7개 시차 Holm $p_{\text{holm}} = 4.42\times 10^{-5}$)
   - `z_macro` 1개월 선행($h=+1$, `z_macro_t` $\rightarrow$ `kospi_ret_{t+1}`): $r = -0.3712$ ($p_{\text{raw}} = 0.0021$, 7개 시차 Holm $p_{\text{holm}} = 0.0129$)
   - `z_capital` 동행($h=0$): $r = +0.4832$ ($p_{\text{raw}} = 3.39\times 10^{-5}$, 7개 시차 Holm $p_{\text{holm}} = 0.0002$)
3. **표본 외(Strict OOS) 조기경보 탐색 (`verification_warning_performance_results.csv`, 테스트 19개월):**
   - 주별 `weekly_agg_all` 기준 Recall `57.1%`(`4/7`: 7대 주요 사건 중 4건 포착), 월별 `monthly_macro_only`(`z_macro >= 0.5`) 기준 Recall `14.3%`(`1/7`), Precision `50.0%`(`1/2`), $F_1 = 0.222$, $\text{MCC} = +0.167$. 논문 4.5절(229~235행)의 서술과 100% 일치한다.

---

## 6. 논문 내 수정 필요 문장 및 표 목록 (Original vs Recommended Replacement)

원본 보호 원칙에 따라 [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md)를 직접 수정하지 않고, 교정이 필요한 정확한 위치와 교체 문안을 아래에 제시한다.

### 6.1 초록 및 서론 (12행, 21행, 35행)

| 위치 | 기존 문장 (Original) | 수정 권고 문장 (Recommended Replacement) | 수정 사유 |
| :--- | :--- | :--- | :--- |
| **초록 (12행)** | `첫째, 전체 67개월 중 58.21%(39개월, 학습 구간 66.67%, 테스트 구간 36.84%)에서 월 2개 이상의 경제 국면이 동시에 활성화되었으며, 월별 최댓값 1개만 선택하는 단일 국면 방식은 전체 활성 국면 신호(112건)의 43.75%(49건)를 통계적으로 누락시켰다. 둘째, 주별 1차 차분 시계열(291주)에 대한 Newey-West HAC 보정 결과, 뉴스 국면 점유율과 네이버 검색량 간에는 시차 없는 동행(h=0) 동조성이 시황(r=+0.4868, p_holm=9.06e-5), 금리(r=+0.5026, p_holm=1.29e-13), 기업실적(r=+0.2795, p_holm=3.48e-5) 국면에서 강건하게 검증되었으며, 학습 구간과 표본 외 테스트 구간 모두에서 통계적 유의성이 재현되었다.` | `첫째, 전체 67개월 중 58.21%(39개월, 학습 구간 66.67%, 테스트 구간 36.84%)에서 월 2개 이상의 경제 국면이 동시에 활성화되었으며, 월별 대표 국면 1개만 선택하는 단일 국면 방식으로 표현을 제한할 경우 다중 국면 방식에서 관측된 전체 활성 국면 신호(112건) 중 43.75%(49건)가 별도 국면으로 표현되지 않았다. 둘째, 주별 1차 차분 시계열(291주)에 대한 Newey-West HAC 및 24개 검정 Holm 보정 결과, 뉴스 국면 점유율과 네이버 검색량 간에는 시차 없는 동행(h=0) 동조성이 전체 구간에서 금리(r=+0.5026, p_holm=1.29e-13), 시황(r=+0.4868, p_holm=9.06e-5), 금리+물가(r=+0.3217, p_holm=5.07e-6), 기업실적(r=+0.2795, p_holm=3.48e-5) 국면에서 강건하게 확인되었으며, 특히 시황(r=+0.4984, p_holm=0.0432)과 기업실적(r=+0.4718, p_holm=0.0011)은 표본 외 테스트 구간(82주)에서도 다중검정 보정 후 통계적 유의성이 재현되었다(금리는 테스트 구간에서 r=+0.3397, HAC 원시 p=0.0170이나 24개 검정 Holm 보정 후 p_holm=0.3575).` | ① `43.75%`의 정확한 정의 반영<br>② 테스트 구간에서 `금리` 검색의 HAC Holm 보정 결과($p_{\text{holm}}=0.3575 > 0.05$) 정확히 구분 |
| **영문 초록 (21행)** | `First, two or more regimes are simultaneously active in 58.21% of all months (39/67 months; 66.67% in training and 36.84% in out-of-sample testing), showing that conventional single-regime (argmax) assignment omits 43.75% (49 of 112) of active regime signals. Second, weekly first-differenced cross-validation (291 weeks) with Newey-West HAC standard errors confirms strong contemporaneous (h=0) co-movement between news regime shares and Naver search interest in market conditions (r=+0.4868, p_holm=9.06e-5), interest rates (r=+0.5026, p_holm=1.29e-13), and corporate earnings (r=+0.2795, p_holm=3.48e-5), consistently replicated across both training and out-of-sample test periods.` | `First, two or more regimes are simultaneously active in 58.21% of all months (39/67 months; 66.67% in training and 36.84% in out-of-sample testing); restricting representation to a single dominant regime per month leaves 43.75% (49 of 112) of active regime signals unrepresented as separate regimes. Second, weekly first-differenced cross-validation (291 weeks) with Newey-West HAC standard errors and 24-test Holm correction confirms strong contemporaneous (h=0) co-movement between news regime shares and Naver search interest in interest rates (r=+0.5026, p_holm=1.29e-13), market conditions (r=+0.4868, p_holm=9.06e-5), combined macro (r=+0.3217, p_holm=5.07e-6), and corporate earnings (r=+0.2795, p_holm=3.48e-5) over the full sample, with market conditions (r=+0.4984, p_holm=0.0432) and corporate earnings (r=+0.4718, p_holm=0.0011) remaining statistically significant after HAC Holm correction in the out-of-sample test period (whereas interest rates show r=+0.3397, raw HAC p=0.0170, p_holm=0.3575).` | 국문 초록과 동일한 정합성 확보 |
| **1.1절 (35행)** | `금리 인상기에 부동산 PF 부실과 반도체 수출 반등이 동시에 진행되는 복합 국면에서, 가장 점수가 높은 단일 토픽 하나만 남기고 나머지 활성 신호를 버리는 방식은 심각한 정보 손실을 초래한다.` | `금리 인상기에 부동산 시장 위축과 기업 실적 변동 등이 동시에 진행되는 복합 국면에서, 가장 점수가 높은 단일 대표 국면 하나만 선택하는 방식은 동시에 활성화된 다른 국면 신호를 별도로 포착하지 못하는 한계를 지닌다.` | 과장된 '심각한 정보 손실' 표현 완화 |

### 6.2 3.3절 토픽 12 설명 (106행) 및 4.1절 표 1 (129~140행)

- **위치 1:** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 3.3절 106행
  - **기존 문장:**
    > `- **AI·반도체 (`aichip`, 1개 토픽):** 토픽 12 (AI, 인공지능, 반도체, 엔비디아, HBM)`
  - **수정 권고 문장:**
    > `- **AI·반도체 (`aichip`, 1개 토픽):** 토픽 12 (차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 배터리, 전기 — 사전 내 '전기차배터리' 세부 그룹을 통해 할당됨; 반면 일반 AI 토픽[토픽 11]은 최소 점유율 미달[`0.88% < 1.0%`]로 잔차 처리되고 반도체·수출 토픽[토픽 8]은 경합 비율 미달로 미할당됨)`
- **위치 2:** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 4.1절 129~140행 (표 1 및 본문 설명)
  - **기존 표 1 (오류):**
    ```markdown
    | 경제 국면 (Slug) | 할당 토픽 수 | 학습 구간 평균 비중 (%) | 학습 구간 표준편차 (%p) | 활성화 임계 비중 ($z \ge 0.5$, %) | 전체 67개월 중 활성 월수 (학습 / 테스트) |
    | :--- | :---: | :---: | :---: | :---: | :---: |
    | **시황 (`market`)** | 2 | 29.94 | 2.15 | 31.01 | 18개월 (12 / 6) |
    | **부동산 (`realestate`)** | 3 | 6.87 | 0.57 | 7.15 | 23개월 (20 / 3) |
    | **금리·물가 (`macro`)** | 2 | 4.72 | 1.18 | 5.31 | 13개월 (12 / 1) |
    | **자본거래 (`capital`)** | 2 | 2.22 | 0.35 | 2.40 | 19개월 (14 / 5) |
    | **기업실적 (`earnings`)** | 1 | 1.89 | 0.38 | 2.08 | 22개월 (18 / 4) |
    | **AI·반도체 (`aichip`)** | 1 | 1.25 | 0.42 | 1.46 | 17개월 (13 / 4) |
    | **잔차 비중 (`residual`)** | 17 | 53.11 | 2.20 | - | - |
    ```
  - **수정 권고 표 1 ([`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv) 검증 완료):**
    ```markdown
    | 경제 국면 (Slug) | 할당 토픽 수 | 학습 구간 평균 비중 (%) | 학습 구간 표준편차 (%p) | 활성화 임계 비중 ($z \ge 0.5$, %) | 전체 67개월 중 활성 월수 (학습 48 / 테스트 19) |
    | :--- | :---: | :---: | :---: | :---: | :---: |
    | **부동산 (`realestate`)** | 3 | 12.54 | 0.70 | 12.89 | 18개월 (16 / 2) |
    | **자본거래 (`capital`)** | 2 | 8.66 | 0.71 | 9.02 | 22개월 (17 / 5) |
    | **금리·물가 (`macro`)** | 2 | 6.67 | 1.26 | 7.30 | 13개월 (12 / 1) |
    | **시황 (`market`)** | 2 | 6.16 | 0.37 | 6.35 | 25개월 (16 / 9) |
    | **AI·반도체 (`aichip`)** | 1 | 6.05 | 0.42 | 6.26 | 16개월 (14 / 2) |
    | **기업실적 (`earnings`)** | 1 | 5.63 | 1.13 | 6.19 | 18개월 (14 / 4) |
    | **잔차 비중 (`residual`)** | 17 | 54.30 | 1.27 | - | - |
    ```
  - **129행 본문 교체 문안:**
    > `11개 할당 토픽이 전체 문서 가중치에서 차지하는 비중의 합은 학습 구간 평균 45.70%이며, 나머지 17개 비할당·모호 토픽이 잔차 비중(residual, 평균 54.30%)을 구성한다. 할당 국면 중에서는 부동산(12.54%, 3개 토픽)과 자본거래(8.66%, 2개 토픽)의 평균 비중이 가장 높고, 활성 월수는 시황(25개월)과 자본거래(22개월)에서 가장 빈번하게 관측되었다.`

### 6.3 4.2절 연구 A 해석 및 동시 출현 조합 (164~165행) 및 5.1절 (245행)

- **위치:** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 4.2절 164~165행
  - **기존 문장:**
    > `2. **단일 국면 방식의 구조적 정보 손실(43.75%):** 전체 67개월 동안 6대 국면에서 $z_{d,t} \ge 0.5$ 임계값을 넘은 활성 신호는 총 112건(학습 89건, 테스트 23건)이다. 그러나 한 달에 가장 강한 대표 국면 1개만 남기는 단일 국면 방식(Argmax 및 Hurdle Argmax)은 최대 63건의 활성 신호만 반영할 수 있으며, 나머지 **49건(43.75%)의 활성 국면 신호는 통계적으로 완전히 누락**된다.`
    > `3. **복합 경제 이슈의 동시 출현 구조:** 특히 2022~2023년 고물가·금리 인상 국면에서는 금리·물가(macro)와 자본거래(capital) 또는 부동산(realestate)이 동시에 활성화되는 빈도가 높았으며, 2024~2025년 구간에서는 시황(market)과 기업실적(earnings), AI·반도체(aichip)와 자본거래(capital)의 동시 활성화가 빈번하게 관측되었다.`
  - **수정 권고 문장:**
    > `2. **단일 대표 국면 표현의 한계(미표현 활성 신호 비율 43.75%):** 전체 67개월 동안 6대 국면에서 $z_{d,t} \ge 0.5$ 임계값을 넘은 활성 국면 신호는 총 112건(학습 89건, 테스트 23건)이다. 한 달에 가장 강한 대표 국면 1개만 선택하는 단일 국면 방식(Argmax 및 Hurdle Argmax)으로 표현을 제한할 경우 활성 월(63개월)당 최대 1개씩 총 63건의 신호만 대표 국면으로 표시되며, 동일 월에 함께 임계값을 넘은 나머지 **49건(43.75%, 학습 47.19%[42/89], 테스트 30.43%[7/23])의 활성 국면 신호는 별도 국면으로 표현되지 않는다.**`
    > `3. **복합 경제 이슈의 동시 출현 구조:** 전체 67개월에서 가장 빈번히 관측된 2국면 조합은 시황+기업실적(market;earnings, 5개월: 학습 3, 테스트 2), AI·반도체+자본거래(aichip;capital, 4개월: 학습 4), 금리·물가+부동산(macro;realestate, 3개월: 학습 3), 부동산+자본거래(realestate;capital, 3개월: 학습 3), 기업실적+자본거래(earnings;capital, 3개월: 학습 2, 테스트 1) 순이다(3국면 동시 활성 월을 포함한 쌍별 동시 출현 빈도는 시황+기업실적 8개월, 금리·물가+시황 6개월, 부동산+시황 6개월, AI·반도체+자본거래 6개월, 금리·물가+부동산 5개월). 특히 2022~2023년 고물가·금리 인상 국면에서는 금리·물가(macro)가 부동산(realestate, 2022년 중 5개월 동시 활성) 및 시황(market, 2022~2023년 중 5개월 동시 활성)과 빈번히 동반 활성화된 반면, 자본거래(capital)와는 동시 활성화된 달이 없었다(0개월).`

### 6.4 4.4절 표 4 및 본문 해석 (201~224행), 5.1절 (247행)

- **위치:** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 4.4절 203~218행 (표 4)
  - **수정 권고 표 4 ([`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) 100% 정합):**
    ```markdown
    | 뉴스 국면 ↔ 네이버 검색 그룹 | 시차 ($h$) | 학습 구간 (`2021~2024`, $N=208$) $r$ (`HAC p_holm`) | 테스트 구간 (`2025~2026`, $N=82$) $r$ (`HAC p_holm`) | 전체 구간 (`2021~2026`, $N=291$) $r$ (`HAC p_holm`) | HAC Holm ($p_{\text{holm}}<0.05$) 판정 |
    | :--- | :---: | :---: | :---: | :---: | :---: |
    | **시황 뉴스 ↔ 국내증시 검색** | **$h = 0$ (동행)** | **+0.6478** (`1.14e-7`***) | **+0.4984** (`0.0432`*) | **+0.4868** (`9.06e-5`***) | **학습·테스트·전체 유의** |
    | | $h = -1$ (검색 선행) | -0.2448 (`0.1783`) | -0.3461 (`0.0244`*) | -0.2822 (`0.0026`**) | 음(-)의 역전 (반작용) |
    | | $h = +1$ (뉴스 선행) | -0.1338 (`1.0000`) | +0.0442 (`1.0000`) | -0.0144 (`1.0000`) | 비유의 |
    | **기업실적 뉴스 ↔ 기업실적 검색** | **$h = 0$ (동행)** | **+0.2160** (`0.0143`*) | **+0.4718** (`0.0011`**) | **+0.2795** (`3.48e-5`***) | **학습·테스트·전체 유의** |
    | | $h = -1$ (검색 선행) | -0.1654 (`0.1603`) | +0.0444 (`1.0000`) | -0.1160 (`0.7033`) | 비유의 |
    | | $h = +1$ (뉴스 선행) | -0.0638 (`1.0000`) | -0.2033 (`1.0000`) | -0.0968 (`1.0000`) | 비유의 |
    | **금리·물가 뉴스 ↔ 금리 검색** | **$h = 0$ (동행)** | **+0.5511** (`2.57e-13`***) | +0.3397 (`0.3575`, 원시 `0.0170`) | **+0.5026** (`1.29e-13`***) | **학습·전체 유의** (테스트 보정 후 비유의) |
    | | $h = -1$ (검색 선행) | -0.2822 (`9.48e-5`***) | -0.2116 (`1.0000`) | -0.2647 (`3.00e-5`***) | 음(-)의 역전 (반작용) |
    | | $h = +1$ (뉴스 선행) | -0.2869 (`2.15e-5`***) | -0.1456 (`1.0000`) | -0.2528 (`4.11e-6`***) | 음(-)의 역전 (반작용) |
    | **금리·물가 뉴스 ↔ 금리+물가 검색** | **$h = 0$ (동행)** | **+0.4978** (`3.29e-11`***) | +0.2254 (`1.0000`) | **+0.3217** (`5.07e-6`***) | **학습·전체 유의** |
    | **금리·물가 뉴스 ↔ 물가 검색** | $h = 0$ (동행) | +0.0658 (`1.0000`) | +0.1355 (`1.0000`) | +0.0776 (`1.0000`) | 비유의 |
    | **자본거래 뉴스 ↔ 공모주 검색** | $h = 0$ (동행) | +0.1437 (`1.0000`) | +0.1658 (`1.0000`) | +0.1348 (`0.9527`) | 비유의 (원시 $p=0.0447$) |
    | **부동산 뉴스 ↔ 부동산 검색** | $h = 0$ (동행) | +0.1288 (`1.0000`) | -0.0768 (`1.0000`) | +0.1008 (`1.0000`) | 비유의 |
    | **AI·반도체 뉴스 ↔ AI반도체 검색** | $h = 0$ (동행) | -0.0357 (`1.0000`) | +0.1417 (`1.0000`) | +0.0609 (`1.0000`) | 비유의 |
    ```
    *(주: 시차 $h=\pm 1$에서는 각 구간 표본 수가 $N=207, 81, 290$주이며, `HAC p_holm`은 각 구간 내 8개 쌍 $\times$ 3개 시차 = 24개 검정에 대한 Holm-Bonferroni 보정 $p$-값임.)*
- **위치:** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 4.4절 221행 및 224행
  - **221행 수정 권고 문안:**
    > `1. **즉각적인 주간 동행 반응($h=0$)과 표본 외 재현성:** 시황(전체 r=+0.4868, p_holm=9.06e-5)과 기업실적(전체 r=+0.2795, p_holm=3.48e-5)은 학습 구간(p_holm=1.14e-7, 0.0143)뿐만 아니라 표본 외 테스트 구간(N=82주)에서도 24개 검정 HAC Holm 보정 후 통계적 유의성이 강건하게 재현되었다(시황 r=+0.4984, p_holm=0.0432; 기업실적 r=+0.4718, p_holm=0.0011). 금리·물가 뉴스와 금리 검색은 학습 구간(r=+0.5511, p_holm=2.57e-13)과 전체 구간(r=+0.5026, p_holm=1.29e-13)에서 가장 강한 동행성을 보였으며, 테스트 구간에서도 양(+)의 상관(r=+0.3397, HAC 원시 p=0.0170, 일반 Pearson p_holm=0.0377)을 유지하였으나 24개 검정에 대한 보수적 HAC Holm 보정 후에는 유의수준을 상회하였다(HAC p_holm=0.3575).`
  - **224행 수정 권고 문안:**
    > `4. **앵커 키워드('은행') 공통 분모 민감도 검증:** 네이버 데이터랩 상대지수(score_rel = score / anchor_score)가 공유하는 분모('은행' 검색량)의 영향 여부를 확인하기 위해 추가 민감도 검정(news_search_anchor_sensitivity.csv)을 수행하였다. 첫째, 주간 1차 차분된 앵커 지수와 6대 뉴스 국면 점유율 간 상관은 전체 구간에서 모두 비유의하였다(|r| <= 0.1122, HAC 원시 p >= 0.097). 둘째, 시변 분모(anchor_score)로 나누지 않은 각 그룹의 순수 분자 변동(Delta score)을 사용한 결과, 분모 노이즈가 제거되어 전체 구간 동행 상관계수가 금리(r=+0.5026 -> +0.5290, p_holm=3.95e-16), 시황(r=+0.4868 -> +0.5330, p_holm=1.92e-5), 금리+물가(r=+0.3217 -> +0.3651, p_holm=1.30e-8), 기업실적(r=+0.2795 -> +0.3464, p_holm=8.26e-8) 모두에서 오히려 상승하였으며, 앵커 변동을 공변량으로 통제한 부분회귀에서도 동일한 유의성이 유지됨을 확인하였다.`

---

## 7. 검증된 주장 vs 제거·보정해야 할 미검증/과장 주장 대조표

| 구분 | 구체적 내용 | 근거 파일 및 통계량 |
| :--- | :--- | :--- |
| **검증된 핵심 주장 (유지 가능)** | **1. 다중 국면 활성화의 보편성:** 전체 67개월 중 `58.21%`(39개월; 학습 `66.67%`, 테스트 `36.84%`)에서 월 2개 이상의 국면이 동시에 활성화되며, 단일 대표 국면 방식은 전체 활성 신호 112건 중 49건(`43.75%`)을 별도 국면으로 표현하지 못한다. | [`single_vs_multi_metrics.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_metrics.csv) |
| **검증된 핵심 주장 (유지 가능)** | **2. 무제약 Argmax의 비활성 달 강제 할당 한계:** 모든 국면이 $z_{d,t} < 0.5$인 4개월(`5.97%`: 학습 1개월, 테스트 3개월)에서도 무제약 Argmax는 인위적으로 대표 국면을 강제 할당하는 반면, Hurdle/다중 국면 방식은 이를 비활성(`none`)으로 구분한다. | [`single_vs_multi_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_monthly.csv) |
| **검증된 핵심 주장 (유지 가능)** | **3. 월별 KOSPI 동행 회귀 및 시차 상관:** 67개월 다중회귀에서 `z_macro`($\hat{\beta}=-0.0252, p_{\text{holm}}=0.0022$)와 `z_capital`($\hat{\beta}=+0.0265, p_{\text{holm}}=0.0123$)만 다중검정 보정 후 유의하며, `z_macro`는 1개월 선행($h=+1$)에서도 $r=-0.3712$($p_{\text{holm}}=0.0129$)의 음(-)의 상관을 보인다. | [`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_ols_results.csv), [`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/verification_correlation_lag_results.csv) |
| **검증된 핵심 주장 (유지 가능)** | **4. 주별 뉴스-검색 동행($h=0$) 반응 및 공통 분모 강건성:** 전체 291주에서 `금리`($r=+0.5026$), `시황`($r=+0.4868$), `금리+물가`($r=+0.3217$), `기업실적`($r=+0.2795$)이 HAC Holm 보정 후 강건하게 유의하며, `시황`과 `기업실적`은 테스트 구간(82주)에서도 HAC Holm $p < 0.05$를 통과한다. 공통 분모(`은행`) 제거 시 상관계수는 오히려 상승한다. | [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv), [`news_search_anchor_sensitivity.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_anchor_sensitivity.csv) |
| **제거·보정 대상 주장 (수정 필수)** | **1. 표 1의 국면별 평균 비중·표준편차·활성 월수:** 단어 사전 매핑 점유율(`best_share`)을 월별 문서 비중으로 오기한 수치 및 임의 배분된 국면별 활성 월수를 실제 [`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv) 값으로 전면 교체해야 함. | [`phase5_6_train_only_regime_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_train_only_regime_monthly.csv) |
| **제거·보정 대상 주장 (수정 필수)** | **2. 토픽 12(`aichip`)가 AI·엔비디아·HBM 키워드로 구성되었다는 서술:** 실제 토픽 12는 전기차·모빌리티·배터리 토픽(`차량, 전기차, 모델... 배터리`)이며, 순수 AI/반도체 토픽(토픽 8, 11)은 미할당·잔차 처리되었음을 정직하게 명시해야 함. | [`phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv) |
| **제거·보정 대상 주장 (수정 필수)** | **3. 2022~2023년 `macro;capital` 빈번 동시 출현 주장:** 2022~2023년 중 `macro`와 `capital`의 동시 활성은 0개월이므로 삭제하고, 실제 동시 활성화된 `macro+realestate`(5개월) 및 `macro+market`(5개월)으로 교정해야 함. | [`single_vs_multi_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_monthly.csv) |
| **제거·보정 대상 주장 (수정 필수)** | **4. 테스트 구간(Eval OOS)에서 `금리` 검색이 HAC 다중검정 보정 후에도 유의하다는 주장 및 표 4의 $h=\pm 1$ 오기:** 테스트 구간 `금리` 검색은 $\text{HAC } p_{\text{raw}}=0.0170$, $\text{HAC } p_{\text{holm}}=0.3575 > 0.05$이므로 보정 후 유의하다고 서술하지 말아야 하며, 표 4의 `시황`/`기업실적` $h=\pm 1$ 오기 수치를 실제 CSV 값으로 교체해야 함. | [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) |

---

## 8. 최종 제출 전 필수 수정 체크리스트 (Pre-Submission Checklist)

- [ ] **체크 1 (표 1 전면 교체):** [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md) 4.1절 표 1(131~140행) 및 129행 본문의 국면별 학습 평균 비중, 표준편차, $z \ge 0.5$ 임계 비중, 활성 월수를 본 감사 보고서 **6.2절의 검증된 표 1**로 교체하였는가?
- [ ] **체크 2 (토픽 12 키워드 정정):** 3.3절 106행의 `토픽 12 (AI, 인공지능, 반도체, 엔비디아, HBM)`를 실제 [`phase5_6_topic_regime_mapping.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/reactions/phase5_6_topic_regime_mapping.csv) 상위 단어(`차량, 전기차, 모델, 자동차... 배터리`) 및 토픽 8·11 미할당 설명으로 정정하였는가?
- [ ] **체크 3 (연구 A 동시 출현 쌍 및 43.75% 표현 정정):** 4.2절 165행에서 2022~2023년 `macro;capital` 동시 출현 문구를 삭제하고 실제 빈번 조합(`market;earnings` 5개월, `aichip;capital` 4개월, `macro;realestate` 3개월 등)으로 수정하였으며, `43.75%`를 "별도 국면으로 표현되지 않는 활성 국면 신호의 비율"로 명확히 서술하였는가?
- [ ] **체크 4 (표 4 수치 교정 및 테스트 구간 `금리` 유의성 구분):** 4.4절 표 4(203~218행)에서 `시황`($h=\pm 1$) 및 `기업실적`($h=\pm 1$)의 오기 수치를 실제 [`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) 수치로 교체하고, 테스트 구간 `금리` 검색($r=+0.3397$, $\text{HAC } p_{\text{raw}}=0.0170$, $\text{HAC } p_{\text{holm}}=0.3575$)을 HAC Holm 보정 후 유의($p_{\text{holm}} < 0.05$)한 국면(`시황`, `기업실적`)과 명확히 구분하여 초록·본문·결론을 수정하였는가?
- [ ] **체크 5 (네이버 데이터랩 공통 분모 민감도 근거 반영):** 4.4절 224행에 본 감사에서 생성한 [`news_search_anchor_sensitivity.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_anchor_sensitivity.csv)의 실증 수치(순수 분자 $\Delta \text{score}$ 사용 시 상관계수 $r$ 상승 및 앵커 통제 부분회귀 결과)를 반영하였는가?
- [ ] **체크 6 (연구 C 개별 문서 예측 규칙 명시):** 3.7절 또는 4.5절에 향후 인간 라벨과 모델 예측을 비교할 때 월별 임계값($z \ge 0.5$)이 아닌 문서 단위 NMF 가중치($W$) 기반 국면 할당 규칙을 사전 명세하여 적용한다는 점을 보완하였는가?

