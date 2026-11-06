# JKIICE 논문 게재 경쟁력 강화 통합 마스터 보고서 (Reviewer Readiness Master Report)

- **실행 일시**: 2026-11-06 (`RUN_20261106_161800`)
- **기준 파이프라인**: `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/` (불변 보존)
- **기존 원고 (불변 보존)**: `docs/PAPER_DRAFT_JKIICE.md` (SHA-256: `3671813A54BB88BD0FDBB98C78EC0F36DC37375D77001614E43DA11B81874957`)
- **신규 심사 대비 보강 후보본**: `docs/PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md`

---

## 1. 프로젝트 개요 및 5대 핵심 질문에 대한 실증 해답 요약

본 프로젝트는 한국정보통신학회논문지(JKIICE) 심사위원이 제기할 수 있는 방법론적·통계적·학술적 질문에 대해 실제 데이터와 100% 재현 가능한 실험으로 답하기 위해 수행되었다.

| 핵심 질문 | 수행 연구 및 스크립트 | 핵심 실증 결과 요약 |
| :--- | :--- | :--- |
| **Q1. 왜 NMF를 사용했는가? LDA 등 대안 모델 대비 어떤 장점과 한계가 있는가?** | **연구 A**: `analysis/reviewer_readiness/compare_nmf_lda.py` (`evaluate_topic_quality.py`) | 동일 학습 표본(144,000건)·동일 어휘(22,193개)·내부 검증 표본(48,000건)에서 $K \in \{10, 12, 14, 16\}$ 통제 비교 결과, $K=14$ 기준 **NMF는 $C_v = 0.8258$, $\text{NPMI} = 0.3011$, $\text{TD@20} = 0.9143$(중복도 $0.0857$), 학습 36.1초, 변환 0.14초, 유효 국면 6개 분리**를 달성한 반면, **LDA는 $C_v = 0.7448$, $\text{NPMI} = 0.2233$, $\text{TD@20} = 0.8036$(중복도 $0.1964$), 학습 91.1초, 변환 1.45초, 유효 국면 5개 분리(`market`, `earnings` 미분리)**에 그침. 단, NMF($K=14$) 역시 `hhdebt`와 `trade`를 독립 분리하지 못하는 한계를 가짐. |
| **Q2. 최종 6개 경제 이슈 국면은 초기값이나 학습 표본이 달라져도 안정적으로 재현되는가?** | **연구 B**: `analysis/reviewer_readiness/run_topic_stability.py` | ① **80% 층화 부분표본(115,200건) 10회 반복(`seed=101~110`)**: 기준 $H$ 대비 평균 Cosine 유사도 **$0.8492$** (범위 $0.7682 \sim 0.9808$), Top-10 Jaccard $0.6077$, Weighted Jaccard@20 $0.7525$, 핵심 할당 토픽(`T1, T3, T4, T6, T7, T13`) Cosine **$0.9615 \sim 0.9968$**. ② **초기화 민감도 11회(`nndsvda`, `nndsvdar` 5회, `random` 5회)**: SVD 변형 초기화 평균 Cosine **$0.9888$**, 무작위 초기화 **$0.8671$**. **총 21회 실험 전체(21/21, 100%)에서 기준 6대 유효 국면이 빠짐없이 재현됨.** |
| **Q3. 다중 국면 활성화가 단일 대표 국면 방식보다 실제 경제 분석에서 어떤 정보를 추가로 보존하는가?** | **연구 C**: `analysis/reviewer_readiness/analyze_multi_regime_cases.py` | 전체 67개월 중 다중 활성 39개월(58.21%)에서 단일 방식 제한 시 별도 미표현되는 활성 신호 **49/112건(43.75%)**에 대해, 객관적 규칙으로 자동 선정된 5개 사례 월(`2021-09, 2022-10, 2023-08, 2026-01, 2026-02`)의 실제 코퍼스 기사(`news_corpus.parquet`) 가중치 $s_{i,d}$를 역추적(월평균 재계산 오차 $8.018 \times 10^{-11}$)함. `2022-10` 금리 인상기($z_{\text{macro}}=+1.83$)의 부동산 거래 절벽($z_{\text{realestate}}=+1.45$)과 `2023-08`·`2026-02`(OOS)의 시황·기업실적 복합 활성화 실체를 실제 기사 32건으로 입증함. |
| **Q4. 주별 네이버 검색 교차 검증 결과는 시차 설정, 앵커 선택, 블록 부트스트랩에서도 강건한가?** | **연구 D**: `analysis/reviewer_readiness/verify_search_robustness.py` | ① **HAC `maxlags` $\in \{2, 4, 8\}$**: 전체 기간 4쌍과 테스트 기간 `earnings`($r=+0.4718, p_{\text{holm}} \le 0.0015$)는 전 시차 유의, 테스트 기간 `market`($r=+0.4984$)은 `lag=2`(`0.0339`)·`lag=4`(`0.0432`) 유의 및 `lag=8`(`0.0616`, 원시 $p=0.0027$) 경계선 유의. ② **이동 블록 부트스트랩($L \in \{2, 4, 8\}$주, $B=2,000$)**: 테스트 기간 `market`($[+0.2079, +0.6367]$ at $L=4$)과 `earnings`($[+0.2989, +0.5986]$ at $L=4$) 모두 전 블록 길이에서 95% 신뢰구간이 0을 배제함. ③ **공통 앵커(`'은행'`) 민감도**: $\Delta \text{score}$ 원시 차분 및 앵커 통제 부분회귀 모두 일관되게 유의함. |
| **Q5. Strict OOS 범위, 선행연구 대비 학술적 기여, 심사자 공격 방어 및 한계는 무엇인가?** | **연구 E, F, G**: `audit_strict_oos_claims.py`, `build_literature_matrix.py`, `generate_reviewer_audit.py` | 텍스트 특징 추출의 무누수 Strict OOS(재계산 오차 $1.643 \times 10^{-14}$)와 67개월 표본 내 동시점 회귀($R^2=16.19\%$)를 명확히 분리(연구 E)하고, Crossref 검증 완료된 24개 문헌 및 선행연구 비교 매트릭스로 3대 학술적 기여를 정립(연구 F)하였으며, 심사자 예상 공격 12선에 대한 방어 매트릭스와 3대 한계(사전 예측력 미입증, `aichip` 편중 및 미형성 국면, 인간 라벨링 미수행)를 투명하게 문서화(연구 G)함. |

