# 연구 F: 국내외 선행연구(2019~2026 중심) 비교 검증 및 학술적 차별성 보고서

- **검증 일시**: 2026-11-06 (`RUN_20261106_161800`)
- **검증 목적**: 심사위원의 질문인 *'이 연구가 기존 국내외 뉴스 텍스트 마이닝·거시경제·검색 트렌드 연구와 무엇이 다른가? 인용 문헌은 모두 실재하는가?'*에 답하기 위해, Crossref API 및 공식 학술 DB로 검증된 선행연구 비교 매트릭스와 3대 학술적 기여를 확립한다.
- **산출물**:
  - `data/processed/reviewer_readiness/RUN_20261106_161800/literature_source_audit.csv`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/literature_comparison_matrix.csv`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/verified_references.bib`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/literature_review_2019_2026.md`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/research_gap_and_contribution.md`

---

## 1. 기존 참고문헌 전수 서지 감사 및 신규 문헌 검증 (`literature_source_audit.csv`)

> [!IMPORTANT]
> **서지 검증 핵심 발견 사항**:
> 1. 기존 `docs/PAPER_DRAFT_JKIICE.md`의 참고문헌 16건 중 **13건은 Crossref/KCI/BOK에서 실존이 확인**되었으나, `[2]` Bybee et al. (2024)의 페이지 번호(`2947-2993` → Crossref 정식 페이지 **`3105-3147`**), `[6]` 김수현 외 (2020)의 서지사항(`한국경제의 분석` 제26권 제1호, pp. 1-65), `[10]` Truong et al. (2020)의 2저자 성명(`Runge` → **`Oudre`**)에 서지 보정이 필요함을 확인하였다.
> 2. 반면 기존 초안의 `[7]`(`박성호·정용운 2020, 한국데이터정보과학회지`)과 `[16]`(`송원호·강규호 2019, 경제학연구`) 2건은 Crossref DOI 접두사(`10.7465/jkdi`) 및 KCI/DBpia 검색에서 실존이 확인되지 않았다(`UNVERIFIED_NOT_FOUND`). 따라서 새 후보 원고(`docs/PAPER_DRAFT_JKIICE_reviewer_ready_20261106.md`)에서는 미확인 문헌 2건을 완전히 제거하고, Crossref DOI로 100% 검증된 최신 국내외 연구(Seo 2025; Kim & Lee 2026; Shapiro et al. 2022; Glasserman & Mamaysky 2019; O'Callaghan et al. 2015; Egger & Yu 2022; Da et al. 2015; Youk et al. 2026; Cho 2026; Jung et al. 2025; Kim & Hwangbo 2024)로 교체하였다.

| ID | 서지 요약 | 검증 상태 | 검증 출처 / DOI | 개정 후보본 조치 |
| :---: | :--- | :---: | :--- | :--- |
| `ORIG_REF_01` | Baker, S. R., Bloom, N., & Davis, S. J. (2016), QJE, 131(4), 1593-1636 | `VERIFIED_EXACT` | `10.1093/qje/qjw024` | `KEEP_AS_IS` |
| `ORIG_REF_02` | Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024), Journal of Finance, 79(5), 2947-2993 | `VERIFIED_WITH_PAGE_CORRECTION` | `10.1111/jofi.13377` | `UPDATE_PAGES_TO_3105_3147` |
| `ORIG_REF_03` | Thorsrud, L. A. (2020), JBES, 38(2), 393-409 | `VERIFIED_EXACT` | `10.1080/07350015.2018.1506344` | `KEEP_AS_IS` |
| `ORIG_REF_04` | Tetlock, P. C. (2007), Journal of Finance, 62(3), 1139-1168 | `VERIFIED_EXACT` | `10.1111/j.1540-6261.2007.01232.x` | `KEEP_AS_IS` |
| `ORIG_REF_05` | 서범석, 이영환, 조형배 (2022), 기계학습을 이용한 뉴스심리지수(NSI)의 작성과 활용, 국민계정리뷰 2022-1 / BOK 경제연구 2022-15 | `VERIFIED_BOK_AND_SSRN` | `10.2139/ssrn.4230611` | `KEEP_AND_ADD_SEO_2025_IJF` |
| `ORIG_REF_06` | 김수현, 박기영 (2021), 텍스트 분석을 이용한 한국의 경제 심리 및 경기 변동 연구, 금융연구 35(3), 1-35 | `VERIFIED_WITH_METADATA_CORRECTION` | `N/A (KCI: ART002585258 / BOK WP 2019-18)` | `CORRECT_TO_KIM_ET_AL_2020` |
| `ORIG_REF_07` | 박성호, 정용운 (2020), 비정형 뉴스 빅데이터를 활용한 거시경제 지표 선행성 분석, 한국데이터정보과학회지 31(5), 895-909 | `UNVERIFIED_NOT_FOUND` | `NONE` | `REMOVE_AND_REPLACE_WITH_VERIFIED_STUDY` |
| `ORIG_REF_08` | Lee, D. D., & Seung, H. S. (1999), Nature, 401(6755), 788-791 | `VERIFIED_EXACT` | `10.1038/44565` | `KEEP_AS_IS` |
| `ORIG_REF_09` | Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003), JMLR, 3, 993-1022 | `VERIFIED_EXACT` | `N/A (JMLR v3 pp.993-1022)` | `KEEP_AS_IS` |
| `ORIG_REF_10` | Truong, C., Runge, L., & Vayatis, N. (2020), Signal Processing, 167, 107299 | `VERIFIED_WITH_AUTHOR_CORRECTION` | `10.1016/j.sigpro.2019.107299` | `CORRECT_2ND_AUTHOR_TO_OUDRE` |
| `ORIG_REF_11` | Stock, J. H., & Watson, M. W. (2019), Introduction to Econometrics, 4th ed., Pearson | `VERIFIED_EXACT` | `N/A (Textbook)` | `KEEP_AS_IS` |
| `ORIG_REF_12` | Newey, W. K., & West, K. D. (1987), Econometrica, 55(3), 703-708 | `VERIFIED_EXACT` | `10.2307/1913610` | `KEEP_AS_IS` |
| `ORIG_REF_13` | Hamilton, J. D. (1989), Econometrica, 57(2), 357-384 | `VERIFIED_EXACT` | `10.2307/1912559` | `KEEP_AS_IS` |
| `ORIG_REF_14` | Garcia, D. (2013), Journal of Finance, 68(3), 1267-1300 | `VERIFIED_EXACT` | `10.1111/jofi.12027` | `KEEP_AS_IS` |
| `ORIG_REF_15` | Engle, R. F. (1982), Econometrica, 50(4), 987-1007 | `VERIFIED_EXACT` | `10.2307/1912773` | `KEEP_AS_IS` |
| `ORIG_REF_16` | 송원호, 강규호 (2019), 뉴스 텍스트를 활용한 통화정책 충격의 금융시장 파급효과 분석, 경제학연구 67(4), 5-42 | `UNVERIFIED_NOT_FOUND` | `NONE` | `REMOVE_AND_REPLACE_WITH_VERIFIED_STUDY` |
| `NEW_REF_17` | Seo, B. (2025), Econometric forecasting using ubiquitous news text: Text-enhanced factor model, International Journal of Forecasting, 41(3), 1055-1072 | `VERIFIED_EXACT` | `10.1016/j.ijforecast.2024.11.001` | `ADD_TO_REFERENCES` |
| `NEW_REF_18` | Kim, S.-H., & Lee, W. (2026), Economic Conditions, Public Sentiment, and News Coverage: A Time-Series Analysis of Economic Agenda Dynamics in South Korea, Journalism & Mass Communication Quarterly | `VERIFIED_EXACT` | `10.1177/10776990261483609` | `ADD_TO_REFERENCES` |
| `NEW_REF_19` | Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022), Measuring news sentiment, Journal of Econometrics, 228(2), 221-243 | `VERIFIED_EXACT` | `10.1016/j.jeconom.2020.07.053` | `ADD_TO_REFERENCES` |
| `NEW_REF_20` | Glasserman, P., & Mamaysky, H. (2019), Does Unusual News Forecast Market Stress?, JFQA, 54(5), 1937-1974 | `VERIFIED_EXACT` | `10.1017/S0022109019000127` | `ADD_TO_REFERENCES` |
| `NEW_REF_21` | O'Callaghan, D., Greene, D., Carthy, J., & Cunningham, P. (2015), An analysis of the coherence of descriptors in topic modeling, Expert Systems with Applications, 42(13), 5645-5657 | `VERIFIED_EXACT` | `10.1016/j.eswa.2015.02.055` | `ADD_TO_REFERENCES` |
| `NEW_REF_22` | Egger, R., & Yu, J. (2022), A Topic Modeling Comparison Between LDA, NMF, Top2Vec, and BERTopic to Demystify Twitter Posts, Frontiers in Sociology, 7, 886498 | `VERIFIED_EXACT` | `10.3389/fsoc.2022.886498` | `ADD_TO_REFERENCES` |
| `NEW_REF_23` | Da, Z., Engelberg, J., & Gao, P. (2015), The Sum of All FEARS: Investor Sentiment and Asset Prices, Review of Financial Studies, 28(1), 1-32 | `VERIFIED_EXACT` | `10.1093/rfs/hhu072` | `ADD_TO_REFERENCES` |
| `NEW_REF_24` | Cho, J. A. (2026), Does Search Heat Ignite AI-Stock Volatility? Evidence From Korea's AI Supply Chain, Asia-Pacific Journal of Financial Studies | `VERIFIED_EXACT` | `10.1111/ajfs.70060` | `ADD_TO_REFERENCES` |
| `NEW_REF_25` | Youk, S., Kim, H., & Kim, Y. (2026), The impact of COVID-19 on news reporting and public information-seeking about particulate matter: a time-series analysis of issue competition, Quality & Quantity, 60(5), 17507-17528 | `VERIFIED_EXACT` | `10.1007/s11135-026-02870-3` | `ADD_TO_REFERENCES` |
| `NEW_REF_26` | Jung, Y.-H., Choi, Y.-H., Hong, J.-G., Kang, M.-G., & Kim, S.-T. (2025), 뉴스 기반의 투자 의사 결정 보조를 위한 단기 시점별 주가 변동 예측 시스템, 한국산학기술학회논문지, 26(3), 699-704 | `VERIFIED_EXACT` | `10.5762/KAIS.2025.26.3.699` | `ADD_TO_REFERENCES` |
| `NEW_REF_27` | Kim, Y., & Hwangbo, J.-K. (2024), The Trend Analysis of Drug-Related News Articles with Topic Modeling, 한국정보통신학회논문지(JKIICE), 28(3), 356-359 | `VERIFIED_EXACT` | `10.6109/jkiice.2024.28.3.356` | `ADD_TO_REFERENCES` |

