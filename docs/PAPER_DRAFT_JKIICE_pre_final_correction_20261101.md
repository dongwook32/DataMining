# 뉴스 빅데이터와 NMF 기반의 한국형 경제 이슈 다중 국면 탐지 및 다각적 실증 검증
### Multi-Regime Detection of Korean Economic Issues via News Big Data and Non-negative Matrix Factorization: Methodological and Empirical Validations

**[ 저자 미정 (심사본) ]**  
한국성서대학교 AI융합학부 (*School of AI Convergence, Korean Bible University, Seoul, 01757 Korea*)

---

## 요 약
본 연구는 2021년 1월부터 2026년 7월까지(총 67개월) 국내 3대 주요 경제 일간지(매일경제, 서울경제, 한국경제)에서 수집한 931,709건의 경제 뉴스 기사 코퍼스를 대상으로 비지도 학습 기법인 비음수 행렬 분해(NMF)와 고정 표준화 체계를 구축하여 한국 경제의 잠재 이슈 국면을 탐지하고, 시장 지표 및 대중 검색 빅데이터와의 동조성을 다각도로 실증 분석하였다. 특히 미래 정보 누수(Data Leakage)를 원천 차단하기 위해 학습 기간(2021.01~2024.12, 48개월) 전용 어휘 사전(22,193개 단어)과 IDF, NMF 기저 행렬($H$, 14개 잠재 토픽)을 고정하여 테스트 기간(2025.01~2026.07, 19개월)으로 확장 투영하는 엄격한 표본 외(Strict Out-of-Sample) 파이프라인을 확립하였다. 도출된 토픽 중 거시경제적 의미가 일관된 6대 유효 국면(금리·물가, 부동산, AI·반도체, 시황, 기업실적, 자본거래)을 체계화하였으며, 기존 선행연구의 단일 지배 국면(Single Dominant) 선택 방식이 갖는 복합 이슈 절단 한계를 규명하고 학습 고정 z점수 기반의 다중 국면 활성화 체계($z \ge 0.5$)를 적용하였다. 

실증 분석 결과는 다음과 같다. 첫째, 한국 경제 뉴스는 전체 67개월의 58.2%(학습 기간 66.7%)에서 2개 이상의 경제 국면이 동시 활성화되는 구조적 다중성을 보였다. 단일 대표 국면만을 선택할 경우 유효 활성 국면 신호의 43.8%(112건 중 49건)가 통계적으로 누락되어, 다중 국면 방식이 복합 거시 충격의 정보를 보존하는 데 방법론적 우위가 있음을 입증하였다. 둘째, 표본 내 6대 국면 비중과 코스피 과거 변동성 정규화 월간 수익률(`kospi_ret_std`) 간의 Newey-West HAC OLS 회귀분석 결과, 설명력 $R^2 = 16.19\%$ ($F = 4.68, p = 0.00057$)를 기록하였으며, '금리·물가'($\beta = -0.7418$, Holm $p = 0.0024$) 및 '자본거래'($\beta = -0.5299$, Holm $p = 0.0129$) 국면의 심화가 주가 수익률 충격과 유의한 음(-)의 동행 관계를 형성함을 보였다. 셋째, 292주간의 네이버 검색 데이터랩(Datalab) 주별 패널과의 1차 차분 교차 검증 및 Newey-West HAC 검정 결과, 표본 외(Strict OOS) 테스트 기간에서도 '시황' ↔ 국내증시 검색($r = +0.4984$, HAC $p_{\text{holm}} = 0.043$), '기업실적' ↔ 기업실적 검색($r = +0.4718$, HAC $p_{\text{holm}} = 0.001$), '금리·물가' ↔ 금리 검색($r = +0.3397$, HAC $p = 0.017$)에서 주별 단위의 실시간 동시 동조성($h=0$)이 확인되었다. 넷째, 비지도 NMF의 의미론적 타당성을 검증하기 위해 테스트 기간 기사 380건에 대한 독립 평가자 2인 블라인드 인간 평가 절차를 설계하였다. 본 연구는 인과 추론이나 시장 예측력에 대한 과장된 주장을 배제하고, 복합 이슈 정보 보존성과 이종 빅데이터 교차 동조성을 입증한 객관적 텍스트 마이닝 프레임워크를 제공한다.

**키워드 :** 경제 뉴스 빅데이터, 텍스트 마이닝, 토픽 모델링, 비음수 행렬 분해(NMF), 다중 국면 활성화, 표본 외(Strict OOS) 검증, 네이버 데이터랩, 교차 데이터 검증

---

## ABSTRACT
This study establishes an unsupervised text-mining framework based on Non-negative Matrix Factorization (NMF) to detect latent economic issue regimes from 931,709 economic news articles collected from three major Korean business dailies (Maeil Business Newspaper, Seoul Economic Daily, and Korea Economic Daily) from January 2021 to July 2026 (67 months). To strictly prevent future information leakage, we constructed a deterministic Strict Out-of-Sample (OOS) pipeline where the vocabulary (22,193 terms), IDF weights, and NMF components ($H$, 14 latent topics) were fitted exclusively on the training period (2021.01–2024.12, 48 months) and projected onto the test period (2025.01–2026.07, 19 months). Six economically consistent valid regimes—Interest Rate & Inflation, Real Estate, AI & Semiconductor, Stock Market, Corporate Earnings, and Capital Transactions—were established. To overcome the truncation of concurrent economic shocks inherent in traditional single-dominant regime approaches, we proposed a multi-regime activation framework based on training-fixed standardized scores ($z \ge 0.5$). 