---

## 2. 실행된 스크립트 및 생성된 전체 산출물 목록

### 2.1 신규 분석 스크립트 (`analysis/reviewer_readiness/`)
1. `analysis/reviewer_readiness/audit_workspace.py` — Phase 1 전수 파일 감사 및 SHA-256 해시 매니페스트 생성 (41개 추적 파일, 누락 0건)
2. `analysis/reviewer_readiness/evaluate_topic_quality.py` — 공용 토픽 응집도($C_v, \text{NPMI}, U_{\text{mass}}$), 다양성($\text{TD@10, TD@20}$), Hungarian 매칭 모듈
3. `analysis/reviewer_readiness/compare_nmf_lda.py` — 연구 A: NMF vs LDA ($K \in \{10, 12, 14, 16\}$) 정량 비교 및 $K=14$ 토픽 정렬
4. `analysis/reviewer_readiness/run_topic_stability.py` — 연구 B: 80% 층화 부분표본 10회 및 초기화 11회(총 21회) 토픽·국면 안정성 실험
5. `analysis/reviewer_readiness/analyze_multi_regime_cases.py` — 연구 C: 다중 국면 5개 대표 사례 월 자동 선정 및 코퍼스 기사(`W` 가중치) 역추적
6. `analysis/reviewer_readiness/verify_search_robustness.py` — 연구 D: 주별 네이버 검색 HAC 시차(`maxlags=2,4,8`) 및 이동 블록 부트스트랩($L=2,4,8, B=2,000$) 검증
7. `analysis/reviewer_readiness/audit_strict_oos_claims.py` — 연구 E: Strict OOS 데이터 누수 감사 및 논문 주장-근거 매트릭스(`C01~C10`) 검증
8. `analysis/reviewer_readiness/build_literature_matrix.py` — 연구 F: Crossref 기반 참고문헌 전수 감사, 선행연구 비교 매트릭스 및 BibTeX 생성
9. `analysis/reviewer_readiness/generate_reviewer_audit.py` — 연구 G: JKIICE 심사자 공격 테스트 및 12대 예상 질문 방어 매트릭스 생성