---

## 2. 국내외 주요 선행연구 비교 매트릭스 (`literature_comparison_matrix.csv`)

| ID | 연구자 (연도) | 학술지 (DOI) | 데이터 및 규모 | 토픽/텍스트 기법 | 단일 vs 다중 국면 표현 | Strict OOS 시간 분리 | 검색 데이터 및 외부 교차 검증 | 본 연구와의 핵심 차별점 |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **S01** | Baker, Bloom, & Davis (2016) | The Quarterly Journal of Economics, 131(4), 1593-1636 (`10.1093/qje/qjw024`) | US 10 major newspapers + international newspapers (Multi-decade newspaper archives) | Keyword boolean frequency counting (EPU) | Single dimension (Policy Uncertainty) | Fixed dictionary (no unsupervised basis learning) | Option implied volatility (VIX), policy announcements, human audit | 본 연구는 비지도 NMF 토픽 기저에서 6대 경제 국면을 추출하고 동일 월 다중 국면 동시 활성화(58.21%)와 검색 데이터 교차 동조성을 검증함 |
| **S02** | Thorsrud (2020) | Journal of Business & Economic Statistics, 38(2), 393-409 (`10.1080/07350015.2018.1506344`) | Norwegian daily business newspaper (Dagens Næringsliv) (~450,000 articles (1990-2016)) | LDA (K=80 topics) + Dynamic Factor Model | Continuous topic shares aggregated into single macro factor | Quasi-real-time expanding window for DFM, but LDA topic model estimated on full corpus | Quarterly GDP growth nowcasting | 본 연구는 NMF 어휘·IDF·기저 행렬(H)·표준화 모수를 모두 학습 기간(48개월)에만 완전 동결한 Strict OOS를 적용하고 NMF vs LDA를 직접 비교함 |
| **S03** | Bybee, Kelly, Manela, & Xiu (2024) | The Journal of Finance, 79(5), 3105-3147 (`10.1111/jofi.13377`) | Wall Street Journal (WSJ) full archive (~800,000 articles (1984-2017)) | LDA (K=180 topics) | Continuous topic attention (does not compare single-dominant vs multi-regime threshold activation) | Primarily full-sample LDA topic estimation + in-sample/OOS macro regressions | Macroeconomic outputs (industrial production, employment) and stock market returns | 본 연구는 한국 경제지 93.1만 건에서 학습 고정 NMF와 LDA를 비교하고, 단일 대비 다중 국면 미표현 비중(43.75%)과 주별 네이버 검색 차분 교차 검증을 결합함 |
| **S04** | Glasserman & Mamaysky (2019) | Journal of Financial and Quantitative Analysis, 54(5), 1937-1974 (`10.1017/S0022109019000127`) |  Thomson Reuters news on 50 large financial firms (~360,000 articles (1996-2014)) | N-gram entropy (Unusualness) + Dictionary Sentiment | Not a multi-regime topic framework | Yes (Rolling past training window to prevent look-ahead bias) | Realized & implied stock market volatility | 시간 분리(Look-ahead 방지) 철학을 공유하되, 본 연구는 비지도 NMF 토픽 모델과 다중 경제 국면 활성화 및 검색 데이터 교차 검증으로 확장함 |
| **S05** | Shapiro, Sudhof, & Wilson (2022) | Journal of Econometrics, 228(2), 221-243 (`10.1016/j.jeconom.2020.07.053`) | 16 major US newspapers (LexisNexis) (~240,000 economics/business articles (1980-2015)) | Lexicon & NLP sentiment scoring | Single aggregate sentiment dimension | Fixed lexicon / pre-trained sentiment model | Consumer sentiment surveys & macro impulse responses | 단일 감성 지수로 축약할 때 사라지는 6대 세부 경제 국면(금리·물가, 부동산, 시황, 기업실적 등)의 동시 활성화 구조를 분리하여 분석함 |
| **S06** | O'Callaghan, Greene, Carthy, & Cunningham (2015) | Expert Systems with Applications, 42(13), 5645-5657 (`10.1016/j.eswa.2015.02.055`) | 6 English news & social corpora (Associated Press, guardian, Wikipedia, etc.) (Multiple corpora (2,246 to 43,586 docs)) | NMF (TF-IDF + NNDSVD) vs. LDA (Variational/Gibbs) | Methodological topic quality comparison | No temporal split or economic time-series validation | Topic coherence (NPMI, UCI, UMass) and generality metrics | O'Callaghan et al.의 방법론적 통찰을 한국 경제 뉴스 93.1만 건(학습 표본 14.4만 건)으로 확장하여 NMF vs LDA Coherence·Diversity·21회 안정성 실험을 수행함 |
| **S07** | Seo, Lee, & Cho (2022) | BOK Working Paper No. 2022-15 / 국민계정리뷰 2022-1 (`10.2139/ssrn.4230611`) | Korean internet portal economic news (Daily economic news sentences) | Transformer supervised sentiment classification | Single aggregate sentiment index | Supervised train/test split for sentence sentiment, then rolling index construction | CCSI, BSI, GDP, and macroeconomic series | 감성 단일 지수(NSI)와 달리 비지도 NMF 기반 6대 이슈 국면의 다중 활성화(58.21%)와 주별 네이버 검색 트렌드 동조성을 검증함 |
| **S08** | Seo (2025) | International Journal of Forecasting, 41(3), 1055-1072 (`10.1016/j.ijforecast.2024.11.001`) | Korean news articles across 52 media outlets (>18,000,000 articles) | Rule-based Subject-Predicate Theme Frequency Indices (TFIs) + Factor Model | Multi-sector frequency indices (rule-based, not unsupervised NMF topic decomposition) | Pseudo-out-of-sample macroeconomic forecasting (GDP nowcasting) | Korean GDP and macroeconomic indicators | 규칙 기반 주어-서술어 빈도 대신 비지도 NMF 토픽 분해와 자동 도메인 매핑의 재현성(21회 실험)을 검증하고, 네이버 검색 빅데이터와의 주별 차분 교차 검증을 수행함 |
| **S09** | Kim, Lee, Shin, & Park (2020) | 한국경제의 분석 (Journal of Korean Economic Analysis), 26(1), 1-65 (`BOK WP 2019-18 / KCI ART002585258`) | BOK Monetary Policy Board minutes & Korean economic news (BOK minutes + news corpus) | LDA, Word2Vec, and lexicon methods | Continuous topic proportions / single policy tone index | Full-sample topic modeling | BOK base rate and macroeconomic variables | 학습 기간 고정 Strict OOS NMF 파이프라인을 구축하고, NMF vs LDA 정량 비교 및 주별 네이버 검색 차분 HAC·부트스트랩 교차 검증을 제시함 |
| **S10** | Kim & Lee (2026) | Journalism & Mass Communication Quarterly, OnlineFirst (`10.1177/10776990261483609`) | South Korean economic news archive (BigKinds) (23-year monthly time series) | News coverage volume & sentiment tone (Time-series VAR/agenda dynamics) | Aggregate news volume/tone (no NMF multi-regime activation framework) | Full-sample time-series econometric modeling | GDP growth, CPI inflation, unemployment rate, KOSPI, and survey sentiment | 본 연구는 93.1만 건 기사에서 비지도 NMF로 6대 세부 경제 국면을 분리하고, 단일 대비 다중 국면 표현 보존성(43.75%)과 주별 네이버 검색 차분 동조성을 Strict OOS에서 검증함 |
| **S11** | Youk, Kim, & Kim (2026) | Quality & Quantity, 60(5), 17507-17528 (`10.1007/s11135-026-02870-3`) | BigKinds Korean news + Naver search trend (Multi-year daily/weekly time series) | Keyword-based issue volume (COVID-19 vs. Particulate Matter) | Two pre-defined environmental/health issues | Full-sample time-series analysis | Cross-validation between BigKinds news volume and Naver search volume | 빅카인즈 뉴스와 네이버 검색 결합 방식을 6대 거시·금융 경제 국면으로 확장하고, Strict OOS 분할과 주별 1차 차분 + Newey-West HAC + 24개 검정 Holm 보정 + 블록 부트스트랩을 적용함 |
| **S12** | Cho (2026) | Asia-Pacific Journal of Financial Studies, Early View (`10.1111/ajfs.70060`) | Korean search volume (Naver) & AI supply-chain stock data (Firm-level panel in Korean stock market) | Search volume index (no news NMF topic modeling) | Single sector (AI supply chain) | Panel regression design | Stock return volatility in Korean market | 본 연구는 뉴스 코퍼스 NMF 6대 국면과 네이버 검색 지수를 교차 대조하여 시황·기업실적 동조성과 `aichip` 토픽(전기차·배터리 편중)과 AI반도체 검색 간 의미적 범위 괴리를 규명함 |
| **S13** | Jung, Choi, Hong, Kang, & Kim (정용한 외) (2025) | 한국산학기술학회논문지 (JKAIS), 26(3), 699-704 (`10.5762/KAIS.2025.26.3.699`) | Korean financial news & intraday/daily stock prices (Short-term stock news dataset) | LDA Topic Modeling | Topic vector input (no multi-regime vs single-regime analysis) | Standard train/test split without topic stability or HAC/Holm inference | Short-term stock price fluctuations | 본 연구는 93.1만 건 코퍼스에서 NMF가 LDA보다 높은 Coherence·Diversity·도메인 분리도를 보임을 실증하고, HAC·Holm·블록 부트스트랩 기반의 엄격한 통계 추론을 수행함 |
| **S14** | Kim & Hwangbo (김윤하, 황보준권) (2024) | 한국정보통신학회논문지 (JKIICE), 28(3), 356-359 (`10.6109/jkiice.2024.28.3.356`) | BigKinds Korean news articles (2021-2023) (3-year issue-specific news subset) | LDA Topic Modeling | Descriptive topic keyword listing | No (descriptive full-period by year) | None (descriptive text mining) | 동일 학회지(JKIICE)의 기존 빅카인즈 토픽 모델링 연구 대비, 93.1만 건 경제 뉴스 전수 코퍼스, NMF vs LDA 비교, 21회 안정성 검증, Strict OOS 분리, 시장·검색 다중 교차 검증으로 방법론적 수준을 고도화함 |
| **OURS** | 본 연구 (Proposed Study) (2026) | 한국정보통신학회논문지 (JKIICE) 투고 후보본 (`RUN_PHASE5_6_20261027_184959 / RUN_20261106_161800`) | BigKinds 3대 경제지(매경·서경·한경) + 한국은행 ECOS + 네이버 데이터랩 (931,709건 기사 (67개월, 292주)) | TF-IDF + NMF (K=14, nndsvd) [LDA K=10~16 대조 및 21회 안정성 검증 완료] | 단일 국면(Argmax) vs 다중 국면(z>=0.5) 직접 정량 비교 (미표현 신호 43.75% 및 5대 사례 기사 원문 검증) | Yes (학습 2021~2024 [48개월] 어휘·IDF·NMF H·표준화 모수 완전 동결 후 테스트 2025~2026.07 [19개월] 투영) | 월별 코스피 수익률 충격 HAC OLS(R²=16.19%) + 주별 1차 차분 네이버 검색 HAC(maxlags=2,4,8)·24검정 Holm·이동 블록 부트스트랩(B=2,000) | 기준 연구 (Baseline Reference) |

