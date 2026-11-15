# JKIICE 논문 개정 후보본 변경 이력 보고서 (Paper Revision Changelog)

- **작성 일시**: 2026-11-06 (`RUN_20261106_161800`)
- **기준 원고 (보존 대상, 수정 없음)**: `docs/PAPER_DRAFT_JKIICE.md` (SHA-256: `3671813A54BB88BD0FDBB98C78EC0F36DC37375D77001614E43DA11B81874957`)
- **신규 심사 대비 보강 후보본**: `docs/PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md`

---

## 1. 핵심 불변 수치 유지 확인 (100% 보존)

신규 후보본(`docs/PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md`)은 기존 `docs/PAPER_DRAFT_JKIICE.md`의 확정된 핵심 표(Table 1~4)와 모든 기준 통계량을 소수점까지 변경 없이 그대로 유지하였다:
- **코퍼스 및 분할**: 931,709건 (`2021.01~2026.07`, 67개월: 학습 48개월 643,095건 / 테스트 19개월 288,614건), 학습 어휘 22,193개, 적합 표본 144,000건, $K=14$, 6대 유효 국면(`macro, realestate, aichip, market, earnings, capital`) 및 미형성 2개(`hhdebt, trade`).
- **Table 1 (학습 고정 표준화 모수 및 활성 월수)**: 6대 국면 합계 $\mu_{\text{train}} = 45.70\%$, 잔차 $\mu_{\text{train}} = 54.30\%$, 활성 신호 총합 전체 112건(학습 89건 + 테스트 23건).
- **Table 2 (단일 vs 다중 국면 활성화 비교)**: 전체 67개월 중 $\ge 2$개 다중 활성 월수 **39개월(58.21%)** (학습 32개월[66.67%], 테스트 7개월[36.84%]), 단일 국면 제한 시 별도 미표현 활성 신호 **49/112건(43.75%)** (학습 42/89건[47.19%], 테스트 7/23건[30.43%]).
- **Table 3 (`kospi_ret_std` 동행 HAC OLS, $N=67$, `maxlags=3`)**: $R^2 = 16.19\%$ ($\text{Adj-}R^2 = 7.81\%$), HAC $F(6, 60) = 4.6833$ ($p = 0.000573$), `z_macro` $\beta = -0.7418$ ($p_{\text{raw}}=0.0004, p_{\text{holm}}=0.0024$), `z_capital` $\beta = -0.5299$ ($p_{\text{raw}}=0.0026, p_{\text{holm}}=0.0129$).
- **Table 4 (주별 1차 차분 네이버 검색 교차 검증, `maxlags=4`, 24개 검정 Holm 보정)**:
  - 전체 구간($N=291$, $h=0$): 금리 $r = +0.5026$ ($p_{\text{holm}} = 1.29 \times 10^{-13}$), 시황 $r = +0.4868$ ($p_{\text{holm}} = 9.06 \times 10^{-5}$), 금리+물가 $r = +0.3217$ ($p_{\text{holm}} = 5.07 \times 10^{-6}$), 기업실적 $r = +0.2795$ ($p_{\text{holm}} = 3.48 \times 10^{-5}$).
  - 테스트 구간($N=82$, $h=0$): 시황 $r = +0.4984$ ($p_{\text{holm}} = 0.0432$), 기업실적 $r = +0.4718$ ($p_{\text{holm}} = 0.0011$) 유의; 금리 $r = +0.3397$ ($p_{\text{raw}} = 0.0170, p_{\text{holm}} = 0.3575$) 보정 후 비유의.

---

## 2. 장·절별 상세 보강 및 변경 내역