### 2.2 신규 데이터 및 검증 아티팩트 (`data/processed/reviewer_readiness/RUN_20261106_161800/`)
- **Phase 1**: `workspace_baseline_manifest.csv`, `workspace_environment_spec.json`, `workspace_audit_summary.md`
- **연구 A**: `topic_model_comparison_metrics.csv`, `nmf_topic_terms.csv`, `lda_topic_terms.csv`, `topic_alignment.csv`, `topic_model_comparison_qc.md`, `topic_model_comparison_report.md`, `topic_model_comparison_figures/k_sensitivity_comparison.png`
- **연구 B**: `topic_stability_runs.csv`, `topic_stability_pairwise.csv`, `topic_stability_summary.csv`, `regime_mapping_stability.csv`, `topic_stability_qc.md`, `topic_stability_report.md`, `topic_stability_figures/topic_stability_by_topic.png`
- **연구 C**: `multi_regime_case_manifest.csv`, `multi_regime_case_monthly.csv`, `multi_regime_case_articles.csv`, `single_multi_case_comparison.csv`, `multi_regime_case_qc.md`, `multi_regime_case_report.md`, `multi_regime_case_figures/case_study_z_comparison.png`
- **연구 D**: `news_search_hac_lag_sensitivity.csv`, `news_search_block_bootstrap_ci.csv`, `news_search_anchor_sensitivity_audit.md`, `news_search_robustness_qc.md`, `news_search_robustness_report.md`, `news_search_robustness_figures/eval_oos_bootstrap_ci.png`
- **연구 E**: `strict_oos_data_leakage_audit.csv`, `strict_oos_claim_matrix.csv`, `strict_oos_scope_report.md`
- **연구 F**: `literature_source_audit.csv`, `literature_comparison_matrix.csv`, `verified_references.bib`, `literature_review_2019_2026.md`, `research_gap_and_contribution.md`
- **연구 G**: `reviewer_response_evidence_matrix.csv`, `reviewer_attack_test.md`, `anticipated_reviewer_comments.md`

### 2.3 신규 종합 보고서 및 논문 후보본 (`docs/`)
1. `docs/REVIEWER_READINESS_MASTER_REPORT.md` (본 문서)
2. `docs/NMF_LDA_COMPARISON_REPORT.md`
3. `docs/TOPIC_STABILITY_REPORT.md`
4. `docs/MULTI_REGIME_CASE_STUDY_REPORT.md`
5. `docs/NEWS_SEARCH_ROBUSTNESS_REPORT.md`
6. `docs/STRICT_OOS_SCOPE_AUDIT.md`
7. `docs/LITERATURE_RESEARCH_GAP_REPORT.md`
8. `docs/REVIEWER_ATTACK_TEST.md`
9. `docs/PAPER_REVISION_CHANGELOG.md`
10. `docs/PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md` (신규 심사 대비 보강 후보본)

---

## 3. 논문의 학술적 기여 및 심사 준비도 8대 자문 질문에 대한 냉정한 평가

1. **NMF 선택이 LDA 대비 정당화되는가?**
   - **예(정당화됨).** 동일한 144,000건 학습 표본과 22,193개 어휘에서 수행한 통제 실험(연구 A) 결과, $K=14$ 기준 NMF는 LDA 대비 응집도($C_v = 0.8258$ vs $0.7448$, $\text{NPMI} = 0.3011$ vs $0.2233$)와 어휘 다양성($\text{TD@20} = 0.9143$ vs $0.8036$)이 높고, 특히 LDA가 전 $K$ 구간에서 분리하지 못한 `market`(시황)과 `earnings`(기업실적) 국면을 NMF는 일관되게 분리하며 학습·변환 속도도 2.5~10배 빠르다.
2. **토픽과 6개 국면 매핑은 안정적인가?**
   - **핵심 6대 국면은 매우 안정적이며, 미형성 2개 국면의 경계 특성도 명확히 규명됨.** 80% 층화 부분표본 10회와 초기화 11회 등 총 21회 실험(연구 B)에서 기준 6대 유효 국면은 **21/21회(100%)** 재현되었고, 할당된 8개 토픽 중 6개 토픽(`T1, T3, T4, T6, T7, T13`)은 부분표본 평균 Cosine 유사도 $0.9615 \sim 0.9968$을 기록하였다. 한편 `hhdebt`는 80% 부분표본 10회 중 8회에서 `T2`가 주택담보대출 어휘로 이동하며 추가 분리된 반면 `trade`는 21회 중 20회에서 미형성되어 도메인 분리 경계가 투명하게 설명된다.