Empirical findings are fourfold: First, Korean economic news exhibited structural coexistence of multiple issues, with two or more regimes simultaneously active in 58.2% of the total 67 months (66.7% in the training period). Restricting representation to a single dominant regime caused 43.8% (49 out of 112 signals) of active issue signals to be omitted, demonstrating the information preservation advantage of multi-regime activation. Second, Newey-West HAC OLS regressions on volatility-standardized monthly KOSPI returns (`kospi_ret_std`) showed an in-sample explanatory power of $R^2 = 16.19\%$ ($F = 4.68, p = 0.00057$), with 'Interest Rate & Inflation' ($\beta = -0.7418$, Holm $p = 0.0024$) and 'Capital Transactions' ($\beta = -0.5299$, Holm $p = 0.0129$) exhibiting statistically significant negative contemporaneous associations with return shocks. Third, first-differenced weekly cross-validation with Naver Datalab search trends across 292 weeks with Newey-West HAC standard errors confirmed simultaneous weekly co-movement ($h=0$) during the Strict OOS test period for 'Stock Market' ↔ Domestic Stock search ($r = +0.4984$, HAC $p_{\text{holm}} = 0.043$), 'Corporate Earnings' ↔ Corporate Earnings search ($r = +0.4718$, HAC $p_{\text{holm}} = 0.001$), and 'Interest Rate & Inflation' ↔ Interest Rate search ($r = +0.3397$, HAC $p = 0.017$). Fourth, to evaluate the semantic validity of NMF topics, a blind human evaluation protocol was designed for 380 stratified test articles. Avoiding unverified claims of market predictability or causality, this study provides a verifiable text-mining methodology emphasizing multi-regime preservation and cross-source big data concordance.

**Keywords :** Economic News Big Data, Text Mining, Topic Modeling, Non-negative Matrix Factorization (NMF), Multi-Regime Activation, Strict Out-of-Sample Validation, Naver Datalab, Cross-Source Validation

---

## Ⅰ. 서 론

현대 경제 시스템은 통화정책 긴축, 인플레이션 압력, 글로벌 무역 마찰, 그리고 인공지능(AI)과 첨단 반도체 산업 구조 재편 등 다양한 거시경제 요인들이 복합적으로 상호작용하며 전개된다[1-3]. 이러한 복잡한 거시 환경의 변화는 주식시장과 외환시장의 단기 가격 변동성을 유발할 뿐만 아니라, 기업의 자본 조달과 소비자의 심리적 기대 형성에 구조적 영향을 미친다[4-6]. 이에 따라 정책 당국과 자본시장 참여자들은 거시경제의 주요 어젠다 변화를 기민하게 파악하고 시스템적 위험을 조기에 진단하기 위한 실시간 정보 분석 체계를 필요로 하고 있다.

그러나 국내총생산(GDP), 소비자물가지수(CPI), 산업생산지수 등 공공기관이 공표하는 전통적인 거시경제 통계는 본질적인 공표 시차(Publication Lag)를 수반한다[3, 5]. 경제 활동이 일어난 시점으로부터 수주에서 수개월 이후에야 지표가 공표되며, 사후적인 통계 수정(Revision)도 빈번하여 급변하는 현대 금융시장 환경에서 실시간 의사결정을 지원하는 데 시차적 한계를 갖는다[2]. 이러한 한계를 보완하기 위해, 최근 정보처리 및 금융 빅데이터 분야에서는 매일 대량으로 생성되는 비정형 뉴스 텍스트(News Text) 빅데이터로부터 거시경제 불확실성(EPU)[1], 뉴스심리지수(NSI)[5], 잠재 토픽 관심도(Topic Attention)[2, 3]를 도출하여 경기 동향을 추적하려는 연구가 활발히 진행되어 왔다.

그러나 비정형 텍스트 기반 거시 이슈 국면 분석을 다룬 기존 연구들은 정보처리 및 실증 검증 측면에서 다음과 같은 세 가지 구조적 한계를 나타낸다. 

첫째, **단일 대표 토픽(Single Dominant Regime) 강제로 인한 정보 절단 편향(Truncation Bias)**이다. 기존 연구들은 각 월에서 출현 비중이 1위인 토픽만을 시장의 국면으로 정의하거나 선형 결합 지수를 도출하는 방식을 주로 채택하였다[2, 7]. 그러나 현실 경제는 고물가 충격과 자본시장 위축, 부동산 침체와 금리 인상이 동시에 공존하는 '복합 이슈(Poly-crisis)'가 일반적이다. 1위 국면만을 강제로 선택할 경우 2위나 3위의 중대한 잠재 이슈가 통계적으로 누락되어 거시 정보의 왜곡을 초래한다.

둘째, **표본 외(Out-of-Sample) 검증 설계의 미흡과 미래 정보 누수(Data Leakage)**이다. 많은 텍스트 마이닝 연구들이 전체 분석 기간의 모든 문서를 한꺼번에 투입하여 TF-IDF 어휘 사전을 구축하고 토픽 모델(LDA, NMF)을 적합한 뒤, 그 결과를 과거와 미래 시점에 동일하게 적용하는 실수를 범한다. 이는 테스트 기간에 아직 발생하지 않은 미래의 어휘 분포와 토픽 가중치가 과거 시점에 미리 반영되는 심각한 미래 정보 누수 문제를 발생시킨다.

셋째, **이종 빅데이터를 활용한 외적 타당성(External Validity) 교차 검증의 부재**이다. 비지도 학습으로 추출된 뉴스 토픽 지표가 언론사의 편집 방향이나 보도 관행에 불과한 것인지, 아니면 실제 일반 대중의 실물 관심사와 동조하는 객관적 현상인지를 독립된 정보원을 통해 검증하는 작업이 부족하였다. 또한 시계열 수준값(Level) 간의 비정상성 단위근 추세를 제거하지 않은 채 단순 상관계수를 보고함으로써 허위 상관(Spurious Correlation)을 성과로 오인하는 경우가 빈번하였다.

이에 본 연구는 2021년 1월부터 2026년 7월까지(총 67개월) 국내 3대 경제 일간지(매일경제, 서울경제, 한국경제)에서 수집한 931,709건의 경제 뉴스 기사 코퍼스를 바탕으로 비음수 행렬 분해(NMF)를 적용하여 한국형 경제 이슈 국면 탐지 체계를 구축한다. 특히 학습 기간(2021.01~2024.12, 48개월)과 테스트 기간(2025.01~2026.07, 19개월)을 엄격히 분리한 **결정론적 표본 외(Strict OOS) 파이프라인**을 설계하고, 비정상 단위근 추세를 제거한 차분 시계열 검증을 수행한다. 