---

## 3. 선행연구 대비 학술적 공백(Research Gap) 및 본 연구의 방어 가능한 3대 기여

### 3.1 기존 국내외 연구의 4대 방법론적 공백
1. **단일 지수 축약 또는 단일 우세 국면 가정으로 인한 복합 이슈 손실**:
   - Baker et al. (2016)의 EPU, Shapiro et al. (2022) 및 서범석 외 (2022)의 뉴스심리지수(NSI), Thorsrud (2020)의 경기동행지수는 다차원 경제 기사를 단일 불확실성·감성·경기 지수로 압축한다. 그러나 실제 한국 경제에서는 고물가·금리 인상(`macro`)과 부동산 시장 경색(`realestate`), 혹은 증시 급등락(`market`)과 상장사 실적 발표(`earnings`)가 같은 달에 동시에 부각된다.
2. **비지도 토픽 모델 선택(NMF vs LDA) 및 안정성(Stability) 검증의 부재**:
   - 국내외 경제 뉴스 토픽 모델링 연구(Bybee et al., 2024; 김수현 외, 2020; 정용한 외, 2025; 김윤하·황보준권, 2024)는 대부분 관행적으로 LDA를 채택하거나 단일 시드 적합 결과만 보고하며, 동일 코퍼스에서 NMF와 LDA의 Coherence·Diversity·도메인 분리도 비교나 부분표본 재추출 안정성을 정량 검증하지 않았다.
