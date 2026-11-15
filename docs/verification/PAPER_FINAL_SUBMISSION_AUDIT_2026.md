# JKIICE 2026 국문지 최종 제출본 정합성 감사 보고서 (Final Submission Audit Report)

- **감사 수행일**: 2026-11-02
- **감사 대상 산출물**:
  1. 마크다운 정본: [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md)
  2. 제출용 원문파일 (`.docx`): [`docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx) (69,557 bytes, 147 문단, 8개 표 객체[본문 표 1~4 + 수식 정렬 표 3개 + 저자 약력 표 1개])
  3. 심사용 블라인드 파일 (`.docx`): [`docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx) (68,605 bytes, 141 문단, 7개 표 객체[본문 표 1~4 + 수식 정렬 표 3개])
  4. 생성 스크립트: [`analysis/build_jkiice_2026_submission_docx.py`](file:///c:/Users/CDW/1_Project/DataMining/analysis/build_jkiice_2026_submission_docx.py)
  5. 투고 점검표: [`docs/PAPER_SUBMISSION_CHECKLIST_2026.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_SUBMISSION_CHECKLIST_2026.md)

---

## 1. 작업 1 점검: 최종 원고 내용 동결 (Content Freeze)

- **원칙 준수 여부**: **적합 (100% 준수)**
- 새로운 연구나 추가 통계 분석을 일절 수행하지 않았으며, 기존 검증 완료 아티팩트(`RUN_PHASE5_6_20261027_184959` 및 `data/processed/supplemental_validation/`)에서 확정된 세 가지 실증 축만 사용하였습니다:
  1. **연구 A (RQ1)**: 단일 대표 국면(Argmax / Hurdle Argmax) vs 다중 국면 활성화($z_{d,t} \ge 0.5$) 정보 보존성 비교 ([`single_vs_multi_metrics.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_metrics.csv), [`single_vs_multi_monthly.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_monthly.csv), [`single_vs_multi_regime_combinations.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv))
  2. **Phase 5.6 Strict OOS (RQ2)**: 시장·거시 지표 동행 회귀, 시차 상관, 조기경보 규칙 한계 평가 ([`verification_ols_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/verification_ols_results.csv), [`verification_correlation_lag_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/verification_correlation_lag_results.csv), [`verification_warning_performance_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/verification_warning_performance_results.csv))
  3. **연구 B (RQ3)**: 네이버 데이터랩 주별 상대 검색 지수 1차 차분 교차 검증 및 공통 앵커 민감도 점검 ([`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv), [`news_search_anchor_sensitivity.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_anchor_sensitivity.csv))
  4. **인간 평가 연구 C 제외**: 초록·서론·방법·결과·표에서 완전히 제외되었으며, 5.2절 세 번째 한계 항목에만 기사 단위 인간 라벨링 미수행 사실과 향후 연구 방향을 서술함(후속 연구용 원본 CSV·가이드라인 5종은 삭제하지 않고 그대로 보존함).

---

## 2. 작업 2 점검: 최종 수치·논리 정합성 전수 감사

### 2.1 표 1 ~ 표 4 수치와 초록·본문·결론 일치 여부

| 검증 영역 | 핵심 지표 및 검증 수치 | 국문초록 | 영문초록 | 본문 (3~4장) | 표 (Table 1~4) | 결론 (5장) | 원본 CSV 대조 결과 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **코퍼스 및 분할** | 총 931,709건 (67개월: 학습 48개월[643,095건] + 테스트 19개월[288,614건]), 어휘 22,193개, $K=14$ | 일치 | 일치 | 일치 | 일치 (Table 1, 2) | 일치 | `phase5_6_run_metadata.json` 일치 |
| **표 1 (국면 분포)** | 학습 6대 국면 합계 $45.70\%$, 잔차 $54.30\%$; 활성 신호 총합 **112건** (학습 **89건**, 테스트 **23건**) | 일치 | 일치 | 일치 (4.1절) | 일치 (Table 1) | 일치 (5.1절) | `phase5_6_train_only_regime_monthly.csv` 일치 |
| **표 2 (RQ1: 다중 국면)** | $\ge 2$개 다중 활성 월수: 전체 **$58.21\%$ (39/67)**, 학습 **$66.67\%$ (32/48)**, 테스트 **$36.84\%$ (7/19)** | 일치 | 일치 | 일치 (4.2절) | 일치 (Table 2) | 일치 (5.1절) | `single_vs_multi_metrics.csv` 일치 |
| **표 2 (RQ1: 미표현 신호)** | 단일 대표 국면 제한 시 미표현 신호: 전체 **$43.75\%$ (49/112)**, 학습 **$47.19\%$ (42/89)**, 테스트 **$30.43\%$ (7/23)** | 일치 | 일치 | 일치 (4.2절) | 일치 (Table 2) | 일치 (5.1절) | `single_vs_multi_metrics.csv` 일치 |
| **표 3 (RQ2: HAC OLS)** | 종속변수 `kospi_ret_std` ($N=67$), $R^2 = \mathbf{0.161879}$ ($16.19\%$), $\text{Adj-}R^2 = \mathbf{0.078067}$ ($7.81\%$), $\text{HAC } F = \mathbf{4.6833}$ ($p = \mathbf{0.000573}$) | 일치 | 일치 | 일치 (4.3.1절) | 일치 (Table 3) | 일치 (5.1/5.2절) | `verification_ols_results.csv` 일치 |
| **표 3 (RQ2: 개별 계수)** | `z_macro` ($\beta = -0.7418, p_{\text{raw}} = 0.0004, p_{\text{holm}} = 0.0024$), `z_capital` ($\beta = -0.5299, p_{\text{raw}} = 0.0026, p_{\text{holm}} = 0.0129$) | 일치 | 일치 | 일치 (4.3.1절) | 일치 (Table 3) | 일치 | `verification_ols_results.csv` 일치 |

### 2.2 뉴스-네이버 검색 주별 교차 검증(Table 4) 상관계수 및 HAC·Holm 보정 $p$값 정밀 대조

[`news_search_hac_results.csv`](file:///c:/Users/CDW/1_Project/DataMining/data/processed/supplemental_validation/news_search_hac_results.csv) 원본과 마크다운([`PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md)) 및 Word 제출본([`PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx), [`PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx))의 국문초록, 영문초록, 표 4, 4.4절 본문, 5.1절 결론 5개 위치를 전수 대조한 결과는 다음과 같습니다:

| 매칭 쌍 (`pair_label`, $h=0$) | 분석 구간 | 표본 수 ($N$) | 상관계수 ($r$) | HAC 원시 $p$ (`hac_p_raw`) | 24개 검정 HAC Holm 보정 $p$ (`hac_p_holm`) | 초록·표 4·본문·결론 5개 위치 일치 여부 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **금리·물가 뉴스 ↔ 금리 검색** (`macro ↔ search_macro_interest`) | 전체 기간 (`Full`) | 291 | **$+0.5026$** | $5.38 \times 10^{-15}$ | **$1.29 \times 10^{-13}$** | **5개 위치 모두 정확히 병기 및 일치** |
| **시황 뉴스 ↔ 국내증시 검색** (`market ↔ search_market`) | 전체 기간 (`Full`) | 291 | **$+0.4868$** | $4.53 \times 10^{-6}$ | **$9.06 \times 10^{-5}$** | **5개 위치 모두 정확히 병기 및 일치** |
| **금리·물가 뉴스 ↔ 금리+물가 검색** (`macro ↔ search_macro_combined`) | 전체 기간 (`Full`) | 291 | **$+0.3217$** | $2.41 \times 10^{-7}$ | **$5.07 \times 10^{-6}$** | **5개 위치 모두 정확히 병기 및 일치** |
| **기업실적 뉴스 ↔ 기업실적 검색** (`earnings ↔ search_earnings`) | 전체 기간 (`Full`) | 291 | **$+0.2795$** | $1.83 \times 10^{-6}$ | **$3.48 \times 10^{-5}$** | **5개 위치 모두 정확히 병기 및 일치** |
| **시황 뉴스 ↔ 국내증시 검색** (`market ↔ search_market`) | 테스트 구간 (`Eval OOS`) | 82 | **$+0.4984$** | $0.0020$ | **$0.0432$** (유의) | **5개 위치 모두 정확히 병기 및 일치** |
| **기업실적 뉴스 ↔ 기업실적 검색** (`earnings ↔ search_earnings`) | 테스트 구간 (`Eval OOS`) | 82 | **$+0.4718$** | $4.49 \times 10^{-5}$ | **$0.0011$** (유의) | **5개 위치 모두 정확히 병기 및 일치** |
| **금리·물가 뉴스 ↔ 금리 검색** (`macro ↔ search_macro_interest`) | 테스트 구간 (`Eval OOS`) | 82 | **$+0.3397$** | $0.0170$ | **$0.3575$** (보정 후 비유의) | **초록·표 4·4.4절 모두 비유의 명시** |

### 2.3 학습 기간과 테스트 기간 구분, 명칭 일관성, 과장 표현 배제 점검