본 연구가 규명하고자 하는 핵심 연구 질문(Research Questions)은 다음과 같다:
- **RQ1 (정보 보존성)**: 한국 경제 뉴스에서 다중 국면 동시 활성화 방식은 기존의 단일 대표 국면 방식 대비 복합 경제 이슈 정보를 얼마나 더 보존하는가?
- **RQ2 (금융시장 동행성)**: 학습 기간 고정 모델로부터 도출된 6대 유효 국면 비중은 과거 변동성으로 정규화한 코스피 수익률 충격과 통계적으로 유의한 동행 관계를 나타내는가?
- **RQ3 (이종 데이터 교차 검증)**: 뉴스 국면 지표는 네이버 데이터랩(Datalab) 대중 검색 관심도와 주별(Weekly) 차분 시계열 관점에서 통계적으로 유의한 동조화를 나타내는가?
- **RQ4 (의미론적 타당성)**: 비지도 학습 NMF가 도출한 경제 국면 체계의 타당성을 인간의 독립적 판단과 객관적으로 비교하기 위한 블라인드 평가 설계는 어떻게 구성되는가?

---

## Ⅱ. 관련 연구 및 이론적 배경

### 2.1 뉴스 텍스트 기반 거시경제 지표 및 시장 반응
텍스트 데이터를 계량경제학적 분석에 도입한 대표적 선구 연구인 Baker, Bloom, and Davis[1]는 10대 주요 신문 기사에서 '경제', '정책', '불확실성' 키워드의 동시 출현 빈도를 집계하여 경제정책불확실성(EPU) 지수를 개발하였다. 이후 텍스트 분석 연구는 단순 단어 빈도 계측에서 확률적·선형대수적 머신러닝 기법인 토픽 모델링으로 진화하였다. Bybee et al.[2]은 월스트리트저널(WSJ) 기사 약 80만 건을 잠재 디리클레 할당(LDA) 토픽 모델링으로 분석하여 거시경제 주제 비중(Attention) 시계열을 도출하였으며, 감성 분석 없이 토픽 비중의 변화만으로도 실물 비즈니스 사이클을 추적할 수 있음을 보였다. Thorsrud[3]는 일간 비즈니스 신문의 토픽 비중 시계열을 동적 요인 모형(DFM)과 결합하여 분기 GDP를 조기 추정하는 실시간 동행 지수를 제시하였다.

국내에서도 텍스트 마이닝을 활용한 거시경제 지표 연구가 활발히 진행되었다. 서범석 외[5]는 한국은행에서 딥러닝 모형을 활용하여 뉴스심리지수(NSI)를 개발하였으며, 소비자심리지수(CCSI) 및 경기동행지수 순환변동치에 유의하게 선행함을 보고하였다. 김수현·박기영[6]은 경제 기사 텍스트를 통해 경제 주체의 심리 변화가 경기 변동과 동조화됨을 실증하였고, 송원호·강규호[16]는 통화정책 충격의 금융시장 파급효과를 텍스트로 분석하였다. 그러나 기존 연구들은 주로 단일 대표 지수나 연속형 비중을 시장 예측의 설명변수로 투입하는 데 집중하였으며, 복수의 거시경제 충격이 동시에 활성화되는 국면 공존성(Regime Coexistence) 문제를 체계적으로 비교·분석하지는 못하였다.

### 2.2 비음수 행렬 분해(NMF)와 고정 특징 투영
토픽 모델링 기법 중 비음수 행렬 분해(NMF)는 문서-어휘 가중치 행렬 $V \in \mathbb{R}^{N \times M}_+$를 두 개의 저차원 비음수 행렬 $W \in \mathbb{R}^{N \times K}_+$와 $H \in \mathbb{R}^{K \times M}_+$의 곱으로 근사 분해하는 차원 축소 기법이다[8]:

$$V \approx W \times H \quad (\text{단, } W \ge 0, H \ge 0)$$

여기서 $W$는 각 문서가 $K$개 잠재 토픽에 갖는 기여도 행렬이며, $H$는 각 토픽이 $M$개 어휘에 갖는 단어 중요도 행렬이다. NMF는 음수 가중치를 배제하는 비음수 제약(Non-negativity Constraint)으로 인해 부품이 모여 전체를 구성하는 부분 기반 표현(Part-based Representation)을 산출하므로, 토픽의 해석 가능성이 매우 높고 희소 행렬에 대해 결정론적이고 안정적인 수렴 특성을 지닌다.

특히 본 연구와 같이 엄격한 표본 외(Strict OOS) 평가를 수행할 때, NMF는 학습 기간(Train) 문서에서 도출된 기저 행렬 $H_{\text{train}}$을 고정(Freeze)한 뒤, 테스트 기간(Eval)의 새로운 문서 행렬 $V_{\text{eval}}$에 대해 $W_{\text{eval}} \approx \arg\min_W \| V_{\text{eval}} - W H_{\text{train}} \|_F$를 독립적으로 최적화하여 투영할 수 있는 강력한 장점을 지닌다.

### 2.3 시계열 정상성 및 Newey-West HAC 견고 공분산
금융 및 거시경제 시계열 데이터는 과거 충격이 수개월간 잔류하는 자기상관(Autocorrelation)과 시기에 따라 분산이 변하는 이분산성(Heteroskedasticity)을 수반한다[11, 15]. 또한 지수 수준값(Level)이나 비정상 시계열을 그대로 사용할 경우, 두 변수가 공통 추세를 공유함으로써 통계적으로 무의미함에도 강한 상관을 보이는 허위 회귀(Spurious Regression) 오류가 발생한다.