3. **전체 기간 일괄 토픽 적합에 따른 미래 정보 누수(Look-ahead Bias)**:
   - 많은 선행연구가 전체 분석 기간의 문서로 어휘 사전과 토픽 기저를 먼저 학습한 뒤 시계열 회귀를 수행하여, 평가 기간의 미래 어휘와 토픽 구조가 과거 지표 산출에 개입하는 정보 누수 한계를 안고 있다.
4. **뉴스 국면과 대중 검색 관심도 간 주별 차분(First-Difference) 및 HAC·다중검정·부트스트랩 교차 검증의 부재**:
   - 최근 한국 뉴스 보도를 분석한 Kim and Lee (2026)는 월별 기사량·논조와 서베이 심리지수를 분석하였고, Youk et al. (2026)은 코로나19·미세먼지 이슈에 대해 빅카인즈 뉴스와 네이버 검색을 비교하였으나, 6대 거시·금융 경제 국면에 대해 단위근 추세를 제거한 주별 1차 차분 시계열과 Newey-West HAC, 다중검정 보정, 블록 부트스트랩을 결합하여 표본 외(Strict OOS) 동조성을 검증한 연구는 수행되지 않았다.

### 3.2 본 연구의 방어 가능한 3대 학술적 기여 (Defensible Contributions)
1. **[방법론적 기여] 한국 경제 뉴스에서 NMF의 적합성·안정성 실증 및 결정론적 Strict OOS 아키텍처 확립**:
   - 931,709건 코퍼스의 학습 기간(48개월) 동일 표본(144,000건)·동일 어휘(22,193개) 통제 실험에서 NMF($K=14$)가 LDA($K=14$) 대비 더 높은 토픽 응집도($C_v = 0.8258$ vs $0.7448$, $\text{NPMI} = 0.3011$ vs $0.2233$)와 어휘 다양성($\text{TD@20} = 0.9143$ vs $0.8036$), 빠른 연산 속도(학습 $36.1$초 vs $91.1$초), 그리고 더 많은 유효 경제 국면 분리(6개 vs 5개)를 달성함을 입증하였다.
   - 나아가 80% 층화 부분표본 10회 반복 및 초기화 민감도 11회 실험(총 21회)에서 6대 핵심 국면이 100%(21/21회) 재현됨을 확인하고, 어휘·IDF·NMF $H$·표준화 모수($\mu_{\text{train}}, \sigma_{\text{train}}$)를 학습 기간에만 완전 동결하여 테스트 기간(19개월)으로 투영하는 무누수(Zero-Leakage) 파이프라인을 구현하였다.