1. **학습 기간과 테스트 기간 구분**:
   - 월별 분석: 학습 기간 `2021-01 ~ 2024-12` (48개월, 기사 643,095건) vs 표본 외 테스트 기간 `2025-01 ~ 2026-07` (19개월, 기사 288,614건).
   - 조기경보 평가 가능 기간(향후 1~2개월 예측창 $t+1, t+2$ 필요에 따라 마지막 2개월 제외): 전체 평가 가능 65개월(`2021-01 ~ 2026-05`), 테스트 평가 가능 17개월(`2025-01 ~ 2026-05`).
   - 주별 검색 교차 검증: 전체 292개 ISO 주차(`2020-W53 ~ 2026-W31`: 학습 209주, 테스트 83주) 및 구간 내 1차 차분 후 유효 표본 수($h=0$: 학습 $N=208$, 테스트 $N=82$, 전체 $N=291$; $h=\pm 1$: 학습 $N=207$, 테스트 $N=81$, 전체 $N=290$)가 정확히 구분되어 기술됨.
2. **`aichip` 표시 명칭의 일관성**:
   - 마크다운 정본과 Word 제출본 2종 모두에서 국문 표시 명칭이 **`첨단산업(전기차·배터리 중심)`**(총 9회 출현), 영문 표시 명칭이 **`Advanced Industry (EV/Battery-centered)`**로 100% 일관되게 표기되었으며, 코드 식별자 `aichip`에 토픽 12(차량·전기차·배터리 어휘 중심)가 매핑된 이유(`supported_ev_battery_only`)와 의미적 한계가 3.3절, 4.4절, 5.2절에 일관되게 기술됨.
3. **인간 평가(연구 C) 완료 오해 표현 부재 확인**:
   - 본문 및 초록 전체에서 `380건`, `Batch A`, `Batch B`, `Cohen's kappa`, `인간 평가 설계 완료` 등의 문구가 0건임을 확인함.
   - 5.2절 한계 3번에서만 *"본 연구는 비지도 학습으로 도출된 경제 이슈 국면의 의미적 타당성을 독립 평가자의 기사 단위 라벨링을 통해 검증하지 못했다는 한계를 갖는다"*라고 명확히 한계로 기술됨.
4. **예측력·인과성·조기경보 성능 과장 표현 부재 확인**:
   - 다중 국면의 $43.75\%$ 수치는 *"표현상 정보 보존성(Representational Information Preservation)에 관한 결과이며 예측 정확도의 개선을 의미하지 않는다"*고 명시함.
   - 월별 코스피 수익률 회귀($R^2 = 16.19\%$)는 *"67개월 전체 표본에서의 동시점 설명 회귀이며 미래 수익률 예측력을 의미하지 않는다"*고 명시함.
   - 월별 조기경보 규칙은 일반 하락 경고 정밀도가 자연발생률($69.23\%$)을 넘지 못했고, Phase 5.6의 `z_macro >= 0.5` 단독 규칙이 테스트 17개월에서 적중 0건($\text{TP}=0, \text{FP}=1$)이었다는 점을 4.3.2절과 5.2절에 숨김없이 보고함.

---

## 3. 작업 3~4 점검: JKIICE 2026 국문지 양식 적용 및 제출 파일 생성 결과

1. **공식 양식 확보 및 분석**:
   - `https://kiice.org/board/proceedings/article/271327` 공지에서 배포된 `한국정보통신학회_국문지양식2026.zip` 및 `국문지 게재료 산출표(2026).png`를 다운로드하여 [`scratch/kiice_template_2026/`](file:///c:/Users/CDW/1_Project/DataMining/scratch/kiice_template_2026/)에 보존하고, `[일반] 한국정보통신학회논문편집양식_2026.hwp`와 `★★★심사용 파일 편집양식★★★ 반드시 확인.pdf`의 세부 타이포그래피·블라인드 삭제 규정을 추출하였습니다.
2. **생성된 최종 제출용 Word 파일 검증**:
   - [`docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx): 제1면 학회 배너(`JKIICE`), 국·영문 제목, ① 국문 저자명, ② 영문 저자명·직위·소속, 국·영문 요약, 국문 키워드 및 알파벳순 영문 `Keywords :`, ③ 교신저자 각주, Open Access(`pISSN: 2234-4772`), 제1면 직후 Page Break, 본문 `Ⅰ. 서 론` ~ `Ⅴ. 결 론`, `Table 1` ~ `Table 4` 삼선표, 수식 `(1)` ~ `(3)`, 영문 `REFERENCES` `[1]~[16]`, ⑤ 저자 약력 및 사진 입력란까지 완비.
   - [`docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx): 학회 필수 지침(`file_5.pdf`)에 따라 ① 국문 저자명, ② 영문 저자명·소속, ③ 교신저자 각주, ④ 사사, ⑤ 저자 약력 표를 완전히 삭제한 블라인드 심사용 파일.
   - [`docs/PAPER_DRAFT_JKIICE.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.docx): 제출용 원문파일(`PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`)과 동일하게 동기화 완료.
3. **최종 감사 판정**: **JKIICE 2026 국문지 투고 가능 (PASS — 저자 실명·소속·약력 기입 후 즉시 투고 가능)**