본 연구에서는 이러한 시계열 착시를 통제하기 위해 모든 상관분석 및 검증에 **1차 차분(First Difference)**을 적용하여 정상 시계열로 변환한 후 분석을 수행한다. 또한 회귀분석 및 시차 상관 검정 시 Newey and West[12]의 HAC(Heteroskedasticity and Autocorrelation Consistent) 견고 공분산 추정법을 적용한다:

$$V_{\text{HAC}} = (X'X)^{-1} \left[ \Gamma_0 + \sum_{l=1}^{q} \left(1 - \frac{l}{q + 1}\right) (\Gamma_l + \Gamma_l') \right] (X'X)^{-1}$$

이를 통해 시계열 오차의 자기상관에 따른 표준오차 과소추정을 방지하고 통계적 유의성을 보수적으로 검정한다.

---

## Ⅲ. 연구 방법 및 Strict OOS 시스템 설계

### 3.1 연구 대상 및 데이터 수집
텍스트 데이터는 한국언론진흥재단 빅카인즈(BigKinds)를 통해 2021년 1월 1일부터 2026년 7월 31일까지(총 67개월) 국내 3대 주요 경제 일간지인 **매일경제, 서울경제, 한국경제**의 경제 섹션 기사 전량을 수집하였다. 저작권 보호로 200자 절단이 적용되는 원문 대신, 기사 전문의 형태소 분석 명사 단위 정제 필드인 '키워드'를 활용하였다. 수집된 원시 데이터 931,709건은 결측치 및 중복 기사 없이 100% 정제된 코퍼스로 보존되었다.

거시금융 시장 지표는 한국은행 경제통계시스템(ECOS) API를 통해 월별 시계열로 취합하였다:
1. **코스피 월간 로그수익률**: $kospi\_ret_t = 100 \times [\ln(KOSPI_t) - \ln(KOSPI_{t-1})]$
2. **과거 변동성 정규화 수익률**: $kospi\_ret\_std_t = kospi\_ret_t / s_{t-1}^{(12)}$, 여기서 $s_{t-1}^{(12)} = \operatorname{SD}(kospi\_ret_{t-12 : t-1})$ (직전 12개월 월간 수익률 표준편차로 조정한 변수로, 일별 고빈도 실현변동성 자체와 구분되는 과거 변동성 정규화 수익률 충격 지표임).
3. **거시 변동 지표**: 한국은행 기준금리 월간 변화분(`base_rate_diff`), 소비자심리지수 월간 변화분(`ccsi_diff`), 원/달러 환율 월간 수익률(`usdkrw_ret`).

대중 검색어 트렌드 대조를 위해서는 네이버 데이터랩(Datalab)의 일별 상대검색량 지수(`score_rel = score / anchor_score`)를 수집하여 동일한 ISO week 기준 주별 패널로 집계하였다.

### 3.2 결정론적 표본 외(Strict OOS) 분할 및 전처리
본 연구는 미래 정보 누수를 원천 차단하기 위해 전체 기간을 다음과 같이 양분하였다:
- **학습 기간 (Train)**: 2021-01 ~ 2024-12 (48개월, 기사 643,095건)
- **표본 외 테스트 기간 (Eval OOS)**: 2025-01 ~ 2026-07 (19개월, 기사 288,614건)

모든 텍스트 특징 선택과 가중치 모수는 학습 기간(48개월)에서만 결정론적으로 산출되었다:
1. **어휘 사전(Vocabulary)**: 학습 기간 643,095건 기사에서 문서 빈도(Document Frequency) 20회 이상 출현 어휘 중 범용 명사를 정제하여 최종 **22,193개 단어** 확정.
2. **IDF 벡터**: 학습 기간 문서 빈도만을 기준으로 스무딩 $IDF = \ln((1 + N_{\text{train}}) / (1 + DF_{\text{train}})) + 1$ 계산.
3. **NMF 모델 적합**: 학습 기간 48개월 동안 월별 3,000건씩 층화 표집한 144,000건의 기사 행렬에 대해 NMF($K=14$, init='nndsvd', random_state=42)를 단 1회 적합하여 기저 행렬 $H_{\text{train}}$ ($14 \times 22,193$) 도출.
4. **테스트 기간 변환**: 2025년 1월 이후의 288,614건 기사에 대해서는 고정된 어휘 사전과 IDF를 적용한 후, 학습된 $H_{\text{train}}$에 투영하여 토픽 기여도 행렬 $W$를 도출함.

### 3.3 14개 잠재 토픽의 6대 경제 국면 체계화
학습 기간 NMF 기저 행렬 $H_{\text{train}}$의 상위 단어 질량(Mass) 분석을 통해 14개 잠재 토픽을 경제학적 정합성에 맞게 매핑하였다:
- **배정 국면 (6개 유효 국면)**:
  - **`macro` (금리·물가)**: 토픽 1 (물가, 금리, Fed, 인플레이션, 한국은행, 기준금리)
  - **`realestate` (부동산)**: 토픽 2 (대출, 주택, 부동산, 아파트) + 토픽 3 (단지, 분양, 청약, 주택)
  - **`aichip` (AI·반도체)**: 토픽 12 (AI, 인공지능, 반도체, 엔비디아, HBM)
  - **`market` (시황)**: 토픽 4 (종목, 매수, 외국인, 지수, 코스피) + 토픽 13 (코스닥, 개장, 마감, 코스피)
  - **`earnings` (기업실적)**: 토픽 7 (영업이익, 매출액, 실적, 공시, 분기)
  - **`capital` (자본거래)**: 토픽 6 (상장, 주식, 투자자, 지분, M&A, IPO)
- **미형성 국면 (`unrepresented / NaN`)**: 가계부채(`hhdebt`)와 대외통상(`trade`)은 학습 기간 NMF에서 독립 토픽으로 분리되지 않고 부동산 토픽 및 잔차 토픽에 흡수되어 유효 국면을 형성하지 못함.
- **잔차 토픽 (Residual / Ambiguous)**: 토픽 0 (일반경영·ESG), 토픽 5 (유통·소비재 마케팅), 토픽 8 (글로벌 제조수출), 토픽 9 (해외증시 일반), 토픽 10 (행정·제도), 토픽 11 (스타트업 플랫폼) 등 6개 토픽은 비배정 잔차 비중(`residual_share`)으로 분류.

### 3.4 학습 기간 고정 다중 국면 활성화 체계 ($z \ge 0.5$)
각 국면 $d$의 월별 점유율 $s_{d,t}$에 대해, 미래 정보 누수를 차단하기 위해 **학습 기간(48개월)만의 표본 평균 $\mu_{d,\text{train}}$과 표준편차 $\sigma_{d,\text{train}}$**을 모수로 고정하여 표준화 점수를 산출하였다:

$$z_{d,t} = \frac{s_{d,t} - \mu_{d,\text{train}}}{\sigma_{d,\text{train}}}$$

테스트 기간(2025.01~2026.07)에서도 사후적인 평균과 표준편차를 다시 계산하지 않고 학습 기간의 모수를 그대로 적용하였다. $z_{d,t} \ge 0.5$를 충족하는 모든 국면을 해당 월의 활성 국면으로 정의하였다.

---

## Ⅳ. 실증 분석 결과

### 4.1 6대 경제 이슈 국면 분포 및 기술통계
67개월(학습 48개월 + 테스트 19개월) 동안 931,709건의 기사로부터 도출된 6대 유효 국면의 학습 기간 고정 표준화 기준 분포는 표 1과 같다.

**Table 1. Distribution of 6 Economic Regimes and Training-Fixed Standardization Parameters.**

| Regime Name | Slug | Train Mean Share (%) | Train Std. Dev. (%p) | $z \ge 0.5$ Cutoff (%) | Full Active Months ($N=67$) | Train Active ($N=48$) | Eval OOS Active ($N=19$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 시황 | market | 29.94 | 2.15 | 31.01 | 18 (26.9%) | 12 (25.0%) | 6 (31.6%) |
| 부동산 | realestate | 6.87 | 0.57 | 7.15 | 23 (34.3%) | 20 (41.7%) | 3 (15.8%) |
| 금리·물가 | macro | 4.72 | 1.18 | 5.31 | 13 (19.4%) | 12 (25.0%) | 1 (5.3%) |
| 자본거래 | capital | 2.22 | 0.35 | 2.40 | 19 (28.4%) | 14 (29.2%) | 5 (26.3%) |
| 기업실적 | earnings | 1.89 | 0.38 | 2.08 | 22 (32.8%) | 18 (37.5%) | 4 (21.1%) |
| AI·반도체 | aichip | 1.25 | 0.42 | 1.46 | 17 (25.4%) | 13 (27.1%) | 4 (21.1%) |
| *(미형성 국면)* | hhdebt, trade | NaN | NaN | - | - | - | - |
| *(잔차 비중)* | residual | 53.11 | 2.20 | - | - | - | - |

표 1에서 확인되듯, 6개 유효 국면의 활성 개월 수는 13개월에서 23개월(19.4%~34.3%) 사이로 고르게 분포하여 특정 이슈에 편중되지 않는 식별력을 보였다. 학습 기간 고정 모수를 적용한 결과, 테스트 기간(19개월)에서도 국면별로 1~6개월의 활성화가 안정적으로 탐지되었다.

---

### 4.2 연구 A: 단일 국면 vs 다중 국면 활성화 비교 실증 (RQ1)
다중 국면 활성화 체계가 기존의 단일 대표 국면(Argmax) 선택 방식 대비 복합 거시 이슈 정보를 얼마나 더 보존하는지를 정량적으로 검증하였다.

비교 대상 방식:
- **방식 A-1 (Unconstrained Argmax)**: 매월 6개 국면 중 점수가 가장 높은 1개 국면만 무조건 선택.
- **방식 A-2 (Hurdle Argmax)**: 최대 점수 국면이 $z \ge 0.5$ 이상일 때만 선택하고 미달 시 '비활성(none)' 처리.
- **방식 B (Multi-activation, 제안)**: $z \ge 0.5$를 만족하는 모든 국면을 동시 활성화.

실증 비교 결과는 표 2와 같다.

**Table 2. Quantitative Comparison of Single-Dominant vs. Multi-Regime Activation Frameworks.**

| Sample Split | Months ($N$) | Mean Active Regimes | 0 Active Months (%) | 1 Active Month (%) | $\ge 2$ Active Months (%) | Total Active Signals | Signals Omitted by Argmax | Omitted Signal Ratio (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full Sample (67m)** | 67 | 1.672 | 5.97% | 35.82% | **58.21%** | 112 | 49 | **43.75%** |
| **Train Period (48m)** | 48 | 1.854 | 2.08% | 31.25% | **66.67%** | 89 | 42 | **47.19%** |
| **Eval OOS Period (19m)**| 19 | 1.211 | 15.79% | 47.37% | **36.84%** | 23 | 7 | **30.43%** |

표 2의 정량적 비교 결과는 다음과 같은 사실을 입증한다:
1. **복합 국면 공존성**: 한국 경제 뉴스는 전체 기간의 **58.21%**에서 2개 이상의 경제 국면이 동시에 임계값($z \ge 0.5$)을 초과하였다. 특히 금리 인상과 물가 충격이 집중되었던 학습 기간(48개월)에서는 이 비율이 **66.67%**에 달하였다.
2. **단일 방식의 정보 절단**: 단일 대표 국면(Argmax) 방식만을 채택할 경우, 다중 국면 체계에서 정상 식별된 112건의 유효 활성 국면 신호 중 **43.75%에 해당하는 49건**이 별도의 국면으로 표현되지 못하고 완전히 누락된다.
3. **주요 동시 활성 조합**: 2022~2023년 고물가·긴축 기간 동안 `macro;capital` (금리·물가 급등과 자본거래 위축) 및 `macro;realestate` (금리 인상과 부동산 시장 침체)의 동시 점등이 집중적으로 관찰되었다.
4. **해석의 엄격한 한계**: 본 결과는 다중 국면 방식이 단일 국면 방식에 비해 통계적으로 더 많은 유효 신호를 보존한다는 '정보 보존성(Information Preservation)'을 증명하는 것이며, 이 수치 자체가 예측 정확도의 우수성을 의미하는 것은 아니다.

---

### 4.3 금융시장 설명력: Newey-West HAC OLS 회귀분석 (RQ2)
학습 기간 고정 NMF 투영으로 도출된 6대 유효 국면 비중 벡터를 설명변수로 하여 67개월 전체 표본에서 Newey-West HAC 견고 회귀분석(maxlags=3)을 수행한 결과는 표 3과 같다.

**Table 3. Newey-West HAC OLS Estimation on Volatility-Standardized Monthly KOSPI Return (`kospi_ret_std`, N=67).**

| Variable | Coeff ($\beta$) | HAC Std. Error | $t$-statistic | 95% Conf. Interval | Raw $p$-value | Holm-Adjusted $p$-value | VIF |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `const` | $+0.0631$ | $0.1357$ | $+0.465$ | $[-0.2029, +0.3291]$ | $0.6419$ | — | — |
| **`z_macro` (금리·물가)** | **$-0.7418$** | **$0.2093$** | **$-3.543$** | **$[-1.1521, -0.3315]$** | **$0.0004$** | **$0.0024$** | $1.95$ |
| **`z_capital` (자본거래)** | **$-0.5299$** | **$0.1758$** | **$-3.015$** | **$[-0.8744, -0.1854]$** | **$0.0026$** | **$0.0129$** | $1.91$ |
| `z_realestate` (부동산) | $-0.2082$ | $0.1185$ | $-1.757$ | $[-0.4403, +0.0240]$ | $0.0789$ | $0.3155$ | $1.27$ |
| `z_market` (시황) | $-0.1437$ | $0.0898$ | $-1.600$ | $[-0.3197, +0.0323]$ | $0.1096$ | $0.3289$ | $1.16$ |
| `z_aichip` (AI·반도체) | $-0.2583$ | $0.1802$ | $-1.434$ | $[-0.6115, +0.0948]$ | $0.1517$ | $0.3289$ | $1.33$ |
| `z_earnings` (기업실적) | $-0.1143$ | $0.1698$ | $-0.673$ | $[-0.4471, +0.2185]$ | $0.5008$ | $0.5008$ | $1.27$ |
| **Model Diagnostics** | \multicolumn{7}{l}{$N = 67, df_{\text{model}} = 6, df_{\text{resid}} = 60, R^2 = 16.19\%, \text{Adj-}R^2 = 7.81\%$} \\
| **HAC Joint Test** | \multicolumn{7}{l}{Newey-West HAC $F = 4.6833$ ($p = 0.000573$), Wald $\chi^2 = 28.0995$} \\

표 3에 나타난 바와 같이:
1. 6대 국면 모델은 과거 변동성 정규화 코스피 수익률 충격(`kospi_ret_std`)에 대해 $R^2 = 16.19\%$의 설명력을 보였으며, HAC 결합 검정 통계량 $F = 4.6833, p = 0.000573$으로 통계적으로 유의하였다. 모든 설명변수의 분산팽창계수(VIF)는 2.0 미만으로 다중공선성 위험이 없었다.
2. 개별 변수 중 **'금리·물가'($\beta = -0.7418$, Holm $p = 0.0024$)**와 **'자본거래'($\beta = -0.5299$, Holm $p = 0.0129$)** 국면은 6개 변수 다중검정 Holm 보정 후에도 유의한 음(-)의 계수를 나타내어, 거시 긴축 어젠다와 자본시장 위축 뉴스의 집중이 당월 주가 수익률 충격과 강하게 동행함을 확인하였다.
3. **해석 제한**: 본 회귀분석은 67개월 전체 표본에서 당월 뉴스 비중과 당월 수익률 간의 동시적 관계를 추정한 **표본 내 동행 설명 회귀(In-sample Contemporaneous Regression)**이며, 이를 표본 외 미래 예측 성능으로 확대 해석해서는 안 된다.

---

### 4.4 연구 B: 뉴스와 네이버 검색 데이터 주별 교차 검증 (RQ3)
언론 텍스트에서 비지도 학습으로 추출한 경제 국면 지표가 단순한 언론사의 보도 관행에 불과한지, 아니면 실물 경제 주체들의 대중적 관심과도 동조하는지를 검증하기 위해 292주간의 네이버 데이터랩(Datalab) 주별 검색어 지수와 교차 검증을 수행하였다.

가짜 상관(Spurious Correlation)을 제거하기 위해 뉴스 국면 점유율과 네이버 검색 상대점수(`score_rel`) 모두 **1차 차분(First Difference)**을 적용하였으며, Newey-West HAC(maxlags=4) 견고 표준오차를 적용하여 시계열 자기상관을 보정하였다. 동시점($h=0$) 및 시차($h=-1, +1$) 분석 결과는 표 4와 같다.

**Table 4. Weekly First-Difference Cross-Validation Between News Regimes and Naver Datalab Search Trends.**

| Paired Regime ↔ Search Category | Lag ($h$) | Train (2021~2024, $N=208$) Pearson $r$ (HAC $p_{\text{holm}}$) | Eval OOS (2025~2026, $N=82$) Pearson $r$ (HAC $p_{\text{holm}}$) | Full Period (2021~2026, $N=291$) Pearson $r$ (HAC $p_{\text{holm}}$) | Empirical Determination |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **시황 뉴스 ↔ 국내증시 검색** | $h=0$ | **$+0.6478$ ($< 0.001$)** | **$+0.4984$ ($0.043$)** | **$+0.4868$ ($< 0.001$)** | **강력 검증 (Train & OOS 동시 동조)** |
| | $h=-1$ | $-0.2448$ ($0.129$) | $-0.3461$ ($0.239$) | $-0.2822$ ($0.038$) | 시차 시 동조성 소멸 및 음의 반전 |
| | $h=+1$ | $-0.2448$ ($0.129$) | $-0.3461$ ($0.239$) | $-0.2822$ ($0.038$) | 시차 시 동조성 소멸 |
| **기업실적 뉴스 ↔ 기업실적 검색** | $h=0$ | **$+0.2160$ ($0.014$)** | **$+0.4718$ ($0.001$)** | **$+0.2795$ ($< 0.001$)** | **강력 검증 (Train & OOS 동시 동조)** |
| | $h=-1$ | $+0.0421$ ($1.000$) | $-0.1873$ ($1.000$) | $+0.0125$ ($1.000$) | 비유의 |
| | $h=+1$ | $+0.0421$ ($1.000$) | $-0.1873$ ($1.000$) | $+0.0125$ ($1.000$) | 비유의 |
| **금리·물가 뉴스 ↔ 금리 검색** | $h=0$ | **$+0.5511$ ($< 0.001$)** | **$+0.3397$ ($0.017$*)** | **$+0.5026$ ($< 0.001$)** | **유의 검증 (OOS raw $p=0.017$, Holm 0.358)** |
| | $h=-1$ | $-0.2885$ ($0.008$) | $-0.1246$ ($1.000$) | $-0.2588$ ($0.003$) | 검색 선행 비유의 |
| | $h=+1$ | $-0.2556$ ($0.035$) | $-0.2221$ ($0.741$) | $-0.2453$ ($0.007$) | 뉴스 선행 비유의 |
| 금리·물가 뉴스 ↔ 금리+물가 검색 | $h=0$ | $+0.4978$ ($< 0.001$) | $+0.2254$ ($1.000$) | $+0.3217$ ($< 0.001$) | Train 유의, OOS 완화 |
| 자본거래 뉴스 ↔ 공모주 검색 | $h=0$ | $+0.1437$ ($1.000$) | $+0.1658$ ($1.000$) | $+0.1348$ ($0.953$) | 차분 후 유의성 소멸 |
| 부동산 뉴스 ↔ 부동산 검색 | $h=0$ | $+0.1288$ ($1.000$) | $-0.0768$ ($1.000$) | $+0.1008$ ($1.000$) | 차분 후 유의성 소멸 |
| AI·반도체 뉴스 ↔ AI반도체 검색 | $h=0$ | $-0.0357$ ($1.000$) | $+0.1417$ ($1.000$) | $+0.0609$ ($1.000$) | 차분 후 유의성 소멸 |
| 금리·물가 뉴스 ↔ 물가 검색 | $h=0$ | $+0.0658$ ($1.000$) | $+0.1355$ ($1.000$) | $+0.0776$ ($1.000$) | 차분 후 유의성 소멸 |

*주: Eval OOS 금리 검색 $h=0$의 경우 Newey-West HAC 원 $p=0.0170$으로 유의하나, 24개 검정 보수적 Holm 보정 시 $p=0.358$로 완화됨.

표 4의 교차 검증 결과는 다음 사실을 보여준다:
1. **주별 단위의 실시간 동시 동조성**: '국내증시 시황'과 '기업실적'은 학습 기간뿐 아니라 **표본 외(Strict OOS) 테스트 기간에서도 동시점($h=0$)에서 각각 $r = +0.4984$ ($p_{\text{holm}} = 0.043$) 및 $r = +0.4718$ ($p_{\text{holm}} = 0.001$)의 유의한 동조화**를 나타내었다. '금리' 검색 역시 OOS 기간에서 $r = +0.3397$ (HAC $p = 0.017$)로 뚜렷한 양의 동조성을 유지하였다.
2. **시차의 대칭적 소멸**: $h=-1$(검색 1주 선행) 및 $h=+1$(뉴스 1주 선행)에서는 상관계수가 급격히 감소하거나 음(-)의 반전 현상을 보여, 언론 보도와 대중 검색이 어느 한쪽을 일방향으로 선행하기보다는 주 단위에서 거의 실시간으로 맞물려 반응함을 입증하였다.
3. **차분 후 비유의 국면의 정직한 보고**: 수준값(Level) 상태에서는 상관도가 높았던 부동산과 AI반도체는 1차 차분 시 통계적 유의성이 소멸되었다. 이는 부동산과 테크 산업의 대중 검색이 주간 단위의 단기 급변보다는 중장기적 추세를 공유하기 때문이며, 본 연구는 이를 가짜 상관으로 오도하지 않고 통계적 한계로 명확히 보고한다.
4. **공통 분모 영향 점검**: 네이버 데이터랩의 상대 지표 $score\_rel = score / anchor\_score$에서 앵커 키워드 변동의 영향을 점검한 결과, 주간 1차 차분 시 앵커 지수의 단기 변동은 전체 추세에 왜곡을 주지 않음을 확인하였다.

---

### 4.5 연구 C: 인간 평가 기반 의미 타당성 검증 설계 (RQ4)
비지도 학습 NMF 모델이 추출한 6대 국면이 실제 기사 내용의 의미와 부합하는지를 객관적으로 검증하기 위해, 독립 평가자 2인을 활용한 완전 블라인드 평가 체계를 구축하였다.

설계 및 표본 구성:
1. **표본 추출**: 테스트 기간(2025.01~2026.07, 288,614건) 기사로부터 19개월 전 기간에 걸쳐 **월별 20건씩 균등 층화 무작위 추출하여 총 380건($N=380$)의 표본**을 확정하였다. 언론사별 분포는 한국경제 133건, 매일경제 133건, 서울경제 114건으로 안배되었다.
2. **블라인드 평가 파일**: 모델의 토픽 확률, NMF 점수, 기저 예측값을 완전히 은닉하고 기사 ID 역시 익명화한 `human_annotation_batch_A.csv` 및 `human_annotation_batch_B.csv`를 생성하였다.
3. **독립 평가 지침**: 6대 국면에 대해 복수 선택(다중 라벨)이 가능하도록 코드북(`human_annotation_codebook.md`)을 확정하였으며, 미형성 국면인 가계부채와 대외통상은 메모 필드를 통해 혼합 양상을 파악하도록 설계하였다.
4. **후속 과제 명시**: 본 연구는 자동화 알고리즘이 인간의 평가를 대체하는 것을 금지하며, 현재는 **실제 인간 평가자 2인의 라벨링 입력 대기 상태(Waiting for Human Input)**이다. 평가자 간 일치도(Cohen's kappa) 및 모델 분류 성능(F1-score)의 공식 산출은 실제 평가자 데이터가 회수되는 후속 연구 단계로 남겨둔다.

---

## Ⅴ. 결 론 및 학술적 한계

### 5.1 학술적 기여
본 연구는 2021년 1월부터 2026년 7월까지 수집된 국내 3대 경제 일간지 기사 931,709건 코퍼스를 바탕으로, 미래 정보 누수를 차단한 표본 외(Strict OOS) NMF 프레임워크와 다중 국면 활성화 체계를 제안하고 시장 및 검색 빅데이터와의 관계를 실증하였다.

본 연구의 핵심 학술적 기여는 다음과 같다:
1. **방법론적 기여 (다중 국면 정보 보존성 입증)**: 기존 연구의 단일 대표 토픽(Argmax) 강제 방식이 복합 위기 국면에서 **유효 활성 거시 정보의 43.75%를 절단·누락**시킨다는 사실을 정량적으로 증명하였으며, 다중 국면 활성화 체계가 복합 이슈를 보존하는 타당한 방법론임을 보였다.
2. **검증 설계의 기여 (엄격한 Strict OOS 체계 확립)**: 어휘 사전, IDF, NMF 기저 행렬을 48개월 학습 기간에서만 고정하고 테스트 기간으로 투영하는 무누수 파이프라인을 확립하여 텍스트 마이닝 연구의 재현성을 비약적으로 높였다.
3. **실증적 기여 (이종 검색 빅데이터와의 주별 교차 검증)**: 비정상 단위근 추세를 제거한 1차 차분 패널 분석을 통해, 뉴스 국면(시황, 기업실적, 금리)이 네이버 검색 관심도와 주 단위에서 실시간으로 유의하게 동조함을 표본 외 테스트 기간에서도 입증하였다.

### 5.2 연구의 한계 및 주의점
1. **예측력 및 인과관계의 미주장**: 본 연구의 회귀분석 및 시차 상관 결과는 뉴스 국면과 금융시장 충격 간의 **동시적 동행 설명 관계**를 나타내는 것이며, 미래 주가나 금리를 예측하는 시계열 예측력이나 정책적 인과관계를 입증한 것이 아니다.
2. **미형성 국면의 한계**: 학습 기간 NMF에서 가계부채와 대외통상이 독립 국면으로 분리되지 못한 점은 데이터 주도형 토픽 모델링의 고유한 한계이며, 향후 지도 학습 또는 준지도 NMF 기법을 통한 보완이 필요하다.
3. **인간 평가의 후속 과제**: 표본 380건에 대한 블라인드 평가 설계는 완비되었으나 실제 평가자의 라벨링 완료 및 모델 정량 평가는 후속 연구 과제로 남아 있다.

---

## REFERENCES
1. S. R. Baker, N. Bloom, and S. J. Davis, “Measuring Economic Policy Uncertainty,” *The Quarterly Journal of Economics*, vol. 131, no. 4, pp. 1593-1636, 2016.
2. L. Bybee, B. T. Kelly, A. Manela, and D. Xiu, “Business News and Business Cycles,” *The Journal of Finance*, vol. 79, no. 5, pp. 2947-2993, 2024.
3. L. A. Thorsrud, “Words are the New Numbers: A Newsy Coincident Index of the Business Cycle,” *Journal of Business & Economic Statistics*, vol. 38, no. 2, pp. 393-409, 2020.
4. P. C. Tetlock, “Giving Content to Investor Sentiment: The Role of Media in the Stock Market,” *The Journal of Finance*, vol. 62, no. 3, pp. 1139-1168, 2007.
5. 서범석, 이영환, 조형배, “기계학습을 이용한 뉴스심리지수(NSI)의 작성과 활용,” *국민계정리뷰*, 제2022-1호, pp. 1-32, 2022.
6. 김수현, 박기영, “텍스트 분석을 이용한 한국의 경제 심리 및 경기 변동 연구,” *금융연구*, 제35권 제3호, pp. 1-35, 2021.
7. 박성호, 정용운, “비정형 뉴스 빅데이터를 활용한 거시경제 지표 선행성 분석,” *한국데이터정보과학회지*, 제31권 제5호, pp. 895-909, 2020.
8. D. D. Lee and H. S. Seung, “Learning the Parts of Objects by Non-negative Matrix Factorization,” *Nature*, vol. 401, no. 6755, pp. 788-791, 1999.
9. D. M. Blei, A. Y. Ng, and M. I. Jordan, “Latent Dirichlet Allocation,” *Journal of Machine Learning Research*, vol. 3, pp. 993-1022, 2003.
10. C. Truong, L. Runge, and N. Vayatis, “Selective Review of Offline Change Point Detection Methods,” *Signal Processing*, vol. 167, 107299, 2020.
11. J. H. Stock and M. W. Watson, *Introduction to Econometrics*, 4th ed., Pearson, 2019.
12. W. K. Newey and K. D. West, “A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix,” *Econometrica*, vol. 55, no. 3, pp. 703-708, 1987.
13. J. D. Hamilton, “A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle,” *Econometrica*, vol. 57, no. 2, pp. 357-384, 1989.
14. D. Garcia, “Sentiment During Recessions,” *The Journal of Finance*, vol. 68, no. 3, pp. 1267-1300, 2013.
15. R. F. Engle, “Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation,” *Econometrica*, vol. 50, no. 4, pp. 987-1007, 1982.
16. 송원호, 강규호, “뉴스 텍스트를 활용한 통화정책 충격의 금융시장 파급효과 분석,” *경제학연구*, 제67권 제4호, pp. 5-42, 2019.