2. **[정보 표현적 기여] 단일 대표 국면 대비 다중 국면 활성화의 정보 보존성(43.75%) 정량화 및 기사 단위 실증**:
   - 전체 67개월 중 58.21%(39개월)에서 2개 이상의 경제 국면이 동시에 활성화되며, 단일 대표 국면(Argmax) 방식으로 표현을 제한할 경우 다중 국면 활성 신호 112건 중 **49건(43.75%)이 별도 국면으로 표현되지 않음**을 규명하였다.
   - 객관적 규칙으로 자동 선정된 5개 사례 월(`2021-09, 2022-10, 2023-08, 2026-01, 2026-02`)의 실제 코퍼스 기사(`W` 가중치) 역추적을 통해, 단일 국면 표현이 2022년 10월 금리 인상기의 부동산 경색($z=+1.45$)이나 2023년 8월·2026년 2월(OOS) 증시 변동기의 상장사 실적 충격($z=+1.16 \sim +1.64$)을 누락함을 기사 원문 수준에서 입증하였다.
3. **[실증적 기여] 시장 수익률 충격(월별) 및 네이버 검색 트렌드(주별 차분)와의 다각적 동시점 교차 검증 및 한계의 투명한 규명**:
   - 월별 코스피 수익률 충격(`kospi_ret_std`, $N=67$)과의 동행 HAC 회귀($R^2 = 16.19\%, F = 4.6833, p = 0.000573$)에서 금리·물가($\beta = -0.7418, p_{\text{holm}} = 0.0024$)와 자본거래($\beta = -0.5299, p_{\text{holm}} = 0.0129$)의 유의한 음(-)의 동행 관계를 확인하는 동시에, 월별 조기경보 규칙은 테스트 기간 적중 0건($TP=0, FP=1$)으로 사전 예측력이 없음을 투명하게 구분하였다.
   - 291주 주별 1차 차분 네이버 검색 교차 검증에서 Newey-West HAC 시차(`maxlags=2,4,8`), 24개 검정 Holm 보정, 이동 블록 부트스트랩($B=2,000$), 공통 앵커(`'은행'`) 분모 민감도를 모두 통과하여 표본 외 테스트 기간($N=82$주)에서도 **'시황'($r = +0.4984$)과 '기업실적'($r = +0.4718$)의 동시점($h=0$) 동조성이 재현**됨을 입증하였다.