3. **다중 국면 활성화가 단순한 정의상의 차이를 넘어 실질적 분석 가치를 가지는가?**
   - **예(정보 표현 관점에서 실질적 가치를 가짐).** 연구 C의 자동 선정 5개 사례 월 및 실제 기사 가중치($W$) 추적 결과, 단일 대표 국면(Argmax) 방식은 `2022-10` 금리 빅스텝 인상기($z_{\text{macro}}=+1.83$)에 동월 동시에 급증한 부동산 거래 절벽·전세 하락 보도($z_{\text{realestate}}=+1.45$)를 누락하며, `2023-08` 및 `2026-02`(OOS)에서도 시황 변동과 상장사 결산 실적 공시의 동시 활성화를 표현하지 못한다. 다만 이는 표현상 정보 보존성이며 예측 성능 개선으로 과장하지 않았다.
4. **주별 네이버 검색 교차 검증은 추가 강건성 검정 후에도 유지되는가?**
   - **예(유지됨).** 연구 D에서 전체 기간 동시점($h=0$) 4쌍과 테스트 기간 `earnings`($r=+0.4718, p_{\text{holm}} \le 0.0015$)는 `maxlags=2, 4, 8` 전 시차와 블록 부트스트랩($L=2, 4, 8$주, $B=2,000$)에서 모두 강건하게 유의하다. 테스트 기간 `market`($r=+0.4984$)은 `maxlags=2`(`0.0339`)·`maxlags=4`(`0.0432`)에서 유의하고 `maxlags=8`(`0.0616`, 원시 $p=0.0027$)에서 경계선 수준이나, 이동 블록 부트스트랩 95% 신뢰구간($[+0.1870, +0.6350] \sim [+0.2202, +0.6353]$)과 공통 앵커 분모 통제 회귀($p_{\text{holm}}=0.0427$)에서는 모두 유의성이 유지된다.
5. **Strict OOS 설계는 어디까지 엄밀하게 성립하는가?**
   - **텍스트 특징 추출 및 주별 검색 교차 검증에서는 100% 엄밀하게 성립하며, 표 3의 월별 수익률 OLS는 'Strict OOS 특징을 사용한 67개월 전체 표본 동시점 회귀'로 경계가 명확히 설정됨(연구 E).** 어휘(22,193개), IDF, NMF $H$, 토픽 매핑, 표준화 모수($\mu_{\text{train}}, \sigma_{\text{train}}$)는 학습 48개월(`2021~2024`)에만 완전 동결되어 테스트 기간 정보 누수가 0건임이 입증되었다.
6. **선행연구 대비 본 연구의 진짜 학술적 기여는 무엇인가?**
   - ① 한국 경제지 93.1만 건에서 학습 고정 Strict OOS NMF 파이프라인의 적합성(vs LDA)과 21회 재현 안정성을 입증한 **방법론적 기여**, ② 단일 대표 국면 제한 시 미표현되는 복합 경제 이슈 신호(43.75%)를 정량화하고 실제 기사 가중치로 검증한 **정보 표현적 기여**, ③ 단위근 추세를 제거한 주별 1차 차분 뉴스 국면과 네이버 검색 지수 간 표본 외 동시점($h=0$) 동조성(`market`, `earnings`)을 HAC·Holm·블록 부트스트랩으로 입증한 **실증적 기여**의 결합이다.
7. **여전히 남는 가장 큰 한계는 무엇인가?**
   - 첫째, **기사 단위 인간 평가(Human Evaluation)의 부재**로 비지도 토픽의 의미 타당성을 독립 평가자 라벨링으로 검증하지 못한 점. 둘째, 비지도 NMF($K=14$)에서 `hhdebt`와 `trade`가 독립 분리되지 못했고 `aichip` 토픽 12가 전기차·배터리 어휘에 편중(`supported_ev_battery_only`)되어 AI·반도체 전반과의 의미적 괴리가 존재하는 점. 셋째, 월별·주별 유의성이 모두 **동시점($h=0$) 동행 관계**에 국한되며 월별 주가 하락 조기경보 규칙은 테스트 기간 적중 0건($TP=0, FP=1$)으로 사전 예측력이 입증되지 않은 점이다.
8. **JKIICE 투고 시 가장 효과적인 논문 포지셔닝은 무엇인가?**
   - 주가·금리 예측(Forecasting)이나 조기경보 시스템으로 포지셔닝하는 것을 지양하고, **"대규모 경제 뉴스 빅데이터의 무누수(Strict OOS) 다중 국면 표현 체계, 토픽 모델 안정성 검증, 그리고 시장 수익률 충격·대중 검색 트렌드와의 동시점 교차 동조성 분석 연구"**로 명확하고 정직하게 포지셔닝하는 것이 심사 방어에 가장 유리하다.