| 장·절 위치 | 변경 유형 | 보강 및 수정 내용 요약 | 근거 실험 및 산출물 |
| :--- | :---: | :--- | :--- |
| **국·영문 요약 (Abstract)** | 실험 근거 보강 | NMF vs LDA($K=14$) 통제 비교 결과($C_v=0.8258$ vs $0.7448$, $\text{TD@20}=0.9143$ vs $0.8036$), 21회 안정성 실험(6대 국면 100% 재현), 5개 대표 사례 월 기사 가중치($W$) 검증, 주별 검색 이동 블록 부트스트랩($L=4, B=2,000$) 95% 신뢰구간 요약 추가 | 연구 A, B, C, D |
| **Ⅰ. 서론** | 문제 제기 및 RQ 구조화 | 기존 문헌의 4대 방법론적 한계(① NMF vs LDA 비교 및 안정성 미검증, ② 단일 국면/지수 축약, ③ 전 기간 일괄 적합에 따른 정보 누수, ④ 주별 차분·HAC·부트스트랩 외부 교차 검증 부재)와 4대 연구 질문(RQ1~RQ4)으로 정교화 | 연구 A~F |
| **Ⅱ. 관련 연구 (2.1~2.4절, Table F-1 신설)** | 선행연구 확장 및 비교표 추가 | 2015~2026년 검증된 국내외 문헌(Seo 2025; Kim & Lee 2026; Shapiro et al. 2022; Glasserman & Mamaysky 2019; O'Callaghan et al. 2015; Egger & Yu 2022; Da et al. 2015; Youk et al. 2026; Cho 2026; Jung et al. 2025; Kim & Hwangbo 2024)을 반영하고 **Table F-1 (선행연구 구조적 비교표)** 신설 | 연구 F (`literature_comparison_matrix.csv`) |
| **Ⅲ. 연구 방법 — 3.2절 (Table A-1 신설)** | NMF vs LDA 정량 비교 추가 | 동일 144,000건 학습 표본·22,193개 어휘·48,000건 내부 검증 표본에서 $K \in \{10, 12, 14, 16\}$ NMF vs LDA 비교표(**Table A-1**) 추가. 왜 NMF가 Coherence, Diversity, `market`/`earnings` 분리, 연산 속도에서 적합한지 실증 제시 | 연구 A (`topic_model_comparison_metrics.csv`) |
| **Ⅲ. 연구 방법 — 3.3절 (Table B-1 신설)** | 토픽·국면 안정성 검증 추가 | 80% 층화 부분표본 10회(`seed=101~110`, 평균 Cosine $0.8492$) 및 초기화 민감도 11회(`nndsvda`, `nndsvdar`, `random`) 총 21회 실험 결과표(**Table B-1**) 추가. 6대 핵심 국면이 21/21회(100%) 재현됨을 입증 | 연구 B (`topic_stability_runs.csv`, `regime_mapping_stability.csv`) |
| **Ⅲ. 연구 방법 — 3.4절 (Table E-1 신설)** | Strict OOS 적용 범위 감사표 추가 | 각 분석 단계별로 학습 기간 고정(Strict OOS) 여부와 전체 표본 회귀 여부를 명확히 구분한 **Table E-1** 신설 (표 3 OLS는 Strict OOS 특징 기반 67개월 표본 내 동시점 설명 회귀임을 명시) | 연구 E (`strict_oos_data_leakage_audit.csv`) |
| **Ⅳ. 실증 결과 — 4.2절 (Table C-1 신설)** | 다중 국면 5대 사례 및 실제 기사 검증 추가 | 객관적 규칙으로 자동 선정된 5개 사례 월(`2021-09, 2022-10, 2023-08, 2026-01, 2026-02`)과 실제 코퍼스 기사(`article_id`)의 국면 가중치 $s_{i,d}$를 제시한 **Table C-1** 신설 | 연구 C (`multi_regime_case_monthly.csv`, `multi_regime_case_articles.csv`) |
| **Ⅳ. 실증 결과 — 4.4절 (Table D-1 신설)** | 주별 검색 HAC 시차 및 블록 부트스트랩 추가 | HAC 시차 `maxlags` $\in \{2, 4, 8\}$ 민감도와 이동 블록 부트스트랩($L \in \{2, 4, 8\}$주, $B=2,000$) 95% 신뢰구간 비교표(**Table D-1**) 추가 (`market` `maxlags=8` 경계선 유의 $p_{\text{holm}}=0.0616$ 투명 보고 포함) | 연구 D (`news_search_hac_lag_sensitivity.csv`, `news_search_block_bootstrap_ci.csv`) |
| **Ⅴ. 결론 (5.1~5.2절)** | 3대 학술적 기여 및 한계 보강 | 방법론적·정보 표현적·실증적 3대 기여를 정량 근거와 함께 정리하고, 5.2절에 동시점 회귀 vs 예측 구분, 미형성 국면(`hhdebt, trade`) 및 `aichip` 의미 편중, 인간 평가 부재의 한계를 명확히 기술 | 연구 E, F, G |
| **참고문헌 (REFERENCES)** | 전수 서지 감사 및 정정 (16건 → 24건) | Crossref 미확인 문헌 2건(`[7] 박성호·정용운 2020`, `[16] 송원호·강규호 2019`) 제거, `[2] Bybee et al. (2024)` 페이지 정정(`3105-3147`), `[7] 김수현 외 (2020)` 서지 정정(`한국경제의 분석 26(1), 1-65`), Crossref 검증 신규 문헌 10건 추가 (총 24건 전수 검증 완료) | 연구 F (`literature_source_audit.csv`, `verified_references.bib`) |

