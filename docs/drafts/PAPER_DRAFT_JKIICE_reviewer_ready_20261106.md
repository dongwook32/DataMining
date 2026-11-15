# 뉴스 빅데이터와 NMF 기반의 한국형 경제 이슈 다중 국면 탐지 및 다각적 실증 검증
### Multi-Regime Detection of Korean Economic Issues via News Big Data and Non-negative Matrix Factorization: Methodological and Empirical Validations

**[ 저자 미정 (심사 대비 보강본) ]**  
한국성서대학교 AI융합학부 (*School of AI Convergence, Korean Bible University, Seoul, 01757 Korea*)

---

## 요 약
본 연구는 2021년 1월부터 2026년 7월까지(총 67개월) 국내 3대 주요 경제 일간지(매일경제, 서울경제, 한국경제)에서 수집한 931,709건의 경제 뉴스 기사 코퍼스를 대상으로 비지도 학습 기법인 비음수 행렬 분해(NMF)와 고정 표준화 체계를 구축하여 한국 경제의 잠재 이슈 국면을 탐지하고, 토픽 모델의 방법론적 타당성 및 시장·거시 지표, 대중 검색 빅데이터와의 관계를 실증 분석하였다. 미래 정보 누수(Data Leakage)를 원천 차단하기 위해 학습 기간(2021.01~2024.12, 48개월) 전용 어휘 사전(22,193개 단어)과 IDF, NMF 기저 행렬($H$, 14개 잠재 토픽)을 고정하여 테스트 기간(2025.01~2026.07, 19개월)으로 확장 투영하는 엄격한 표본 외(Strict Out-of-Sample) 파이프라인을 확립하였다. 동일 학습 표본(144,000건) 및 동일 어휘에서 잠재 디리클레 할당(LDA)과 정량 비교한 결과($K \in \{10, 12, 14, 16\}$), $K=14$ 기준 NMF는 LDA 대비 더 높은 토픽 응집도($C_v = 0.8258$ vs $0.7448$, $\text{NPMI} = 0.3011$ vs $0.2233$)와 어휘 다양성($\text{TD@20} = 0.9143$ vs $0.8036$), 빠른 연산 속도(학습 36.1초 vs 91.1초) 및 더 많은 유효 국면 분리(6개 vs 5개)를 달성하였다. 또한 80% 층화 부분표본 10회 반복 및 초기화 민감도 11회 실험(총 21회)에서 사전 정의된 매핑 규칙을 통과한 6대 유효 국면(금리·물가, 부동산, 첨단산업(전기차·배터리 중심), 시황, 기업실적, 자본거래)이 21회 전 실험(100%)에서 일관되게 재현됨을 확인하였다(80% 부분표본 평균 코사인 유사도 $0.8492$).

실증 분석 결과는 다음과 같다. 첫째, 한국 경제 뉴스는 전체 67개월의 58.21%(39개월; 학습 기간 66.67%, 테스트 기간 36.84%)에서 2개 이상의 경제 국면이 동시에 활성화되었다. 단일 대표 국면(Argmax) 방식으로 표현을 제한할 경우, 다중 국면 방식($z \ge 0.5$)에서 관측된 활성 국면 신호 중 43.75%(112건 중 49건; 학습 47.19%, 테스트 30.43%)가 별도 국면으로 표현되지 않으며, 객관적 규칙으로 선정된 5개 대표 사례 월(2021-09, 2022-10, 2023-08, 2026-01, 2026-02)의 실제 기사 가중치($W$) 추적을 통해 단일 방식에서 누락되는 제2·제3 국면(예: 2022-10 금리 인상기 부동산 경색 $z=+1.45$, 2026-02 증시 활황기 기업실적 공시 $z=+1.16$)의 실체를 확인하였다. 이는 표현상 정보 보존성에 관한 결과이며 예측 정확도의 개선을 의미하지는 않는다. 둘째, 67개월 전체 표본에서 6대 국면 표준화 점수와 코스피 과거 변동성 정규화 월간 수익률(`kospi_ret_std`) 간의 표본 내 동시점 Newey-West HAC OLS 회귀분석(maxlags=3) 결과, 모형 설명력 $R^2 = 16.19\%$ ($\text{Adj-}R^2 = 7.81\%$, HAC $F = 4.6833, p = 0.000573$)를 기록하였으며, '금리·물가'($\beta = -0.7418$, 원시 $p = 0.0004$, Holm $p = 0.0024$) 및 '자본거래'($\beta = -0.5299$, 원시 $p = 0.0026$, Holm $p = 0.0129$) 국면이 당월 주가 수익률 충격과 유의한 음(-)의 동행 관계를 형성함을 확인하였다(반면 월별 주가 하락 조기경보 규칙은 테스트 평가 가능 17개월에서 적중 0건으로 사전 예측력이 입증되지 않음). 셋째, 292주간의 네이버 데이터랩(Datalab) 주별 상대 검색 지수와의 1차 차분 교차 검증(유효 291주) 및 Newey-West HAC(maxlags=4, 24개 검정 Holm 보정) 검정 결과, 전체 기간 동시점($h=0$)에서 '금리·물가' ↔ 금리 검색($r = +0.5026, \text{HAC } p_{\text{holm}} = 1.29 \times 10^{-13}$), '시황' ↔ 국내증시 검색($r = +0.4868, \text{HAC } p_{\text{holm}} = 9.06 \times 10^{-5}$), '금리·물가' ↔ 금리+물가 검색($r = +0.3217, \text{HAC } p_{\text{holm}} = 5.07 \times 10^{-6}$), '기업실적' ↔ 기업실적 검색($r = +0.2795, \text{HAC } p_{\text{holm}} = 3.48 \times 10^{-5}$)의 양(+)의 동행 관계가 유의하였으며, 표본 외(Strict OOS) 테스트 기간($N=82$주)에서는 '시황' ↔ 국내증시 검색($r = +0.4984, \text{HAC } p_{\text{holm}} = 0.0432$)과 '기업실적' ↔ 기업실적 검색($r = +0.4718, \text{HAC } p_{\text{holm}} = 0.0011$) 두 쌍에서 통계적 유의성이 재현되었고 이동 블록 부트스트랩($L=4$주, $B=2,000$회) 95% 신뢰구간($[+0.2079, +0.6367]$, $[+0.2989, +0.5986]$)에서도 모두 0을 배제하였다('금리·물가' ↔ 금리 검색은 테스트 기간 $r = +0.3397$, HAC 원시 $p = 0.0170$이나 HAC Holm 보정 후 $p_{\text{holm}} = 0.3575$로 유의수준 미충족). 본 연구는 인과 추론이나 시장 예측력에 대한 과장된 주장을 배제하고, 토픽 모델 안정성, 다중 국면 정보 보존성, 그리고 이종 빅데이터 간 동시점 교차 동조성을 검증한 재현 가능한 텍스트 마이닝 프레임워크를 제시한다.

**키워드 :** 경제 뉴스 빅데이터, 텍스트 마이닝, 토픽 모델링, 비음수 행렬 분해(NMF), 다중 국면 활성화, 표본 외(Strict OOS) 검증, 네이버 데이터랩, 교차 데이터 검증

---

## ABSTRACT
This study establishes an unsupervised text-mining framework based on Non-negative Matrix Factorization (NMF) to detect latent economic issue regimes from 931,709 economic news articles collected from three major Korean business dailies (Maeil Business Newspaper, Seoul Economic Daily, and Korea Economic Daily) from January 2021 to July 2026 (67 months). To strictly prevent future information leakage, we constructed a deterministic Strict Out-of-Sample (OOS) pipeline where the vocabulary (22,193 terms), IDF weights, NMF basis matrix ($H$, 14 latent topics), and standardization parameters ($\mu_{\text{train}}, \sigma_{\text{train}}$) were fitted exclusively on the training period (2021.01–2024.12, 48 months) and projected onto the test period (2025.01–2026.07, 19 months). Under controlled comparisons against Latent Dirichlet Allocation (LDA) on the identical 144,000-document training sample and 22,193-term vocabulary ($K \in \{10, 12, 14, 16\}$), NMF ($K=14$) achieved higher topic coherence ($C_v = 0.8258$ vs. $0.7448$, $\text{NPMI} = 0.3011$ vs. $0.2233$), higher topic diversity ($\text{TD@20} = 0.9143$ vs. $0.8036$), faster computation (36.1s vs. 91.1s), and cleaner domain separation (6 vs. 5 valid regimes). Across 21 stability experiments (10 stratified 80% subsample runs and 11 initialization runs), the six valid regimes passing pre-specified mapping rules—Interest Rate & Inflation, Real Estate, Advanced Industry (EV/Battery-centered), Stock Market, Corporate Earnings, and Capital Transactions—were reproduced in 100% (21/21) of runs (mean cosine similarity $0.8492$ across 80% subsamples).

Empirical findings are threefold: First, Korean economic news exhibited concurrent activation of two or more regimes in 58.21% of the 67 months (39/67 months; 66.67% in training and 36.84% in out-of-sample testing). When representation is restricted to a single dominant regime per month, 43.75% (49 out of 112; 47.19% in training and 30.43% in testing) of the active regime signals observed under the multi-regime framework ($z \ge 0.5$) are not represented as separate regimes; article-level weight ($W$) tracing across five objectively selected case months (2021-09, 2022-10, 2023-08, 2026-01, 2026-02) confirms that single-regime representation omits substantive secondary regimes (e.g., housing market distress $z=+1.45$ during the October 2022 rate hike peak and corporate earnings shocks $z=+1.16$ during the February 2026 OOS market rally). This reflects representational information preservation rather than predictive accuracy. Second, in-sample Newey-West HAC OLS regression (maxlags=3) on volatility-standardized monthly KOSPI returns (`kospi_ret_std`, $N=67$) yielded $R^2 = 16.19\%$ ($\text{Adj-}R^2 = 7.81\%$, HAC $F = 4.6833, p = 0.000573$), with 'Interest Rate & Inflation' ($\beta = -0.7418$, raw $p = 0.0004$, Holm $p = 0.0024$) and 'Capital Transactions' ($\beta = -0.5299$, raw $p = 0.0026$, Holm $p = 0.0129$) showing statistically significant negative contemporaneous associations, whereas monthly early-warning rules showed zero true positives ($TP=0, FP=1$) in the 17 evaluable OOS months. Third, weekly first-differenced cross-validation across 291 differenced weeks against Naver Datalab relative search indices with Newey-West HAC standard errors (maxlags=4, 24-test Holm correction) confirmed significant contemporaneous ($h=0$) co-movement over the full period for Interest Rates ($r = +0.5026, \text{HAC } p_{\text{holm}} = 1.29 \times 10^{-13}$), Stock Market ($r = +0.4868, \text{HAC } p_{\text{holm}} = 9.06 \times 10^{-5}$), Combined Macro ($r = +0.3217, \text{HAC } p_{\text{holm}} = 5.07 \times 10^{-6}$), and Corporate Earnings ($r = +0.2795, \text{HAC } p_{\text{holm}} = 3.48 \times 10^{-5}$). In the Strict OOS test period ($N=82$ weeks), contemporaneous co-movement remained statistically significant for 'Stock Market' ↔ Domestic Stock search ($r = +0.4984, \text{HAC } p_{\text{holm}} = 0.0432$; Moving Block Bootstrap 95% CI $[+0.2079, +0.6367]$ at $L=4, B=2,000$) and 'Corporate Earnings' ↔ Corporate Earnings search ($r = +0.4718, \text{HAC } p_{\text{holm}} = 0.0011$; MBB 95% CI $[+0.2989, +0.5986]$), whereas 'Interest Rate & Inflation' ↔ Interest Rate search showed $r = +0.3397$ (raw HAC $p = 0.0170$) but did not remain significant after HAC Holm adjustment ($\text{HAC } p_{\text{holm}} = 0.3575$). Avoiding unverified claims of market forecasting or causality, this study provides a reproducible text-mining methodology for multi-regime representation and cross-source concordance analysis.

**Keywords :** Cross-Source Validation, Economic News Big Data, Multi-Regime Activation, Naver Datalab, Non-negative Matrix Factorization (NMF), Strict Out-of-Sample Validation, Text Mining, Topic Modeling

---

## Ⅰ. 서 론

현대 경제 시스템은 통화정책 긴축, 인플레이션 압력, 글로벌 공급망 재편, 그리고 자산시장 변동 등 다양한 거시경제 요인들이 복합적으로 상호작용하며 전개된다[1-3]. 이러한 거시 환경의 변화는 주식시장과 외환시장의 단기 가격 변동을 수반할 뿐만 아니라, 기업의 자본 조달과 경제 주체의 기대 형성에 영향을 미친다[4-6]. 이에 따라 정책 당국과 시장 참여자들은 거시경제 주요 어젠다의 변화를 정량적으로 파악하고 다원적 이슈 구조를 추적하기 위한 텍스트 정보 분석 체계를 필요로 하고 있다[7-10].

전통적인 거시경제 통계인 국내총생산(GDP), 소비자물가지수(CPI), 산업생산지수 등은 집계 및 공표 시차(Publication Lag)를 수반하며[3, 5], 사후적인 통계 수정(Revision)이 발생할 수 있어 고빈도로 변화하는 경제 현안을 실시간으로 요약하는 데 제약이 있다[2, 6]. 이를 보완하기 위해 최근 정보처리 및 금융 빅데이터 분야에서는 매일 대량으로 생성되는 비정형 뉴스 텍스트(News Text) 빅데이터로부터 경제정책불확실성(EPU)[1], 뉴스심리지수(NSI)[5, 9], 주제별 빈도 요인(TFI)[6], 잠재 토픽 관심도(Topic Attention)[2, 3]를 도출하여 거시 현안을 추적하려는 연구가 활발히 진행되어 왔다.

그러나 비정형 텍스트 기반 거시 이슈 국면 분석을 다룬 기존 국내외 연구들은 방법론적 검증, 정보 표현, 그리고 실증 설계 측면에서 다음과 같은 네 가지 한계를 나타낸다.

첫째, **토픽 모델 선택(NMF vs LDA)의 실증적 정당화 및 표본·초기화 안정성 검증의 부족**이다. 기존 경제·사회 뉴스 토픽 모델링 연구들은 관행적으로 확률적 잠재 디리클레 할당(LDA)[2, 3, 7, 18, 19]을 채택하거나 단일 난수 시드 적합 결과만을 보고하는 경우가 많다. 그러나 명사 키워드 중심의 대규모 경제 뉴스 코퍼스에서 TF-IDF 기반 비음수 행렬 분해(NMF)와 빈도 기반 LDA가 토픽 응집도(Coherence), 어휘 다양성(Topic Diversity), 경제 도메인 분리도에서 어떠한 차이를 보이는지, 그리고 추출된 토픽과 국면 매핑이 학습 표본 재추출이나 초기화 변경에도 안정적으로 재현되는지를 통제된 실험으로 입증한 연구는 드물다[13, 14].

둘째, **단일 대표 국면(Single Dominant Regime) 선택 또는 단일 지수 축약으로 인한 복합 이슈 표현의 제한**이다. 기존 연구들은 다차원 경제 기사를 단일 불확실성·감성 지수로 압축하거나[1, 5, 9], 각 시점에서 출현 비중이 1위인 토픽만을 대표 국면으로 강조하는 방식을 주로 채택하였다. 그러나 현실 경제에서는 고물가·금리 인상 충격과 부동산 시장 경색, 또는 증시 변동과 기업실적 공시가 같은 달에 동시에 부각되는 복합 현상이 빈번하다. 월별 대표 국면 1개만을 선택하여 표현을 제한할 경우, 동일한 시점에 임계 수준 이상으로 활성화된 제2·제3의 유효 국면 신호가 별도의 국면으로 표현되지 못하는 정보 손실이 발생한다.

셋째, **표본 외(Out-of-Sample) 검증 설계의 미흡과 미래 정보 누수(Data Leakage)**이다. 많은 텍스트 마이닝 연구들이 전체 분석 기간의 모든 문서를 한꺼번에 투입하여 어휘 사전을 구축하고 토픽 모델 및 표준화 모수를 적합한 뒤, 그 결과를 과거와 미래 시점에 동일하게 적용한다[10]. 이는 평가 기간에 아직 발생하지 않은 미래의 어휘 분포와 토픽 구조가 과거 시점의 지표 산출에 반영되는 정보 누수(Look-ahead Bias)를 야기하며, 텍스트 특징 추출의 표본 외 동결과 회귀모형의 표본 내 설명력 평가가 혼동되는 문제를 낳는다.

넷째, **이종 빅데이터를 활용한 주별 차분 교차 검증 및 시계열 정상성·유한 표본 강건성 통제의 부족**이다. 비지도 학습으로 추출된 뉴스 토픽 지표가 언론사의 보도 관행에 그치는지, 아니면 일반 대중의 정보 탐색 행동(검색 트렌드)과도 동시점에 동조하는지를 독립된 외부 데이터로 교차 검증한 연구가 부족하였다[15-17]. 또한 시계열 수준값(Level)의 비정상성(단위근 추세)을 제거하지 않은 채 단순 상관계수를 보고하거나, 자기상관(HAC) 시차 민감도 및 비모수 블록 부트스트랩 검증을 생략할 경우 가짜 상관(Spurious Correlation)을 유의한 관계로 오인할 위험이 크다.

이에 본 연구는 2021년 1월부터 2026년 7월까지(총 67개월) 국내 3대 경제 일간지(매일경제, 서울경제, 한국경제)에서 수집한 931,709건의 경제 뉴스 기사 코퍼스를 바탕으로 NMF 기반 한국형 경제 이슈 다중 국면 탐지 체계를 구축하고, 심사 가능한 수준의 방법론적·통계적 강건성 검증을 수행한다.

본 연구가 규명하고자 하는 핵심 연구 질문(Research Questions)은 다음과 같다:
- **RQ1 (토픽 모델 타당성 및 안정성 검증)**: 동일 한국 경제 뉴스 학습 코퍼스에서 NMF는 LDA 대비 어떠한 토픽 품질·다양성·도메인 분리 특성을 보이며(연구 A), 도출된 14개 토픽과 6대 유효 국면 매핑은 80% 층화 부분표본 재추출 및 초기화 변경에 대해 안정적으로 재현되는가(연구 B)?
- **RQ2 (단일 국면과 다중 국면 활성화 비교 및 실제 기사 검증)**: 다중 국면 동시 활성화 방식($z \ge 0.5$)과 단일 대표 국면 선택 방식은 활성 국면 신호 표현에서 어떠한 정량적 차이를 보이며, 실제 코퍼스 기사(`W` 가중치) 수준에서 어떤 복합 경제 이슈를 보존하는가(연구 C)?
- **RQ3 (Strict OOS 적용 범위 구분 및 시장·거시 지표 관계 분석)**: 학습 기간 고정 특징 추출(Strict OOS)과 전체 표본 동시점 회귀분석의 적용 경계는 무엇이며(연구 E), 6대 유효 국면은 코스피 수익률 충격 및 기준금리 변동과 어떠한 동행·시차 관계와 조기경보 한계를 보이는가?
- **RQ4 (네이버 검색 데이터를 이용한 주별 교차 데이터 검증 및 강건성)**: 뉴스 국면 점유율의 주간 1차 차분은 네이버 데이터랩 상대 검색 지수의 주간 차분과 Newey-West HAC 시차(`maxlags=2,4,8`), 다중검정 보정, 이동 블록 부트스트랩(`B=2,000`), 공통 앵커 분모 민감도 하에서 강건한 동시점 동조화를 나타내는가(연구 D)?

---

## Ⅱ. 관련 연구 및 이론적 배경

### 2.1 뉴스 텍스트 기반 거시경제 지표 및 시장 반응
텍스트 데이터를 계량경제학적 분석에 도입한 대표적 연구인 Baker, Bloom, and Davis[1]는 주요 신문 기사에서 '경제', '정책', '불확실성' 관련 키워드의 출현 빈도를 집계하여 경제정책불확실성(EPU) 지수를 개발하였다. Tetlock[4]과 García[23]는 일간 금융 칼럼의 감성 어휘가 주식시장 수익률 및 거래량과 유의한 관련성을 맺음을 보였고, Shapiro, Sudhof, and Wilson[9]은 미국 16개 주요 일간지 기사 24만 건에서 뉴스 감성 지수를 구축하여 거시 충격 반응을 분석하였다. 이후 텍스트 분석 연구는 단어 빈도·감성 계측에서 비지도 토픽 모델링으로 확장되었다. Bybee et al.[2]은 월스트리트저널(WSJ) 기사 약 80만 건을 LDA 토픽 모델링($K=180$)으로 분석하여 거시경제 주제 비중(Attention) 시계열을 도출하였고, Thorsrud[3]는 노르웨이 경제 일간지의 토픽 비중을 동적 요인 모형(DFM)과 결합하여 경기 동행 지수를 구축하였다. 또한 Glasserman and Mamaysky[10]는 과거 학습 창을 기준으로만 뉴스 비정상성(Unusualness)을 산출하여 미래 정보 누수(Look-ahead Bias)를 차단한 금융 시장 스트레스 분석을 제시하였다.

국내에서도 텍스트 마이닝을 활용한 거시경제 및 금융 연구가 활발히 진행되었다. 서범석·이영환·조형배[5]는 기계학습 기반 뉴스심리지수(NSI)를 개발하여 소비자심리지수(CCSI) 등과의 동행·선행성을 분석하였고, Seo[6]는 한국 뉴스 1,800만 건에서 주어-서술어 패턴 기반의 15개 경제 부문 주제빈도지수(TFI)를 도출하여 텍스트 강화 요인 모형(TFM)을 통한 GDP 예측을 수행하였다. 김수현·이영준·신진영·박기영[7]은 한국은행 금융통화위원회 의사록과 경제 뉴스 텍스트를 활용한 거시경제 분석 프레임워크를 정리하였으며, Kim and Lee[8]는 23년치 한국 경제 뉴스 보도량·논조와 거시지표(GDP, 물가, 실업률, 주가지수) 및 대중 경제심리 간의 상호 시계열 동학을 규명하였다. 국내 정보통신·산학 응용 학술지에서도 정용한 외[18]가 뉴스 LDA 토픽과 단기 주가 변동을 연계하였고, 김윤하·황보준권[19]이 한국정보통신학회논문지(JKIICE)에서 빅카인즈 뉴스 토픽 모델링 기반 연도별 동향 분석을 수행하였다.

### 2.2 비음수 행렬 분해(NMF)와 LDA의 이론적 차이 및 고정 특징 투영
문서 집합에서 잠재 주제를 추출하는 대표적인 두 기법은 확률 생성 모형인 LDA[12]와 선형대수적 행렬 분해 기법은 NMF[11]이다. LDA는 디리클레 사전분포 하에서 문서-단어 출현 빈도(Count) 행렬을 다항분포 혼합으로 모델링하는 반면, NMF는 TF-IDF 등으로 가중된 문서-어휘 행렬 $V \in \mathbb{R}^{N \times M}_+$를 두 개의 저차원 비음수 행렬 $W \in \mathbb{R}^{N \times K}_+$와 $H \in \mathbb{R}^{K \times M}_+$의 곱으로 근사 분해한다[11]:

$$V \approx W \times H \quad (\text{단, } W \ge 0, H \ge 0) \tag{1}$$

여기서 $W$는 각 문서가 $K$개 잠재 토픽에 갖는 가중치 행렬이며, $H$는 각 토픽이 $M$개 어휘에 갖는 단어 가중치 행렬이다. O'Callaghan et al.[13]과 Egger and Yu[14]가 실증한 바와 같이, 뉴스 기사와 같이 전 문서에 걸쳐 일반적인 상투어(고빈도 일반 명사)가 반복되는 코퍼스에서 빈도 행렬에 기반한 LDA는 일반 어휘가 여러 토픽의 상위어를 점유하여 도메인 간 경계가 흐려지는(Generality bias) 경향이 있다. 반면 TF-IDF 가중치와 결합된 NMF는 비음수 제약을 통한 가산적 부분 기반 표현(Part-based Representation)을 형성하여 도메인 특유 어휘를 선명하게 분리하며, 결정론적 특이값 분해 초기화(`nndsvd`)와 좌표 하강법을 사용할 때 완벽한 수치적 재현성을 보장한다.

특히 표본 외(Strict OOS) 평가를 수행할 때, 학습 기간(Train) 문서에서 적합된 기저 행렬 $H_{\text{train}}$과 IDF 가중치를 고정(Freeze)한 뒤, 테스트 기간(Eval)의 새로운 문서 행렬 $V_{\text{eval}}$에 대해 $W_{\text{eval}} \approx \arg\min_{W \ge 0} \| V_{\text{eval}} - W H_{\text{train}} \|_F$를 투영함으로써 평가 기간의 미래 텍스트 정보가 토픽 기저 형성에 개입하는 것을 원천 차단할 수 있다.

### 2.3 시계열 정상성, Newey-West HAC 공분산, 다중검정 및 블록 부트스트랩
거시경제 및 뉴스·검색 시계열 데이터는 자기상관(Autocorrelation)과 이분산성(Heteroskedasticity)을 수반하며[20, 22, 24], 수준값(Level) 시계열이 단위근 추세를 공유할 경우 실제 단기 동조성이 없더라도 높은 상관계수가 산출되는 가짜 상관(Spurious Correlation)이 발생한다[15]. 본 연구에서는 단위근 추세에 의한 착시를 방지하기 위해 상관 및 교차 검증 시 지수 수준값 대신 **월간 수익률·차분 또는 주간 1차 차분(First Difference)** 변환 시계열을 사용한다. 또한 회귀분석 및 주별 상관 검정 시 Newey and West[21]의 HAC(Heteroskedasticity and Autocorrelation Consistent) 견고 공분산 추정량(Bartlett 커널)을 적용한다:

$$V_{\text{HAC}} = (X'X)^{-1} \left[ \Gamma_0 + \sum_{l=1}^{q} \left(1 - \frac{l}{q + 1}\right) (\Gamma_l + \Gamma_l') \right] (X'X)^{-1} \tag{2}$$

아울러 복수의 국면·지표·시차를 동시에 검정할 때 발생하는 제1종 오류(Family-wise Error Rate) 팽창을 통제하기 위해 모든 다중 가설 패밀리에 대해 Holm-Bonferroni 단계적 보정($p_{\text{holm}}$)을 적용하며, 유한 표본($N=82$주 등)에서 점근적 정규근사에만 의존하는 한계를 보완하기 위해 시계열 블록 구조를 보존하는 이동 블록 부트스트랩(Moving Block Bootstrap, MBB) 신뢰구간을 병행 검증한다.

### 2.4 국내외 선행연구와의 구조적 비교 및 본 연구의 차별성
기존 국내외 대표 연구들과 본 연구의 방법론적·실증적 차이를 요약하면 표 F-1과 같다.

**Table F-1. Structural Comparison Between Prior Domestic/International Studies and the Proposed Framework.**

| 연구자 (연도) | 데이터 출처 및 규모 | 텍스트/토픽 기법 | 이슈 표현 방식 | 토픽 모델 비교 및 안정성 검증 | Strict OOS 기저 동결 | 검색 트렌드 교차 검증 |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Baker et al. (2016)** [1] | 미국 10대 일간지 등 다수 | 불리언 키워드 빈도 (EPU) | 단일 정책불확실성 지수 | 미수행 (고정 사전) | 고정 사전 | 미수행 (VIX 등 대조) |
| **Glasserman & Mamaysky (2019)** [10] | 금융사 뉴스 36만 건 (`1996~2014`) | N-gram 엔트로피 + 감성 사전 | 스칼라 비정상성·감성 점수 | 미수행 | 적용 (과거 롤링 창) | 미수행 (변동성 대조) |
| **Thorsrud (2020)** [3] | 노르웨이 경제지 45만 건 (`1990~2016`) | LDA ($K=80$) + 동적요인모형 | 단일 경기동행지수로 압축 | 미수행 (LDA 단일) | 부분 적용 (LDA는 전 기간 적합) | 미수행 (GDP 나우캐스팅) |
| **Bybee et al. (2024)** [2] | 미국 WSJ 80만 건 (`1984~2017`) | LDA ($K=180$) | 연속형 토픽 비중 (단일 vs 다중 미비교) | 미수행 (LDA 단일) | 미적용 (전 기간 LDA 적합) | 미수행 (실물·증시 회귀) |
| **서범석 외 (2022) [5] / Seo (2025) [6]** | 한국 뉴스 일별 / 1,800만 건 | 트랜스포머 감성 / 주어-서술어 TFI | 단일 NSI 지수 / 15개 부문 빈도요인 | 미수행 (비지도 토픽 미사용) | 의사 표본 외 예측 | 미수행 (CCSI, GDP 대조) |
| **Kim & Lee (2026)** [8] | 한국 빅카인즈 경제 뉴스 (23년) | 월별 보도량 및 감성 논조 (VAR) | 거시 이슈별 보도량·논조 | 미수행 | 미적용 (전체 기간 시계열) | 미수행 (서베이 심리지수) |
| **Youk et al. (2026) [16] / Cho (2026) [17]** | 빅카인즈 뉴스 / 네이버 검색 | 키워드 빈도 / AI 검색 열기 지수 | 2개 환경이슈 경쟁 / 단일 AI 섹터 | 미수행 | 미적용 | 적용 (비경제 이슈 / AI 단일) |
| **김윤하·황보준권 (2024, JKIICE)** [19] | 빅카인즈 마약 뉴스 (`2021~2023`) | LDA 토픽 모델링 | 연도별 토픽 키워드 기술 | 미수행 (LDA 단일) | 미적용 | 미수행 (기술적 동향 분석) |
| **본 연구 (Proposed Study)** | **빅카인즈 3대 경제지 931,709건 (`2021.01~2026.07`)** | **TF-IDF + NMF ($K=14$, `nndsvd`)** | **규칙 기반 6대 국면 + 다중 활성화 ($z \ge 0.5$)** | **NMF vs LDA ($K=10\sim16$) 및 21회 안정성 검증** | **완전 적용 (어휘·IDF·$H$·$\mu,\sigma$ 학습 48개월 동결)** | **주별 1차 차분 네이버 검색 HAC·Holm·MBB($B=2,000$) 검증** |

---

## Ⅲ. 연구 방법, 모델 타당성 검증 및 Strict OOS 시스템 설계

### 3.1 경제 뉴스 코퍼스 및 전처리
텍스트 데이터는 한국언론진흥재단 빅카인즈(BigKinds)를 통해 2021년 1월 1일부터 2026년 7월 31일까지(총 67개월) 국내 3대 경제 일간지인 **매일경제, 서울경제, 한국경제**의 경제 섹션 기사 전량을 수집하였다. 저작권 보호로 본문 200자 절단이 적용되는 원문 요약 대신, 기사 전문에서 추출된 형태소 분석 명사 키워드 필드(`keywords`)를 사용하였다. 수집된 원시 데이터 931,709건은 결측치 및 중복(`article_id`) 검사 후 931,709건 전량이 분석 코퍼스로 확정되었다(어휘 사전에 매칭되는 토큰이 전혀 없는 11건만 월별 비중 분모에서 제외됨).

거시금융 시장 지표는 한국은행 경제통계시스템(ECOS) 등을 통해 월별 패널(`monthly_panel.csv`, 67개월)로 구축하였다:
1. **코스피 월간 로그수익률 (`kospi_ret`)**: $\text{kospi\_ret}_t = 100 \times \ln(\text{KOSPI}_t / \text{KOSPI}_{t-1})$ ($\%$)
2. **과거 변동성 정규화 월간 수익률 (`kospi_ret_std`)**: $\text{kospi\_ret\_std}_t = \text{kospi\_ret}_t / \text{kospi\_vol12}_{t-1}$, 여기서 $\text{kospi\_vol12}_t = \operatorname{SD}(\text{kospi\_ret}_{t-11 : t})$는 직전 12개월 월간 수익률의 표본 표준편차이다. 이는 변동성 수준 자체가 아니라 과거 변동성 크기로 스케일을 조정한 월간 수익률 충격 지표이다.
3. **거시 변동 지표**: 한국은행 기준금리 월간 변화폭(`base_rate_diff` $= \text{BASE\_RATE}_t - \text{BASE\_RATE}_{t-1}$), 소비자심리지수 월간 변화분(`ccsi_diff`), 원/달러 환율 월간 로그수익률(`usdkrw_ret`).

대중 검색 관심도 대조를 위해서는 네이버 데이터랩(Datalab) Search Trend API를 통해 고정 조회 기간(`2016-01-01 ~ 2026-07-31`) 동안 각 검색어 그룹을 공통 앵커 키워드(`'은행'`)와 함께 조회하여 일별 원시 상대지수(`score`, 그룹 내 최대 검색일=100 기준)와 앵커 대비 상대지수(`score_rel = score / anchor_score`)를 수집하고, 뉴스 코퍼스와 동일한 ISO 8601 주차(`iso_yw`) 기준 주별 평균으로 집계하였다.

### 3.2 TF-IDF와 NMF 기반 경제 이슈 토픽 추출 및 LDA 대안 모델과의 정량 비교 (연구 A)
본 연구는 미래 정보 누수를 원천 차단하기 위해 전체 67개월을 다음과 같이 고정 분할하였다(`RUN_PHASE5_6_20261027_184959`):
- **학습 기간 (Train)**: `2021-01 ~ 2024-12` (48개월, 기사 643,095건)
- **표본 외 테스트 기간 (Eval OOS)**: `2025-01 ~ 2026-07` (19개월, 기사 288,614건)

모든 텍스트 특징 선택과 모델 적합은 학습 기간(48개월) 내부에서만 수행되었다:
1. **어휘 사전(Vocabulary)**: 학습 기간 643,095건 기사에서 최소 문서빈도 `MIN_DF = 200`, 최대 문서빈도 비율 `MAX_DF_RATIO = 0.15`, 상한 30,000개 조건을 적용하고 `(-DF, 토큰 사전순)`으로 정렬하여 최종 **22,193개 어휘**를 확정하였다.
2. **IDF 및 NMF 적합 표본**: 학습 기간 48개월에서 월별 3,000건씩 층화 비복원 추출(`seed=42`)한 144,000건의 학습 표본(`fit_sample_ids.csv`)에 대해 `TfidfTransformer`(`norm='l2', smooth_idf=True`)와 NMF(`n_components=14, init='nndsvd', solver='cd', max_iter=400, random_state=42`)를 단 1회 적합하여 기저 행렬 $H_{\text{train}}$ ($14 \times 22,193$)을 고정하였다(재실행 검증 시 기존 아티팩트 `nmf_H.npy`와 최대 절대 오차 `0.000e+00`로 완벽히 일치함).
3. **전 기간 변환 및 월별·주별 집계**: 고정된 어휘 사전, IDF, $H_{\text{train}}$에 전체 문서를 `transform` 방식으로만 투영하여 문서별 토픽 가중치 $W_{i,k}$를 산출하고, 유효 문서($\sum_k W_{i,k} > 0$)의 정규화 토픽 비중 $w_{i,k} = W_{i,k} / \sum_{k=0}^{13} W_{i,k}$를 월별 및 ISO 주차별로 평균하였다.

왜 확률적 토픽 모델인 LDA 대신 TF-IDF 기반 NMF를 채택하였는지 실증적으로 검증하기 위해, **동일한 학습 표본(144,000건)과 동일한 어휘 사전(22,193개)**, 그리고 학습 표본에 포함되지 않은 나머지 학습 문서에서 월별 1,000건씩 층화 추출한 **48,000건의 학습 내부 검증 표본(Internal Validation Set)**을 사용하여 토픽 수 $K \in \{10, 12, 14, 16\}$ 구간에서 NMF와 LDA(`LatentDirichletAllocation`, 문서-단어 빈도 행렬 입력, `learning_method='online', batch_size=4096, max_iter=10, random_state=42`)를 통제 비교하였다(`topic_model_comparison_metrics.csv`). 비교 결과는 표 A-1과 같다.

**Table A-1. Controlled Comparison Between NMF and LDA Across $K \in \{10, 12, 14, 16\}$ on the Identical Training Corpus (N=144,000 Fit / N=48,000 Internal Validation, 22,193 Vocabulary).**

| 모델 ID (`model_id`) | 토픽 수 ($K$) | $C_v$ (Train 643k) | NPMI (Train 643k) | $U_{\text{mass}}$ | $C_v$ (Val 48k) | NPMI (Val 48k) | TD@10 | TD@20 | Redundancy@20 | 평균 유효 어휘 수 | 할당 토픽 수 | 성립 유효 국면 수 | 학습 시간 (s) | 변환 시간 (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **NMF_K10** | 10 | $0.8337$ | $0.3054$ | $-1.4662$ | $0.8345$ | $0.3070$ | $0.9900$ | $0.9650$ | $0.0350$ | $2,629.5$ | 7/10 | **6개** (`macro;realestate;aichip;market;earnings;capital`) | 6.8 | 0.10 |
| **LDA_K10** | 10 | $0.7374$ | $0.2132$ | $-1.7000$ | $0.7398$ | $0.2150$ | $0.8900$ | $0.8500$ | $0.1500$ | $2,171.7$ | 4/10 | **4개** (`macro;realestate;aichip;capital`) | 100.0 | 1.74 |
| **NMF_K12** | 12 | $0.8356$ | $0.3029$ | $-1.5904$ | $0.8357$ | $0.3039$ | $0.9667$ | $0.9083$ | $0.0917$ | $2,318.2$ | 9/12 | **7개** (`macro;realestate;hhdebt;aichip;market;earnings;capital`) | 10.1 | 0.12 |
| **LDA_K12** | 12 | $0.7438$ | $0.2197$ | $-1.6685$ | $0.7450$ | $0.2206$ | $0.9083$ | $0.8375$ | $0.1625$ | $1,982.7$ | 5/12 | **4개** (`macro;realestate;aichip;capital`) | 91.1 | 1.46 |
| **NMF_K14 (Phase 5.6 기준)** | **14** | **$0.8258$** | **$0.3011$** | **$-1.6217$** | **$0.8261$** | **$0.3020$** | **$0.9643$** | **$0.9143$** | **$0.0857$** | **$2,188.5$** | **8/14** | **6개 (`macro;realestate;aichip;market;earnings;capital`)** | **36.1** | **0.14** |
| **LDA_K14 (주 비교 모형)** | **14** | **$0.7448$** | **$0.2233$** | **$-1.7351$** | **$0.7466$** | **$0.2246$** | **$0.8714$** | **$0.8036$** | **$0.1964$** | **$1,845.9$** | **8/14** | **5개 (`macro;realestate;trade;aichip;capital`)** | **91.1** | **1.45** |
| **NMF_K16** | 16 | $0.8434$ | $0.3200$ | $-1.6784$ | $0.8417$ | $0.3204$ | $0.9437$ | $0.8750$ | $0.1250$ | $1,949.7$ | 12/16 | **7개** (`macro;realestate;hhdebt;aichip;market;earnings;capital`) | 9.1 | 0.16 |
| **LDA_K16** | 16 | $0.7758$ | $0.2432$ | $-1.6891$ | $0.7752$ | $0.2430$ | $0.8500$ | $0.8094$ | $0.1906$ | $1,736.7$ | 8/16 | **6개** (`macro;realestate;hhdebt;trade;aichip;capital`) | 89.9 | 1.42 |

표 A-1 및 $K=14$ 기준 Hungarian 최적 토픽 정렬(`topic_alignment.csv`) 결과는 다음의 방법론적 시사점을 제공한다:
1. **토픽 응집도 및 어휘 다양성 우위**: $K=14$ 기준 NMF는 학습 전체 코퍼스(643,095건)에서 $C_v = 0.8258$, $\text{NPMI} = 0.3011$ (내부 검증 48,000건에서 $C_v = 0.8261, \text{NPMI} = 0.3020$)을 기록하여 LDA($C_v = 0.7448, \text{NPMI} = 0.2233$)보다 높은 단어 동시출현 응집도를 보였다. 특히 상위 20개 핵심어의 고유 비율인 Topic Diversity@20은 NMF가 $0.9143$(중복도 Redundancy@20 $= 0.0857$)인 반면 LDA는 $0.8036$(중복도 $0.1964$)으로, LDA에서는 고빈도 일반 경제 명사들이 여러 토픽에 중복 출현하였다.
2. **핵심 금융·실적 국면 분리 능력 차이**: 동일한 규칙 기반 매핑 함수(`map_topics`)를 적용했을 때, NMF는 $K \in \{10, 12, 14, 16\}$ 전 구간에서 `market`(시황)과 `earnings`(기업실적)를 포함한 6~7개 유효 국면을 일관되게 분리하였다. 반면 LDA는 $K=14$에서 증시·실적·금리 어휘가 단일 토픽(L9: `주가, 하락, 실적, 증시, 지수, 달러, 연구원, 금리, 주식, 매수`)에 혼합되어 `macro`로 흡수됨으로써 전 $K$ 구간에서 `market`과 `earnings` 국면을 독립 토픽으로 분리하지 못하였다.
3. **연산 효율성 및 $K=14$ 고정 원칙**: 144,000건 적합 시간(NMF $36.1$초 vs LDA $91.1$초)과 48,000건 변환 시간(NMF $0.14$초 vs LDA $1.45$초) 모두 NMF가 현저히 빨라 93만 건 대규모 Strict OOS 투영에 적합하였다. 한편 $K=12, 16$ NMF에서는 `hhdebt`까지 7개 국면이 분리되었으나, 본 연구는 사후적 모형 선택(Post-hoc Model Selection)을 배제하기 위해 사전 확정된 Phase 5.6의 $K=14$ 모델을 그대로 유지한다.

### 3.3 14개 토픽에서 6개 유효 경제 국면으로의 매핑 및 안정성 검증 (연구 B)
토픽 번호에 대한 자의적 개입을 배제하기 위해, 사전 구축된 8개 경제 도메인 키워드 사전(`DOMAIN_SPEC`)과 학습 기저 행렬 $H_{\text{train}}$만을 입력으로 하는 규칙 기반 자동 매핑 함수(`map_topics`)를 적용하였다. 각 토픽에서 1위 도메인의 어휘 가중치 점유율(`best_share`)이 `0.01`(`MIN_MAP_SHARE`) 미만이면 `residual`(잔차), 2위 도메인과의 질량 비율(`second_mass / best_mass`)이 `0.90`(`MASS_TIE_RATIO`) 이상이면 `ambiguous`(경합·모호), 두 조건을 모두 통과하면 1위 도메인으로 `assigned`(할당) 판정하였다.

학습 기간 14개 잠재 토픽(`토픽 0 ~ 13`)의 실제 상위 키워드와 매핑 결과는 다음과 같다:
- **할당된 6대 유효 국면 (총 8개 토픽 할당)**:
  - **`macro` (금리·물가, 1개 토픽)**: **토픽 1** (`물가, 금리, 경제, Fed, 인상, 인플레이션, 통화, 경기, 연방, 중앙은행, 정책, 기준금리` — `macro` 점유율 `0.0472`, 2위/1위 비율 `0.191`, 신뢰도 `0.809`)
  - **`realestate` (부동산, 2개 토픽)**: **토픽 2** (`대출, 주택, 금리, 부동산, 은행, 아파트, 전세, 집계, 포인트, 매매, 집값, 담보` — `realestate` 점유율 `0.0284`, 2위 `hhdebt`와의 비율 `0.664`) + **토픽 3** (`단지, 분양, 가구, 아파트, 지상, 지하, 전용, 인근, 청약, 조성, 주택, 입주` — `realestate` 점유율 `0.0403`, 2위/1위 비율 `0.009`)
  - **`aichip` (첨단산업(전기차·배터리 중심), 1개 토픽)**: **토픽 12** (`차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, SUV, 성능, 기아, 충전, 배터리, 전기` — `aichip` 점유율 `0.0125`, 2위/1위 비율 `0.027`, 우세 세부 그룹 `전기차배터리`)
  - **`market` (시황, 2개 토픽)**: **토픽 4** (`종목, 매수, 외국인, 지수, 순매도, 주가, 하락, 삼성전자, 증시, 상위, 시가, 코스피` — `market` 점유율 `0.0343`, 2위/1위 비율 `0.381`) + **토픽 13** (`코스닥, 출발, 개장, 마감, 코스피, 거래일, 종료, 포인트, 상장, 공모가, 하락, 보통주추가상장` — `market` 점유율 `0.2651`, 2위/1위 비율 `0.081`)
  - **`earnings` (기업실적, 1개 토픽)**: **토픽 7** (`영업, 이익, 전년, 영업이익, 실적, 매출액, 공시, 연결, 감소, 영업익, 순이익, 분기` — `earnings` 점유율 `0.0189`, 2위/1위 비율 `0.181`)
  - **`capital` (자본거래, 1개 토픽)**: **토픽 6** (`상장, 주식, 투자자, 펀드, 자산, 지분, 보유, 자금, 수익, 운용, 주주, IB, 인수, ETF, 공모, 매각, 발행, IPO` — `capital` 점유율 `0.0222`, 2위/1위 비율 `0.234`)
- **미형성 국면 (`unrepresented / NaN`, 2개 도메인)**:
  - **가계대출(`hhdebt`)**은 토픽 2에서 `realestate`에 차순위(질량비 `0.664`)로 흡수되어 독립 토픽을 형성하지 못하였으며, **대외통상(`trade`)**은 토픽 0(점유율 `0.0012 < 0.01`)과 토픽 8(`aichip`과 경합비 `0.951 >= 0.90`)이 임계 규칙을 통과하지 못하여 미형성 처리되었다.
- **비할당 잔차·경합 토픽 (`residual / ambiguous`, 6개 토픽)**:
  - **토픽 0** (`경영, 환경, 사회, ESG, 지배구조, 탄소` — `residual`), **토픽 5** (`브랜드, 고객, 상품, 구매, 출시, 매장, 할인` — `residual`), **토픽 8** (`공장, 수출, 중국, 제조, 반도체, 확보, 유럽, 소재, 장비, 배터리` — `trade` 1위·`aichip` 2위 경합비 `0.951`로 `ambiguous`), **토픽 9** (`현지시간, 마켓, 글로벌마켓, 달러, 플랫폼, 해외, CEO, 주가, 테슬라, 뉴욕, 애플, 머스크` — `aichip` 1위·`market` 2위 경합비 `0.906`으로 `ambiguous`), **토픽 10** (`지적, 방안, 제도, 조치, 시행, 위원회, 국회, 규정, 개정` — `residual`), **토픽 11** (`분야, AI, 협력, 혁신, 인공지능, 구축, 역량, 교육, 스타트업, 디지털, 플랫폼, 데이터, 솔루션` — 1위 `aichip` 점유율 `0.0088 < 0.01`로 `residual`) 등 6개 토픽의 비중 합은 `residual_share`로 집계되었다.

> [!NOTE]
> **`첨단산업(전기차·배터리 중심)`(`aichip`) 국면의 매핑 경위 및 의미적 한계 (`supported_ev_battery_only`):**
> 기존 코드의 `KEYWORD_SETS["AI반도체"]`(`aichip`) 검색어 분류체계는 4개 세부 그룹(`인공지능`, `반도체`, `빅테크인프라`, `전기차배터리`)을 묶어 구성되었다. 학습 기간 NMF 적합 결과, 인공지능 관련 어휘가 모인 **토픽 11**은 영문 단일 토큰 `"AI"`가 한글 위주 사전 키워드(`인공지능, 챗GPT, 생성형AI` 등)에 포함되지 않아 도메인 점유율(`0.88%`)이 최소 기준(`1.0%`)에 미달(`residual`)하였고, 반도체·수출 중심의 **토픽 8**과 해외 빅테크 중심의 **토픽 9**는 각각 `trade` 및 `market` 도메인과의 질량비가 `0.90`을 초과하여 `ambiguous`로 분류되었다. 반면 주요 키워드가 `차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, SUV, 성능, 기아, 충전, 배터리, 전기` 등에 집중된 **토픽 12**는 사전 내 `전기차배터리` 세부 그룹의 지지를 받아 유일하게 `aichip` 식별자에 매핑되었다(`supported_ev_battery_only`). 본 연구는 사후적인 토픽 재할당이나 규칙 변경을 배제하기 위해 코드 식별자(`aichip`)와 모델 매핑(`토픽 12`)을 그대로 유지하되, 실제 포착된 토픽의 의미를 반영하여 논문 내 국면 명칭을 **`첨단산업(전기차·배터리 중심)`**으로 표기한다. 또한 이러한 매핑이 AI·반도체 산업 전반에 대한 의미 타당성을 입증하는 것은 아니라는 점을 명확히 한계로 규정한다.

나아가 위 14개 토픽과 6대 유효 국면 매핑이 특정 표본이나 초기화에 의존한 우연적 산물인지 검증하기 위해, **① 실험 B-1 (학습 표본 80% 월별 층화 재표본화: 월 2,400건 $\times$ 48개월 $= 115,200$건, 서로 다른 난수 시드 `101~110`으로 10회 반복 적합)** 및 **② 실험 B-2 (144,000건 동일 표본에서 초기화 방식을 `nndsvda` 1회, `nndsvdar` 5회[시드 `201~205`], `random` 5회[시드 `301~305`]로 변경한 11회 실험)** 등 총 **21회 안정성 실험**을 수행하였다(`topic_stability_runs.csv`, `regime_mapping_stability.csv`). 결과는 표 B-1과 같다.

**Table B-1. Subsample and Initialization Stability of NMF ($K=14$) Topics and Regime Mappings Across 21 Runs.**

| 실험 구분 (Experiment Group) | 반복 횟수 | 적합 문서 수 / 초기화 | 기준 $H$ 대비 평균 Cosine 유사도 (범위) | Top-10 Jaccard 평균 | Top-20 Jaccard 평균 | Weighted Jaccard@20 평균 | 기준 6대 유효 국면 재현율 (`macro, realestate, aichip, market, earnings, capital`) | 미형성 국면 (`hhdebt` / `trade`) 형성 빈도 |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **B-1: 80% 층화 부분표본** (`seed=101~110`) | 10회 | 115,200건 / `nndsvd` | **$0.8492$** ($0.7682 \sim 0.9808$) | $0.6077$ | $0.6383$ | $0.7525$ | **10/10회 (100.0%)** 모두 6/6개 재현 | `hhdebt` 8/10회, `trade` 0/10회 |
| **B-2a: SVD 변형 초기화** (`nndsvda`, `nndsvdar` 5시드) | 6회 | 144,000건 / `nndsvda(r)` | **$0.9888$** ($0.9888 \sim 0.9889$) | $0.8675$ | $0.8759$ | $0.9606$ | **6/6회 (100.0%)** 모두 6/6개 재현 | `hhdebt` 0/6회, `trade` 0/6회 |
| **B-2b: 무작위 초기화** (`random` 5시드) | 5회 | 144,000건 / `random` | **$0.8671$** ($0.8197 \sim 0.9046$) | $0.6388$ | $0.6606$ | $0.7689$ | **5/5회 (100.0%)** 모두 6/6개 재현 | `hhdebt` 3/5회, `trade` 1/5회 |
| **전체 안정성 실험 종합** | **21회** | — | — | — | — | — | **21/21회 (100.0%) 6대 핵심 국면 성립** | `hhdebt` 52.4%, `trade` 4.8% |

표 B-1 및 토픽별 세부 안정성(`topic_stability_summary.csv`) 분석 결과, 6대 유효 국면에 할당된 핵심 토픽들—특히 `T7 earnings`(80% 부분표본 평균 Cosine $0.9968$), `T3 realestate`($0.9953$), `T1 macro`($0.9844$), `T6 capital`($0.9842$), `T13 market`($0.9830$), `T4 market`($0.9615$), `T2 realestate`($0.8077$), `T12 aichip`($0.7810$)—은 표본이 20% 바뀌어도 매우 높은 구조적 일관성을 유지하였으며, **기준 모델의 6대 유효 국면은 21회 실험 전체(100%)에서 빠짐없이 재현**되었다. 또한 SVD 기반 초기화(`nndsvd`, `nndsvda`, `nndsvdar`)가 무작위(`random`) 초기화보다 현저히 높은 재현성(Cosine $0.9888$ vs $0.8671$)을 제공하여 Phase 5.6의 `nndsvd` 선택을 뒷받침한다.

### 3.4 학습 기간 고정 다중 국면 활성화 체계 ($z \ge 0.5$) 및 Strict OOS 적용 범위 구분 (연구 E)
각 유효 국면 $d$의 월별 점유율 $s_{d,t}$에 대해, 미래 정보 누수를 차단하기 위해 **학습 기간(2021.01~2024.12, 48개월)만의 표본 평균 $\mu_{d,\text{train}}$과 표본 표준편차 $\sigma_{d,\text{train}}$(`ddof=1`)**을 모수로 고정하여 표준화 점수를 산출하였다(재계산 검증 시 최대 절대 오차 $1.643 \times 10^{-14}$):

$$z_{d,t} = \frac{s_{d,t} - \mu_{d,\text{train}}}{\sigma_{d,\text{train}}} \tag{3}$$

테스트 기간(2025.01~2026.07, 19개월)에서도 테스트 표본의 평균·표준편차를 다시 계산하지 않고 학습 기간 고정 모수($\mu_{d,\text{train}}, \sigma_{d,\text{train}}$)를 그대로 적용하였으며, $z_{d,t} \ge 0.5$를 충족하는 모든 국면을 해당 월의 활성 국면으로 정의하였다.

심사 과정에서 오해가 발생하지 않도록, 본 연구의 각 분석 단계가 **학습 고정 표본 외(Strict OOS) 평가**인지 아니면 **전체 표본 동시점(In-sample Contemporaneous) 분석**인지를 독립 감사(`strict_oos_data_leakage_audit.csv`)를 통해 표 E-1과 같이 명확히 구분한다.

**Table E-1. Audit of Strict Out-of-Sample (OOS) Boundaries Across Analytical Components.**

| 분석 구성요소 | 적용 기간 | 학습 정보 고정 여부 | 테스트 기간(`2025.01~2026.07`) 누수 여부 | 분석의 정확한 성격 및 해석 범위 |
| :--- | :--- | :--- | :---: | :--- |
| **1. 어휘 사전(22,193개)·IDF·NMF 기저($H_{\text{train}}$)** | 적합: `2021.01~2024.12` ($N=48$m) | 100% 학습 기간 고정 | **누수 없음 (0건)** | **Strict OOS 텍스트 특징 추출기** |
| **2. 토픽-국면 매핑(`map_topics`) 및 표준화 모수($\mu_{\text{train}}, \sigma_{\text{train}}$)** | 산출: `2021.01~2024.12` ($N=48$m) | 100% 학습 기간 고정 | **누수 없음 (0건)** | **Strict OOS 국면 점수($z_{d,t}$) 산출** |
| **3. 다중 국면 활성화 비교 (표 2)** | `Train`(48m) / `Eval OOS`(19m) / `Full`(67m) 분리 보고 | $z \ge 0.5$ 임계값 학습 모수 고정 | **누수 없음 (0건)** | 학습 및 **Strict OOS 테스트 구간 표현 보존성 비교** |
| **4. 월별 코스피 수익률 충격 OLS 회귀 (표 3)** | `Full Sample` (`2021.01~2026.07`, $N=67$m) | 설명변수(`z_*`)는 Strict OOS 특징이나 회귀계수($\beta$)는 67개월 전체 적합 | 회귀계수에 67개월 표본 사용 | **Strict OOS 특징을 사용한 전체 표본 동시점(In-sample Contemporaneous) 설명 회귀** (예측 모형 아님; 학습 48개월 단독 시 $R^2=24.55\%, p=0.0164$) |
| **5. 월별 주가 하락 조기경보 규칙 평가 (4.3.2절)** | `Full`(65m) 및 `Eval OOS`(`2025.01~2026.05`, 17m) 분리 평가 | 사전 고정 규칙(`z_macro >= 0.5`) 적용 | **누수 없음 (0건)** | **Strict OOS 사전 예측 평가 — 테스트 17개월 적중 0건($TP=0, FP=1$)으로 예측력 미입증 투명 보고** |
| **6. 주별 네이버 검색 1차 차분 교차 검증 (표 4, 표 D-1)** | `Train`(208w) / `Eval OOS`(82w) / `Full`(291w) 분리 차분·검정 | 구간별 내부 차분 및 독립 검정 | **누수 없음 (0건)** | **Strict OOS 테스트 기간($N=82$주) 동시점($h=0$) 외부 교차 타당성 검증** |

---

## Ⅳ. 실증 분석 결과

### 4.1 6대 유효 경제 국면 분포 및 기술통계
`phase5_6_train_only_regime_monthly.csv`에서 산출된 6대 유효 국면 및 잔차 비중의 학습 기간(48개월) 고정 표준화 모수와 구간별 활성 개월 수 분포는 표 1과 같다.

**Table 1. Training-Period Standardization Parameters (2021.01–2024.12, $N=48$) and Active Month Counts ($z \ge 0.5$) Across Sample Splits.**

| 국면 표시 명칭 (실질 포착 내용) | 코드 (`Slug`) | 할당 토픽 번호 ($K=14$) | 학습 기간 평균 비중 $\mu_{\text{train}}$ (%, $N=48$) | 학습 기간 표준편차 $\sigma_{\text{train}}$ (%p, $N=48$) | 활성화 임계 비중 ($z \ge 0.5$, %) | 전체 기간 활성 월수 ($N=67$) | 학습 기간 활성 월수 ($N=48$) | 테스트 기간 활성 월수 ($N=19$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **부동산** (전월세·청약분양) | `realestate` | [2, 3] | 12.54 | 0.70 | 12.89 | 18 (26.9%) | 16 (33.3%) | 2 (10.5%) |
| **자본거래** (IPO·공모주·M&A) | `capital` | [6] | 8.66 | 0.71 | 9.02 | 22 (32.8%) | 17 (35.4%) | 5 (26.3%) |
| **금리·물가** (통화정책·물가) | `macro` | [1] | 6.67 | 1.26 | 7.30 | 13 (19.4%) | 12 (25.0%) | 1 (5.3%) |
| **시황** (국내외 증시 마감·수급) | `market` | [4, 13] | 6.16 | 0.37 | 6.35 | 25 (37.3%) | 16 (33.3%) | 9 (47.4%) |
| **첨단산업(전기차·배터리 중심)** | `aichip` | [12] | 6.05 | 0.42 | 6.26 | 16 (23.9%) | 14 (29.2%) | 2 (10.5%) |
| **기업실적** (매출·영업이익 공시) | `earnings` | [7] | 5.63 | 1.13 | 6.19 | 18 (26.9%) | 14 (29.2%) | 4 (21.1%) |
| *(미형성 국면: 가계대출·대외통상)* | `hhdebt`, `trade` | — | NaN | NaN | — | — | — | — |
| *(비할당 잔차·경합 토픽 합계)* | `residual` | [0, 5, 8, 9, 10, 11] | 54.30 | 1.27 | — | — | — | — |
| **할당 6대 국면 합계 / 활성 신호 총합** | — | **8개 토픽** | **45.70** | — | — | **112건** | **89건** | **23건** |

*주: 표 1의 평균 비중($\mu_{\text{train}}$)과 표준편차($\sigma_{\text{train}}$, `ddof=1`)는 Strict OOS 표준화 공식 $z_{d,t} = (s_{d,t} - \mu_{d,\text{train}})/\sigma_{d,\text{train}}$에 사용된 **학습 기간(2021.01~2024.12, 48개월)** 통계량이며, 활성화 임계 비중은 $\mu_{d,\text{train}} + 0.5\sigma_{d,\text{train}}$이다. 참고로 전체 67개월(2021.01~2026.07) 평균 비중은 `realestate` 12.28%, `capital` 8.71%, `macro` 6.59%, `market` 6.24%, `aichip` 5.96%, `earnings` 5.54%, `residual` 54.69%이며, 테스트 기간(2025.01~2026.07, 19개월) 평균 비중은 `realestate` 11.62%, `capital` 8.81%, `macro` 6.41%, `market` 6.43%, `aichip` 5.75%, `earnings` 5.31%, `residual` 55.67%이다.

표 1에서 확인되듯, 학습 기간 기준 6대 할당 국면의 평균 비중 합계는 45.70%이며 6개 비할당·경합 토픽이 54.30%의 잔차 비중(`residual_share`)을 차지한다. 개별 국면의 전체 67개월 중 활성 월수($z_{d,t} \ge 0.5$)는 금리·물가 13개월(19.4%)부터 시황 25개월(37.3%)까지 분포하며, 6대 국면의 활성 신호 총합은 전체 기간 **112건**(학습 89건 + 테스트 23건)이다.

---

### 4.2 단일 국면과 다중 국면 활성화 비교 및 실제 기사 검증 (RQ2, 연구 C)
다중 국면 활성화 체계와 단일 대표 국면(Argmax) 선택 방식이 월별 활성 국면 신호를 어떻게 다르게 표현하는지 `single_vs_multi_metrics.csv`, `single_vs_multi_monthly.csv`, `single_vs_multi_regime_combinations.csv`를 통해 정량적으로 비교하였다.

비교 대상 방식은 다음 세 가지이다:
- **방식 A-1 (Unconstrained Argmax)**: 임계값 조건 없이 매월 6개 국면 중 $z_{d,t}$가 가장 높은 1개 국면을 무조건 대표 국면으로 지정.
- **방식 A-2 (Hurdle Argmax)**: 매월 최대 점수 국면이 $\max_d z_{d,t} \ge 0.5$를 충족할 때만 해당 1개 국면을 대표 국면으로 지정하고, 미달 시 비활성(`none`)으로 분류.
- **방식 B (Multi-Regime Activation, 제안)**: 매월 $z_{d,t} \ge 0.5$를 충족하는 모든 국면을 동시에 활성 국면으로 지정.

구간별 비교 결과는 표 2와 같다.

**Table 2. Quantitative Comparison of Single-Dominant vs. Multi-Regime Activation Representations.**

| 분석 구간 (Sample Split) | 개월 수 ($N$) | 월평균 활성 국면 수 | 0개 활성 (`none`) 월수 (%) | 1개 활성 월수 (%) | 2개 활성 월수 (%) | 3개 활성 월수 (%) | $\ge 2$개 다중 활성 월수 (%) | 다중 국면 방식 전체 활성 신호 수 | 단일 국면 방식 표현 신호 수 (Hurdle 기준) | 단일 국면 제한 시 별도 미표현 활성 신호 수 (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full Sample (`2021-01~2026-07`)** | 67 | 1.672 | 4 (5.97%) | 24 (35.82%) | 29 (43.28%) | 10 (14.93%) | **39 (58.21%)** | 112 | 63 | **49 (43.75%)** |
| **Train Period (`2021-01~2024-12`)** | 48 | 1.854 | 1 (2.08%) | 15 (31.25%) | 22 (45.83%) | 10 (20.83%) | **32 (66.67%)** | 89 | 47 | **42 (47.19%)** |
| **Eval OOS Period (`2025-01~2026-07`)** | 19 | 1.211 | 3 (15.79%) | 9 (47.37%) | 7 (36.84%) | 0 (0.00%) | **36.84% (7개월)** | 23 | 16 | **7 (30.43%)** |

표 2 및 국면 조합 분석 결과는 다음 네 가지 사실을 보여준다:
1. **복합 국면 활성화의 빈도**: 전체 67개월 중 **58.21%(39개월)**에서 월 2개 이상의 경제 국면이 동시에 임계값($z_{d,t} \ge 0.5$)을 상회하였다(2개 활성 29개월[43.28%], 3개 활성 10개월[14.93%], 4개 이상 활성 0개월). 학습 기간(48개월)에서는 다중 활성화 비율이 **66.67%(32개월)**였으며, 표본 외 테스트 기간(19개월)에서도 **36.84%(7개월)**에서 2개 국면이 동시에 활성화되었다.
2. **단일 대표 국면 표현의 구조적 차이(43.75%)**: 단일 대표 국면 방식으로 표현을 제한할 경우, 다중 국면 방식에서 관측된 활성 국면 신호 중 **43.75%(112건 중 49건; 학습 기간 89건 중 42건[47.19%], 테스트 기간 23건 중 7건[30.43%])가 별도 국면으로 표현되지 않는다.** 또한 모든 국면이 $z_{d,t} < 0.5$인 비활성 4개월(전체 5.97%: 학습 1개월[`2021-07`], 테스트 3개월[`2025-05, 2026-04, 2026-06`])에 대해 무제약 Argmax(방식 A-1)는 임계값 미달 국면을 강제로 할당하는 반면, Hurdle Argmax(방식 A-2)와 다중 국면 방식(방식 B)은 이를 비활성(`none`) 상태로 구분한다.
3. **실제 관측된 동시 활성화 국면 조합**: `single_vs_multi_regime_combinations.csv` 및 `single_vs_multi_monthly.csv` 확인 결과, 전체 67개월에서 가장 빈번히 관측된 2국면 단독 조합은 **`market;earnings`(5개월: 학습 3, 테스트 2)**였으며, 이어서 **`aichip;capital`(4개월: 학습 4)**, **`macro;realestate`(3개월: 학습 3)**, **`realestate;capital`(3개월: 학습 3)**, **`earnings;capital`(3개월: 학습 2, 테스트 1)** 순으로 나타났다. 3국면 동시 활성 월(10개월)까지 포함한 쌍별 동시 활성화 빈도를 시기별로 보면, 2022~2023년 고물가·금리 인상기에는 **2022년 중 `macro`와 `realestate`의 동시 활성화가 5개월**(2국면 단독 `macro;realestate` 3개월[`2022-05, 2022-07, 2022-11`] + 3국면 조합 2개월[`2022-06, 2022-10`]), **2022~2023년 중 `macro`와 `market`의 동시 활성화가 5개월**(2국면 단독 `macro;market` 2개월[`2022-09, 2023-09`] + 3국면 조합 3개월[`2022-06, 2022-10, 2023-08`]) 관측된 반면, 같은 2022~2023년 기간 중 `macro`와 `capital`이 동시에 활성화된 달은 없었다(0개월; 전 기간 중 `macro`와 `capital`의 동시 활성화는 `2024-12`의 `macro;market;capital` 1개월뿐임).
4. **자동 규칙 기반 5대 대표 사례 월 선정 및 실제 코퍼스 기사(`W` 가중치) 역추적 검증(연구 C)**: "임계값 이상의 국면을 복수로 허용하면 단일 선택보다 활성 신호가 더 많이 남는 것은 산술적 동어반복(Tautology)이 아닌가?"라는 방법론적 질문에 답하기 위해, 주관적 선별을 배제하고 5가지 객관적 규칙(① 학습 3국면 활성 중 누락 $z$ 최대 월, ② 학습 `macro+realestate` 중 누락 $z$ 최대 월, ③ 학습 최빈 조합 `market+earnings` 중 누락 $z$ 최대 월, ④ 테스트 OOS 누락 $z$ 1위 월, ⑤ 테스트 OOS `market+earnings` 중 누락 $z$ 최대 월)으로 5개 사례 월을 자동 선정하였다(`multi_regime_case_manifest.csv`). 그리고 원시 코퍼스(`news_corpus.parquet`)의 실제 기사에 대해 고정 NMF 기저로 산출된 문서별 정규화 국면 비중 $s_{i,d} = \sum_{k \in T_d} w_{i,k}$(월평균과 `phase5_6_train_only_regime_monthly.csv` 간 최대 절대 오차 $8.018 \times 10^{-11}$)를 역추적한 결과는 표 C-1과 같다.

**Table C-1. Objectively Selected Multi-Regime Case Months and Real Corpus Article Evidence (`multi_regime_case_monthly.csv`, `multi_regime_case_articles.csv`).**

| 사례 월 (구간) | 선정 규칙 요약 | 단일 대표 국면 (Argmax $z$) | 다중 활성 국면 전체 ($z \ge 0.5$) | 단일 방식에서 별도 미표현된 국면 ($z$) | 동월 거시·시장 지표 (`kospi_ret` / `base_rate_diff`) | 실제 코퍼스 내 미표현 국면 및 복합 이슈 기사 검증 근거 (`article_id` 및 상위 가중치 $s_{i,d}$) |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **`2021-09`** (`Train`) | 학습 3국면 중 누락 $z$ 최대 | `capital` ($+1.51$) | `realestate;aichip;capital` | **`aichip` ($+1.26$), `realestate` ($+1.21$)** | $-4.17\%$ / $0.00\%\text{p}$ | 단일 방식은 IPO·공모주(`capital`)만 표시하나, 동월 현대차·기아 전기차 출시(`aichip` $s_{i,d}=0.885$, 기사 `02100101.20210929085258001`)와 가을 분양·전세대출 규제(`realestate` $s_{i,d}=0.946$, 기사 `02100311.20210924143902001`)가 동시에 집중 보도됨 |
| **`2022-10`** (`Train`) | 학습 `macro+realestate` 중 누락 $z$ 최대 | `macro` ($+1.83$) | `macro;realestate;market` | **`realestate` ($+1.45$), `market` ($+0.55$)** | $+6.21\%$ / $+0.50\%\text{p}$ | 한국은행 빅스텝($+50\text{bp}$) 인상 달로 단일 방식은 `macro`만 표시하나, 금리 급등에 따른 주택 매수세 실종·전세값 하락(`realestate` $s_{i,d}=0.943$, 기사 `02100101.20221011160447001`) 및 금리·주담대 복합 기사(`macro` $0.354$ + `realestate` $0.369$, 기사 `02100101.20221012174945001`)가 동시 급증함 |
| **`2023-08`** (`Train`) | 학습 최빈 조합(`market+earnings`) 누락 $z$ 최대 | `earnings` ($+2.05$) | `macro;market;earnings` | **`market` ($+1.64$), `macro` ($+0.78$)** | $-2.94\%$ / $0.00\%\text{p}$ | 2분기 상장사 실적 발표(`earnings`)가 1위이나, 동월 초전도체·2차전지 테마주 급등락으로 `market`($z=+1.64$)이 강하게 활성화되었으며 시황·실적 복합 기사(`market` $0.517$ + `earnings` $0.453$, 기사 `02100601.20230804092836001`)가 다수 관측됨 |
| **`2026-01`** (`Eval OOS`) | 테스트 OOS 누락 $z$ 전체 1위 | `market` ($+2.21$) | `aichip;market` | **`aichip` ($+1.07$)** | $+21.48\%$ / $0.00\%\text{p}$ | 표본 외 기간 코스피 급등($+21.48\%$)으로 `market`이 1위이나, 연초 신형 전기차·배터리 이슈(`aichip` $z=+1.07$, 기사 `02100311.20260113142429002`)가 임계치의 2배 이상으로 동시 활성화됨 |
| **`2026-02`** (`Eval OOS`) | 테스트 OOS `market+earnings` 누락 $z$ 최대 | `market` ($+3.69$) | `market;earnings` | **`earnings` ($+1.16$)** | $+17.85\%$ / $0.00\%\text{p}$ | 표본 외 증시 급등으로 `market`($z=+3.69$)이 압도적 1위이나, 연간 결산 영업이익 공시 시즌으로 `earnings`($z=+1.16$, 기사 `02100311.20260209160521001`) 및 증시·실적 동시 반영 기사(`market` $0.455$ + `earnings` $0.483$, 기사 `02100601.20260209162205001`)가 함께 포착됨 |

표 C-1은 다중 국면 활성화가 단순한 수치적 정의를 넘어, 금리 인상기의 부동산 경색(`2022-10`)이나 증시 변동기의 상장사 실적 충격(`2023-08`, `2026-02`)처럼 거시·금융 분석에서 핵심적인 부차 국면을 보존함을 실제 기사로 입증한다. 단, 이러한 결과는 **표현상 정보 보존성(Representational Information Preservation)**에 관한 것이며, 시장 수익률이나 거시지표의 사전 예측 정확도 개선을 의미하지 않는다.

---

### 4.3 Phase 5.6 Strict OOS 기반 시장·경제 지표 관계 분석 (RQ3)

#### 4.3.1 코스피 수익률 충격에 대한 Newey-West HAC OLS 동행 회귀분석
학습 기간 고정 NMF 투영으로 도출된 6대 유효 국면 표준화 점수(`z_*`)를 설명변수로 하고, 과거 변동성 정규화 월간 코스피 수익률(`kospi_ret_std`)을 종속변수로 하여 전체 67개월(`2021-01 ~ 2026-07`, 결측치 없음) 표본에서 Newey-West HAC 견고 회귀분석(Bartlett 커널, `maxlags=3`)을 수행한 결과(`verification_ols_results.csv`, 모형 ID `Phase56_StrictOOS_ret_std_67m`)는 표 3과 같다.

**Table 3. Newey-West HAC OLS Estimation on Volatility-Standardized Monthly KOSPI Return (`kospi_ret_std`, $N=67$, `maxlags=3`).**

| 설명변수 (Variable) | 회귀계수 ($\beta$) | HAC 표준오차 (SE) | $t$-통계량 ($z$) | 95% 신뢰구간 (CI) | 원시 $p$-값 (`p_value_raw`) | Holm 보정 $p$-값 (`p_value_holm`, 6변수) | VIF |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `const` (상수항) | $+0.0631$ | $0.1357$ | $+0.465$ | $[-0.2029, +0.3291]$ | $0.6419$ | — | — |
| **`z_macro` (금리·물가)** | **$-0.7418$** | **$0.2093$** | **$-3.543$** | **$[-1.1521, -0.3315]$** | **$0.0004$** | **$0.0024$** | $1.95$ |
| **`z_capital` (자본거래)** | **$-0.5299$** | **$0.1758$** | **$-3.015$** | **$[-0.8744, -0.1854]$** | **$0.0026$** | **$0.0129$** | $1.91$ |
| `z_realestate` (부동산) | $-0.2082$ | $0.1185$ | $-1.757$ | $[-0.4403, +0.0240]$ | $0.0789$ | $0.3155$ | $1.27$ |
| `z_market` (시황) | $-0.1437$ | $0.0898$ | $-1.600$ | $[-0.3197, +0.0323]$ | $0.1096$ | $0.3289$ | $1.16$ |
| `z_aichip` (첨단산업(전기차·배터리 중심)) | $-0.2583$ | $0.1802$ | $-1.434$ | $[-0.6115, +0.0948]$ | $0.1517$ | $0.3289$ | $1.33$ |
| `z_earnings` (기업실적) | $-0.1143$ | $0.1698$ | $-0.673$ | $[-0.4471, +0.2185]$ | $0.5008$ | $0.5008$ | $1.27$ |
| **모형 적합도 (Model Fit)** | \multicolumn{7}{l}{$N = 67$ (`2021-01~2026-07`), $df_{\text{model}} = 6$, $df_{\text{resid}} = 60$, $R^2 = 0.161879$ (**$16.19\%$**), $\text{Adjusted } R^2 = 0.078067$ (**$7.81\%$**)} |
| **HAC 결합 검정 (Joint Test)** | \multicolumn{7}{l}{Newey-West HAC ($\text{maxlags}=3$) $F(6, 60) = 4.683257$ (**$p = 0.000573$**), $\text{Wald } \chi^2 = 28.099544$} |

표 3의 주요 결과는 다음과 같다:
1. 6대 국면 동행 회귀모형은 과거 변동성 정규화 월간 수익률(`kospi_ret_std`) 변동의 $R^2 = 16.19\%$ ($\text{Adj-}R^2 = 7.81\%$)를 설명하며, Newey-West HAC 결합 검정 통계량 $F = 4.6833$ ($p = 0.000573$)으로 유의하였다. 모든 설명변수의 분산팽창계수(VIF)는 $1.16 \sim 1.95$로 다중공선성 문제가 없었다(학습 48개월 단독 적합 시에는 $R^2 = 24.55\%, \text{Adj-}R^2 = 13.50\%, \text{HAC } F = 2.9842, p = 0.0164$).
2. 6개 국면 변수에 대한 Holm-Bonferroni 다중검정 보정 결과, **`z_macro`(금리·물가: $\beta = -0.7418, \text{HAC SE} = 0.2093, p_{\text{raw}} = 0.0004, p_{\text{holm}} = 0.0024$)**와 **`z_capital`(자본거래: $\beta = -0.5299, \text{HAC SE} = 0.1758, p_{\text{raw}} = 0.0026, p_{\text{holm}} = 0.0129$)** 두 변수만 유의한 음(-)의 동행 관계를 보였다.
3. 표 E-1에서 명시한 바와 같이, 본 회귀분석은 Strict OOS 텍스트 특징을 설명변수로 사용하여 67개월 전체 표본에서 당월($t$) 뉴스 국면 점유율과 당월($t$) 수익률 충격 간의 관계를 추정한 **표본 내 동시점 설명 회귀(In-sample Contemporaneous Regression)**이며, 미래 수익률 예측력을 의미하지 않는다.

#### 4.3.2 월별 거시지표 시차 상관 및 조기경보 규칙 평가의 구분
`verification_correlation_lag_results.csv`에서 6대 유효 국면과 차분·수익률 변환된 4대 거시·금융 지표(`kospi_ret`, `base_rate_diff`, `ccsi_diff`, `usdkrw_ret`) 간 5개 시차($h \in \{-2, -1, 0, +1, +2\}$, $h>0$은 뉴스 선행, $h<0$은 경제지표 선행)의 **총 120개 검정 패밀리**에 대해 단일 Holm 보정을 수행한 결과는 다음과 같다:
- **`kospi_ret`과의 시차 상관**: `macro` ↔ `kospi_ret` 상관은 $h=0$($N=67, r=-0.1598, p_{\text{raw}}=0.1965, p_{\text{holm}}=1.000$) 및 $h=+1$($N=66, r=+0.0734, p_{\text{raw}}=0.5583, p_{\text{holm}}=1.000$) 모두 비유의하였으며, 6대 국면 전체에서 120개 검정 Holm 보정 후 유의한 단일 변수 주가 수익률 시차 상관은 존재하지 않았다($p_{\text{holm}} \ge 0.4304$).
- **`base_rate_diff`(한국은행 기준금리 월간 변화폭)와의 시차 상관**: 120개 검정 중 Holm 보정 후 유의한($p_{\text{holm}} < 0.05$) 조합은 총 4개로, ① **`macro` ↔ `base_rate_diff` ($h=-2$, 금리 2개월 선행, $N=65$): $r = +0.4886$ ($p_{\text{raw}} = 3.63 \times 10^{-5}, p_{\text{holm}} = 0.0044$)**, ② **`macro` ↔ `base_rate_diff` ($h=+1$, 뉴스 1개월 선행, $N=66$): $r = +0.4749$ ($p_{\text{raw}} = 5.60 \times 10^{-5}, p_{\text{holm}} = 0.0067$)**, ③ **`macro` ↔ `base_rate_diff` ($h=0$, 동월 동행, $N=67$): $r = +0.4580$ ($p_{\text{raw}} = 9.74 \times 10^{-5}, p_{\text{holm}} = 0.0115$)**, ④ **`capital` ↔ `base_rate_diff` ($h=0$, 동월 동행, $N=67$): $r = -0.4260$ ($p_{\text{raw}} = 3.25 \times 10^{-4}, p_{\text{holm}} = 0.0380$)**이다. $h=-2$(금리 변동 선행) 상관이 $h=+1$(뉴스 선행)보다 더 크게 나타난 것은 2022~2023년 연속 금리 인상기 동안 통화정책 결정과 언론 보도가 상호 피드백하며 동조화(Co-movement)되었음을 보여준다.

또한 `verification_warning_performance_results.csv`에서 검증된 월별 조기경보 규칙(향후 1~2개월 예측창 $t+1, t+2$ 평가; 마지막 2개월을 제외한 전체 평가 가능 기간 `2021-01~2026-05` [$N=65$개월] 및 테스트 평가 가능 기간 `2025-01~2026-05` [$N=17$개월])의 성과와 한계는 평가 기준별로 다음과 같이 엄격히 구분된다:
1. **일반 주가 하락 경고 ($\text{kospi\_ret}_{t+1} < 0\%$ 또는 $\text{kospi\_ret}_{t+2} < 0\%$)**:
   - 과거 8국면 기반의 원래 2국면 결합 규칙(`z_macro >= 0.5 | z_hhdebt >= 0.5`)은 65개월 동안 28회 경고를 발생시켜 정밀도 **67.86%**($TP=19, FP=9, FN=26, TN=11$, Recall `42.22%`, Specificity `55.00%`)를 기록하였으나, 동일 기간 실제 하락창 자연발생률 **69.23%**(`45/65`)보다 `-1.37%p` 낮아 변별력이 없었으며, Phase 5.6 Strict OOS에서는 `hhdebt` 국면이 미형성(`NaN`)되어 원래 규칙 자체를 평가할 수 없다.
   - `hhdebt` 결측에 따라 `z_macro >= 0.5` 단독으로 축소한 **Phase 5.6 대체 규칙(`Phase5.6_StrictOOS_MacroOnly`)**은 전체 65개월에서 경고 13건 중 9건 적중(Precision **69.23%**, Recall **20.00%**, $TP=9, FP=4, FN=36, TN=16$)으로 자연발생률(`69.23%`)과 차이가 없었으며(`0.00%p`), **Strict OOS 테스트 평가 가능 기간(17개월, `2025-01~2026-05`)에서는 경고 1건(`2026-03`)이 발생했으나 실제 하락 사건창(9건)을 포착하지 못하였다($TP=0, FP=1, FN=9, TN=7$, Precision `0.00%`, Recall `0.00%`, Specificity `87.50%`, $F_1 = 0.000, \text{MCC} = -0.2582$).**
2. **코스피 급락($\text{kospi\_ret}_t \le -3.0\%$, 전체 67개월 중 16건) 사전 포착**: 과거 2국면 결합 규칙은 16건 중 11건(`68.75%`: `hhdebt` 단독 8건, `macro` 3건)에서 직전 1~2개월 경고가 켜졌으나, Phase 5.6의 `z_macro >= 0.5` 단독 대체 규칙은 2022년 급락 3건(`2022-06, 2022-09, 2022-12`)만 포착(`3/16 = 18.75%`)하였고 테스트 기간 급락 3건(`2025-11, 2026-03, 2026-07`)은 포착하지 못하였다(`0/3 = 0.00%`).
3. **한국은행 기준금리 인상($\text{base\_rate\_diff}_t > 0$, 전체 11건) 사전 포착**: 직전 1~2개월 `z_macro >= 0.5` 기준 포착률은 전체 `7/11 = 63.64%`였으나, 포착된 7건은 모두 `z_macro >= 0.5`가 11개월 연속 지속된 `2022-04~2023-01` 연속 인상기(`7/7 = 100%`, 직전 인상의 사후 보도와 차기 인상 사전 경고창이 중첩되는 구간)에 집중되었고, 긴축 전환 초기 인상 3건(`2021-08, 2021-11, 2022-01`)과 표본 외 재인상 1건(`2026-07`)은 모두 미탐지(`0/4 = 0.00%`)되었다.

따라서 본 연구는 월별 뉴스 국면 지표를 주가나 금리 전환점의 사전 예측(Early-Warning Forecasting) 도구로 주장하지 않으며, 당월 시장 충격과의 동행 설명력(표 3) 및 대중 검색 관심도와의 동시점 교차 검증(표 4)에 실증적 초점을 둔다.

---

### 4.4 네이버 검색 데이터를 이용한 주별 교차 데이터 검증 및 강건성 (RQ4, 연구 D)
뉴스 코퍼스에서 도출된 주별 국면 점유율(`news_share_*`)과 네이버 데이터랩 주별 상대 검색 지수(`score_rel`) 간의 교차 타당성을 검증하기 위해, 292개 ISO 주차(`2020-W53 ~ 2026-W31`: 학습 209주[`2020-W53~2024-W52`], 테스트 83주[`2025-W01~2026-W31`]) 패널을 구축하였다.

비정상 시계열의 공통 추세로 인한 가짜 상관을 배제하기 위해 각 구간(`Train`, `Eval OOS`, `Full`) 내부에서 뉴스 점유율과 검색 지수에 각각 **주간 1차 차분(First Difference)**을 적용하였으며(차분 후 $h=0$ 유효 표본 수: 학습 $N=208$, 테스트 $N=82$, 전체 $N=291$; 시차 $h=\pm 1$ 유효 표본 수: 학습 $N=207$, 테스트 $N=81$, 전체 $N=290$), 시계열 자기상관과 이분산성을 통제하기 위해 표준화 차분 회귀에 **Newey-West HAC 표준오차(Bartlett 커널, 기본 `maxlags=4`)**를 적용하였다. 다중검정 보정은 각 구간별로 **사전 지정된 8개 뉴스-검색 매칭 쌍 $\times$ 3개 시차($h \in \{-1, 0, +1\}$) = 총 24개 검정 패밀리**에 대해 Holm-Bonferroni 보정(`hac_p_holm`)을 수행하였다. `news_search_hac_results.csv`의 전체 검증 결과는 표 4와 같다.

**Table 4. Weekly First-Difference Cross-Validation Between News Regimes and Naver Datalab Relative Search Indices (`news_search_hac_results.csv`, Newey-West HAC `maxlags=4`, 24-Test Holm Adjustment per Split).**

| 뉴스 국면 ↔ 네이버 검색 그룹 (`pair_label`) | 시차 ($h$) | 학습 구간 (`2021~2024`, $N=208/207$) Pearson $r$ (HAC $p_{\text{holm}}$) | 테스트 구간 (`2025~2026`, $N=82/81$) Pearson $r$ (HAC $p_{\text{holm}}$) | 전체 구간 (`2021~2026`, $N=291/290$) Pearson $r$ (HAC $p_{\text{holm}}$) | 다중검정 보정 후 판정 (HAC $p_{\text{holm}} < 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. 시황 뉴스 ↔ 국내증시 검색** | **$h = 0$ (동행)** | **$+0.6478$ ($1.14 \times 10^{-7}$)** | **$+0.4984$ ($0.0432$)** | **$+0.4868$ ($9.06 \times 10^{-5}$)** | **학습·테스트·전체 동행 유의** |
| (`market` ↔ `search_market`) | $h = -1$ (검색 1주 선행) | $-0.2448$ ($0.1783$) | $-0.3461$ ($0.0244$) | $-0.2822$ ($0.0026$) | 1주 시차 음(-)의 반전 |
| | $h = +1$ (뉴스 1주 선행) | $-0.1338$ ($1.0000$) | $+0.0442$ ($1.0000$) | $-0.0144$ ($1.0000$) | 비유의 |
| **2. 기업실적 뉴스 ↔ 기업실적 검색** | **$h = 0$ (동행)** | **$+0.2160$ ($0.0143$)** | **$+0.4718$ ($0.0011$)** | **$+0.2795$ ($3.48 \times 10^{-5}$)** | **학습·테스트·전체 동행 유의** |
| (`earnings` ↔ `search_earnings`) | $h = -1$ (검색 1주 선행) | $-0.1654$ ($0.1603$) | $+0.0444$ ($1.0000$) | $-0.1160$ ($0.7033$) | 비유의 |
| | $h = +1$ (뉴스 1주 선행) | $-0.0638$ ($1.0000$) | $-0.2033$ ($1.0000$) | $-0.0968$ ($1.0000$) | 비유의 |
| **3. 금리·물가 뉴스 ↔ 금리 검색** | **$h = 0$ (동행)** | **$+0.5511$ ($2.57 \times 10^{-13}$)** | $+0.3397$ ($0.3575$)$^{\dagger}$ | **$+0.5026$ ($1.29 \times 10^{-13}$)** | **학습·전체 동행 유의** (테스트 보정 후 비유의) |
| (`macro` ↔ `search_macro_interest`) | $h = -1$ (검색 1주 선행) | $-0.2885$ ($9.48 \times 10^{-5}$) | $-0.1246$ ($1.0000$) | $-0.2588$ ($3.00 \times 10^{-5}$) | 학습·전체 1주 시차 음(-)의 반전 |
| | $h = +1$ (뉴스 1주 선행) | $-0.2556$ ($2.15 \times 10^{-5}$) | $-0.2221$ ($0.7698$) | $-0.2453$ ($4.11 \times 10^{-6}$) | 학습·전체 1주 시차 음(-)의 반전 |
| **4. 금리·물가 뉴스 ↔ 금리+물가 검색** | **$h = 0$ (동행)** | **$+0.4978$ ($3.28 \times 10^{-11}$)** | $+0.2254$ ($1.0000$) | **$+0.3217$ ($5.07 \times 10^{-6}$)** | **학습·전체 동행 유의** (테스트 비유의) |
| (`macro` ↔ `search_macro_combined`) | $h = -1$ (검색 1주 선행) | $-0.3060$ ($8.93 \times 10^{-5}$) | $+0.0420$ ($1.0000$) | $-0.1311$ ($0.0100$) | 학습·전체 1주 시차 음(-)의 반전 |
| | $h = +1$ (뉴스 1주 선행) | $-0.1104$ ($1.0000$) | $+0.0839$ ($1.0000$) | $-0.0174$ ($1.0000$) | 비유의 |
| **5. 금리·물가 뉴스 ↔ 물가 검색** | $h = 0$ (동행) | $+0.0658$ ($1.0000$) | $+0.1355$ ($1.0000$) | $+0.0776$ ($1.0000$) | 비유의 ($h=-1, +1$ 모두 $p_{\text{holm}} \ge 0.1406$) |
| **6. 자본거래 뉴스 ↔ 공모주 검색** | $h = 0$ (동행) | $+0.1437$ ($1.0000$) | $+0.1658$ ($1.0000$) | $+0.1348$ ($0.9527$) | 비유의 ($h=-1, +1$ 모두 $p_{\text{holm}} = 1.0000$) |
| **7. 부동산 뉴스 ↔ 부동산 검색** | $h = 0$ (동행) | $+0.1288$ ($1.0000$) | $-0.0768$ ($1.0000$) | $+0.1008$ ($1.0000$) | 비유의 ($h=-1, +1$ 모두 $p_{\text{holm}} \ge 0.5117$) |
| **8. 첨단산업(전기차·배터리 중심) 뉴스 ↔ AI반도체 검색** | $h = 0$ (동행) | $-0.0357$ ($1.0000$) | $+0.1417$ ($1.0000$) | $+0.0609$ ($1.0000$) | 비유의 ($h=-1, +1$ 모두 $p_{\text{holm}} = 1.0000$) |

*주: $h=0$은 동일 ISO 주차 내 뉴스 점유율 차분과 검색 지수 차분 간 상관($N=208, 82, 291$)이며, $h=+1$은 $t$주 뉴스 차분과 $t+1$주 검색 차분, $h=-1$은 $t$주 뉴스 차분과 $t-1$주 검색 차분 간 상관($N=207, 81, 290$)이다. 괄호 안 수치는 각 구간 내 24개 검정에 대한 Newey-West HAC(`maxlags=4`) Holm 보정 $p$-값(`hac_p_holm`)이다. $^{\dagger}$테스트 구간(`Eval OOS`, $N=82$)의 '금리·물가 뉴스 ↔ 금리 검색'($h=0$)은 $r = +0.3397$, HAC 원시 $p = 0.0170$이나 24개 검정 HAC Holm 보정 후 $p_{\text{holm}} = 0.3575$로 유의수준($0.05$)을 초과하므로 다중검정 보정 후 유의 결과로 분류하지 않는다.

나아가 주별 교차 검증 결과가 특정 HAC 시차(`maxlags=4`) 선택이나 점근적 정규근사에 민감한지 검증하기 위해, **① Newey-West HAC 시차를 `maxlags` $\in \{2, 4, 8\}$주로 변경한 민감도 분석**(`news_search_hac_lag_sensitivity.csv`)과 **② 블록 길이 $L \in \{2, 4, 8\}$주, 반복 $B = 2,000$회(`seed=42`) 이동 블록 부트스트랩(Moving Block Bootstrap, MBB) 95% 신뢰구간 추정**(`news_search_block_bootstrap_ci.csv`)을 수행하였다(연구 D). 동시점($h=0$) 결과 요약은 표 D-1과 같다.

**Table D-1. HAC Lag Sensitivity (`maxlags` $\in \{2, 4, 8\}$) and Moving Block Bootstrap ($L \in \{2, 4, 8\}$ Weeks, $B=2,000$) 95% Confidence Intervals at $h=0$.**

| 뉴스-검색 매칭 쌍 (`pair_label`, $h=0$) | 구간 (`split`, $N$) | Pearson $r$ | HAC $p_{\text{holm}}$ (`lag=2`) | HAC $p_{\text{holm}}$ (`lag=4`) | HAC $p_{\text{holm}}$ (`lag=8`) | MBB 95% CI ($L=2$주) | MBB 95% CI ($L=4$주) | MBB 95% CI ($L=8$주) | MBB 0 배제 여부 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. 시황 ↔ 국내증시** | `Full` ($291$) | $+0.4868$ | $1.31 \times 10^{-5}$ | $9.06 \times 10^{-5}$ | $4.76 \times 10^{-4}$ | $[+0.2584, +0.6258]$ | $[+0.2738, +0.6227]$ | $[+0.2747, +0.6260]$ | **YES (전 블록)** |
| **2. 기업실적 ↔ 기업실적** | `Full` ($291$) | $+0.2795$ | $2.05 \times 10^{-4}$ | $3.48 \times 10^{-5}$ | $5.29 \times 10^{-7}$ | $[+0.1558, +0.4005]$ | $[+0.1710, +0.3910]$ | $[+0.1930, +0.3712]$ | **YES (전 블록)** |
| **3. 금리·물가 ↔ 금리** | `Full` ($291$) | $+0.5026$ | $1.97 \times 10^{-11}$ | $1.29 \times 10^{-13}$ | $1.01 \times 10^{-13}$ | $[+0.3905, +0.6194]$ | $[+0.3958, +0.6085]$ | $[+0.4034, +0.6036]$ | **YES (전 블록)** |
| **4. 금리·물가 ↔ 금리+물가** | `Full` ($291$) | $+0.3217$ | $1.80 \times 10^{-5}$ | $5.07 \times 10^{-6}$ | $1.69 \times 10^{-6}$ | $[+0.1636, +0.4671]$ | $[+0.1711, +0.4596]$ | $[+0.1818, +0.4537]$ | **YES (전 블록)** |
| **1. 시황 ↔ 국내증시** | **`Eval OOS` ($82$)** | **$+0.4984$** | **$0.0339$** | **$0.0432$** | $0.0616$ ($p_{\text{raw}}=0.0027$) | **$[+0.1870, +0.6350]$** | **$[+0.2079, +0.6367]$** | **$[+0.2202, +0.6353]$** | **YES (전 블록)** |
| **2. 기업실적 ↔ 기업실적** | **`Eval OOS` ($82$)** | **$+0.4718$** | **$0.0015$** | **$0.0011$** | **$0.0013$** | **$[+0.2856, +0.6164]$** | **$[+0.2989, +0.5986]$** | **$[+0.3125, +0.5902]$** | **YES (전 블록)** |
| **3. 금리·물가 ↔ 금리** | `Eval OOS` ($82$) | $+0.3397$ | $0.3228$ | $0.3575$ | $0.3693$ | $[+0.0888, +0.6079]$ | $[+0.1112, +0.5877]$ | $[+0.1235, +0.5625]$ | YES (Holm 미충족) |

표 4와 표 D-1의 분석 결과는 다음과 같이 요약된다:
1. **표본 외 테스트 기간에서도 HAC Holm 보정 및 블록 부트스트랩을 통과한 동시점($h=0$) 동조 관계**: 테스트 기간($N=82$주)에서 24개 검정 HAC Holm 보정 후 유의한 동시점 양(+)의 관계는 **① '시황 뉴스 ↔ 국내증시 검색'($r = +0.4984, \text{HAC } p_{\text{holm}} = 0.0432$ at `maxlags=4`)**과 **② '기업실적 뉴스 ↔ 기업실적 검색'($r = +0.4718, \text{HAC } p_{\text{holm}} = 0.0011$ at `maxlags=4`)** 두 쌍으로 확인되었다. 특히 '기업실적'은 `maxlags` $\in \{2, 4, 8\}$ 전 시차에서 $p_{\text{holm}} \le 0.0015$로 강건하게 유의하였으며, '시황'은 `maxlags=2`($p_{\text{holm}}=0.0339$)와 `maxlags=4`($p_{\text{holm}}=0.0432$)에서 유의하고 장기 시차인 `maxlags=8`에서는 원시 $p=0.0027$이나 24개 검정 보정 후 $p_{\text{holm}}=0.0616$으로 경계선 수준을 보였다. 동시에 비모수 이동 블록 부트스트랩($L=2, 4, 8$주, $B=2,000$)에서는 두 쌍 모두 모든 블록 길이에서 95% 신뢰구간이 0을 완전히 배제하여(예: $L=4$주 기준 시황 $[+0.2079, +0.6367]$, 기업실적 $[+0.2989, +0.5986]$) 유한 표본 강건성이 확인되었다.
2. **금리·물가 뉴스와 금리 검색의 구간별 결과 구분**: '금리·물가 뉴스 ↔ 금리 검색'($h=0$)은 학습 기간($r = +0.5511, \text{HAC } p_{\text{holm}} = 2.57 \times 10^{-13}$)과 전체 기간($r = +0.5026, \text{HAC } p_{\text{holm}} = 1.29 \times 10^{-13}$)의 모든 HAC 시차(`maxlags=2,4,8`) 및 부트스트랩에서 가장 강한 동시점 동조성을 나타냈다. 반면 금리 변동의 빈도가 줄어든 테스트 기간($N=82$주)에서 금리 검색은 $r = +0.3397$, HAC 원시 $p = 0.0170$(MBB 95% CI $[+0.1112, +0.5877]$ at $L=4$)의 양(+)의 상관을 보였으나, 24개 검정에 대한 HAC Holm 보정 후에는 $p_{\text{holm}} = 0.3575$로 다중검정 유의수준을 충족하지 못하였다.
3. **1주 시차($h = \pm 1$)에서의 양(+)의 선행성 부재**: $h = -1$(검색 1주 선행) 및 $h = +1$(뉴스 1주 선행)에서는 모든 국면 쌍에서 유의한 양(+)의 상관이 관찰되지 않았으며, 오히려 급등 직후 차주의 기저효과(평균 회귀)로 인해 '시황'($h=-1$)과 '금리'($h=\pm 1$)에서 음(-)의 반전 상관이 나타났다. 이는 뉴스 보도와 대중 검색 관심이 1주 단위의 시차를 두고 한쪽이 다른 쪽을 일방향으로 선행하기보다 **동일 주간($h=0$) 내에 동시적으로 반응**함을 보여준다.
4. **차분 후 비유의 국면(부동산·자본거래·물가·첨단산업)의 원인**: 수준값에서는 완만한 추세를 공유하던 부동산, 공모주(자본거래), 물가 검색은 주간 1차 차분 후 단기 변동 상관이 비유의하였다. 특히 '첨단산업(전기차·배터리 중심) 뉴스(`aichip`) ↔ AI반도체 검색'($h=0, r = +0.0609, p_{\text{holm}} = 1.0000$)의 비유의성은 3.3절에서 규명한 바와 같이 학습 기간 NMF에서 `aichip` 식별자에 할당된 토픽 12가 실제로는 전기차·배터리·자동차 어휘 중심으로 구성된 반면, 검색 지수는 생성형 AI·HBM·반도체 전반을 포괄하는 의미적 범위 차이에 기인한다.
5. **공통 앵커(`'은행'`) 분모 민감도 점검 (`news_search_anchor_sensitivity.csv`)**: 네이버 데이터랩 상대지수(`score_rel = score / anchor_score`)는 서로 다른 API 호출 간 스케일 비교를 위해 공통 앵커 키워드(`'은행'`)의 상대지수로 나눈 값이다. 공통 분모의 변동이 주간 차분 상관에 미친 영향을 점검하기 위해 ① 앵커 지수(`anchor_score`)로 나누지 않은 각 검색 그룹 자체의 원래 상대 검색 지수(`score`, 단일 API 조회 구간 내 자체 최대값=100 기준 상대 지표)의 주간 1차 차분($\Delta \text{score}$)을 사용한 분석과, ② $\Delta \text{score\_rel}$ 회귀식에 주간 앵커 차분($\Delta \text{anchor\_score}$)을 통제변수로 추가한 부분회귀 분석을 수행하였다. 분석 결과, 앵커를 나누지 않은 원래 상대 검색 지표($\Delta \text{score}$)의 차분에서도 전체 구간 동시점($h=0$)에서 '금리'($r = +0.5290, \text{HAC } p_{\text{holm}} = 3.95 \times 10^{-16}$), '시황'($r = +0.5330, \text{HAC } p_{\text{holm}} = 1.92 \times 10^{-5}$), '금리+물가'($r = +0.3651, \text{HAC } p_{\text{holm}} = 1.30 \times 10^{-8}$), '기업실적'($r = +0.3464, \text{HAC } p_{\text{holm}} = 8.26 \times 10^{-8}$) 및 테스트 구간($N=82$)의 '시황'($r = +0.5355, \text{HAC } p_{\text{holm}} = 0.0327$), '기업실적'($r = +0.5508, \text{HAC } p_{\text{holm}} = 0.00016$)에서 유사한 양(+)의 동행 관계가 일관되게 확인되었다(부분회귀에서도 테스트 구간 시황 $\beta=+0.5210, p_{\text{holm}}=0.0427$, 기업실적 $\beta=+0.4910, p_{\text{holm}}=0.0009$로 유의). 다만 네이버 데이터랩의 원래 지수(`score`) 역시 조회 기간 내 최댓값을 100으로 둔 상대 지표이므로 이를 절대 검색량이나 실제 검색 횟수로 해석할 수 없으며, API 정규화 구조상 공통 분모나 스케일링의 영향이 완전히 제거되었다고 단정하지 않는다.

---

## Ⅴ. 결 론

### 5.1 연구 요약 및 학술적 기여
본 연구는 2021년 1월부터 2026년 7월까지 수집된 국내 3대 경제 일간지 기사 931,709건을 바탕으로, 미래 정보 누수를 차단한 결정론적 표본 외(Strict OOS) NMF 파이프라인과 다중 국면 활성화 체계를 구축하고 토픽 모델의 방법론적 안정성, 금융시장 지표 및 네이버 검색 트렌드와의 관계를 다각적으로 검증하였다.

본 연구의 핵심 기여는 다음 세 가지로 요약된다:
1. **[방법론적 기여] 한국 경제 뉴스에서 NMF의 적합성·안정성 실증 및 결정론적 Strict OOS 아키텍처 확립**: 어휘 사전(22,193개), IDF, NMF 기저 행렬($H_{\text{train}}$, 14개 토픽), 그리고 국면 표준화 모수($\mu_{\text{train}}, \sigma_{\text{train}}$)를 모두 48개월 학습 기간(2021~2024)에서만 적합·고정하고 19개월 표본 외 테스트 기간(2025~2026.07)으로 투영하는 무누수(Zero-Leakage) 아키텍처를 구현하였다. 동일 학습 코퍼스에서 LDA와 정량 비교($K \in \{10, 12, 14, 16\}$)하여 NMF($K=14$)의 응집도($C_v = 0.8258$), 어휘 다양성($\text{TD@20} = 0.9143$), 연산 효율성 및 도메인 분리 우위를 입증하였으며, 21회 재표본화·초기화 실험을 통해 6대 유효 국면이 100%(21/21회) 재현됨을 확인하였다.
2. **[정보 표현적 기여] 단일 국면 대비 다중 국면 활성화의 정보 보존성(43.75%) 정량화 및 기사 단위 실증**: 한국 경제 뉴스는 전체 67개월 중 58.21%(학습 66.67%, 테스트 36.84%)에서 월 2개 이상의 경제 국면이 동시에 활성화되었으며, 단일 대표 국면 방식으로 표현을 제한할 경우 다중 국면 방식에서 관측된 활성 국면 신호 중 **43.75%(112건 중 49건; 학습 47.19%, 테스트 30.43%)가 별도 국면으로 표현되지 않는다**는 점을 규명하였다. 나아가 자동 선정된 5개 사례 월의 실제 기사 가중치($W$) 역추적을 통해, 단일 방식에서 누락되는 제2·제3 국면(금리 인상기 부동산 경색, 증시 변동기 기업실적 발표 등)의 실체를 기사 원문 수준에서 확인하였다.
3. **[실증적 기여] 시장 수익률 충격(월별) 및 네이버 검색 데이터(주별 1차 차분)와의 강건한 동시점 교차 검증**: 월별 코스피 수익률 충격(`kospi_ret_std`)과의 전체 표본 동시점 HAC 회귀($R^2 = 16.19\%, \text{HAC } F = 4.6833, p = 0.000573$)에서 금리·물가($\beta = -0.7418, p_{\text{holm}} = 0.0024$)와 자본거래($\beta = -0.5299, p_{\text{holm}} = 0.0129$)의 유의한 음(-)의 동행 관계를 확인하였다. 또한 단위근 추세를 제거한 주별 1차 차분 시계열(291주)과 24개 검정 HAC Holm 보정 및 이동 블록 부트스트랩($B=2,000$)을 통해, 전체 기간 4개 국면 쌍의 동조성과 함께 **표본 외 테스트 기간($N=82$주)에서도 '시황'($r = +0.4984, \text{HAC } p_{\text{holm}} = 0.0432$)과 '기업실적'($r = +0.4718, \text{HAC } p_{\text{holm}} = 0.0011$) 두 국면의 동시점($h=0$) 동조성이 재현**됨을 입증하였다.

### 5.2 연구 한계 및 향후 연구
1. **동시점 설명 관계와 사전 예측력의 엄격한 구분**: 본 연구의 월별 코스피 수익률 회귀분석($R^2 = 16.19\%, \text{HAC } F = 4.6833$)은 Strict OOS 텍스트 특징을 사용한 67개월 전체 표본 동시점 설명 회귀이며, 주별 네이버 검색 교차 검증($h=0$) 역시 **동시점(Contemporaneous) 동행 관계**를 검증한 것으로서 미래 주가나 금리 변동의 인과적 예측력을 입증한 것이 아니다. 실제로 월별 주가 하락 조기경보 평가에서 기존 2국면 규칙의 일반 하락 정밀도(67.86%)는 자연발생률(69.23%)을 상회하지 못했고, Phase 5.6의 `z_macro >= 0.5` 단독 대체 규칙 역시 테스트 평가 가능 기간(17개월)에서 경고 1건, 적중 0건($TP=0, FP=1$)에 그쳤다.
2. **비지도 토픽 매핑의 미형성 국면 및 `첨단산업(전기차·배터리 중심)`(`aichip`) 국면의 의미적 한계**: 학습 기간 NMF($K=14$)에서 가계대출(`hhdebt`)은 부동산(`realestate`, 토픽 2)에 차순위(질량비 $0.664$)로 흡수되었고 대외통상(`trade`)은 첨단산업과 경합(토픽 8 경합비 $0.951 \ge 0.90$)하여 독립 국면으로 분리되지 못하였다. 또한 코드 식별자 `aichip`에 매핑된 토픽 12는 주요 키워드가 `차량, 전기차, 자동차, 현대차, 충전, 배터리` 등에 집중되어 있으며, 기존 AI·반도체 검색어 분류체계에 전기차·배터리 세부 그룹이 포함되어 해당 토픽이 매핑되었다(`supported_ev_battery_only`). 따라서 본 연구에서는 실제 토픽의 의미를 반영하여 국면 명칭을 `첨단산업(전기차·배터리 중심)`으로 표기하였으며, 이러한 매핑이 AI·반도체 전반의 의미 타당성을 입증하는 것은 아니라는 한계를 갖는다. 향후 연구에서는 씨드 단어 가중치를 결합한 준지도(Anchored/Seeded) 토픽 모델링이나 문맥 임베딩 결합 기법을 통해 도메인 분리도를 개선할 필요가 있다.
3. **기사 단위 인간 평가 미수행에 따른 의미 타당성 검증의 한계**: 본 연구는 통계적 토픽 응집도($C_v, \text{NPMI}$), 부분표본 재현 안정성, 그리고 대표 사례 월의 실제 기사 원문 추적을 수행하였으나, 비지도 학습으로 도출된 경제 이슈 국면의 의미적 타당성을 복수의 독립 평가자에 의한 기사 단위 블라인드 라벨링(Human Evaluation)으로 검증하지 못했다는 한계를 갖는다. 통계적 응집도와 안정성이 곧 인간의 의미 타당성 평가를 대체하는 것은 아니므로, 향후 연구에서는 다중 평가자 간 일치도(Cohen's $\kappa$ 등)에 기반한 기사 단위 의미 타당성 검증을 수행할 필요가 있다.

---

## REFERENCES
[1] S. R. Baker, N. Bloom, and S. J. Davis, “Measuring Economic Policy Uncertainty,” *The Quarterly Journal of Economics*, vol. 131, no. 4, pp. 1593-1636, Nov. 2016. DOI: 10.1093/qje/qjw024.
[2] L. Bybee, B. Kelly, A. Manela, and D. Xiu, “Business News and Business Cycles,” *The Journal of Finance*, vol. 79, no. 5, pp. 3105-3147, Oct. 2024. DOI: 10.1111/jofi.13377.
[3] L. A. Thorsrud, “Words are the New Numbers: A Newsy Coincident Index of the Business Cycle,” *Journal of Business & Economic Statistics*, vol. 38, no. 2, pp. 393-409, Apr. 2020. DOI: 10.1080/07350015.2018.1506344.
[4] P. C. Tetlock, “Giving Content to Investor Sentiment: The Role of Media in the Stock Market,” *The Journal of Finance*, vol. 62, no. 3, pp. 1139-1168, Jun. 2007. DOI: 10.1111/j.1540-6261.2007.01232.x.
[5] B. Seo, Y. Lee, and H. Cho, “Machine-Learning-Based News Sentiment Index (NSI) of Korea,” *BOK Working Paper*, no. 2022-15 (and *National Accounts Review*, no. 2022-1), Bank of Korea, 2022. DOI: 10.2139/ssrn.4230611. (서범석, 이영환, 조형배, “한국의 기계학습 기반 뉴스심리지수 / 기계학습을 이용한 뉴스심리지수(NSI)의 작성과 활용,” *BOK 경제연구* 제2022-15호 및 *국민계정리뷰* 제2022-1호, 2022.)
[6] B. Seo, “Econometric forecasting using ubiquitous news text: Text-enhanced factor model,” *International Journal of Forecasting*, vol. 41, no. 3, pp. 1055-1072, Jul. 2025. DOI: 10.1016/j.ijforecast.2024.11.001.
[7] S.-H. Kim, Y.-J. Lee, J.-Y. Shin, and K.-Y. Park, “Text Mining for Macroeconomic Analysis,” *Journal of Korean Economic Analysis*, vol. 26, no. 1, pp. 1-65, 2020. (김수현, 이영준, 신진영, 박기영, “거시경제 분석을 위한 텍스트 마이닝,” *한국경제의 분석*, 제26권 제1호, pp. 1-65, 2020.)
[8] S.-H. Kim and W. Lee, “Economic Conditions, Public Sentiment, and News Coverage: A Time-Series Analysis of Economic Agenda Dynamics in South Korea,” *Journalism & Mass Communication Quarterly*, OnlineFirst, Sep. 2026. DOI: 10.1177/10776990261483609.
[9] A. H. Shapiro, M. Sudhof, and D. J. Wilson, “Measuring news sentiment,” *Journal of Econometrics*, vol. 228, no. 2, pp. 221-243, Jun. 2022. DOI: 10.1016/j.jeconom.2020.07.053.
[10] P. Glasserman and H. Mamaysky, “Does Unusual News Forecast Market Stress?,” *Journal of Financial and Quantitative Analysis*, vol. 54, no. 5, pp. 1937-1974, Oct. 2019. DOI: 10.1017/S0022109019000127.
[11] D. D. Lee and H. S. Seung, “Learning the parts of objects by non-negative matrix factorization,” *Nature*, vol. 401, no. 6755, pp. 788-791, Oct. 1999. DOI: 10.1038/44565.
[12] D. M. Blei, A. Y. Ng, and M. I. Jordan, “Latent Dirichlet Allocation,” *Journal of Machine Learning Research*, vol. 3, pp. 993-1022, Jan. 2003.
[13] D. O'Callaghan, D. Greene, J. Carthy, and P. Cunningham, “An analysis of the coherence of descriptors in topic modeling,” *Expert Systems with Applications*, vol. 42, no. 13, pp. 5645-5657, Aug. 2015. DOI: 10.1016/j.eswa.2015.02.055.
[14] R. Egger and J. Yu, “A Topic Modeling Comparison Between LDA, NMF, Top2Vec, and BERTopic to Demystify Twitter Posts,” *Frontiers in Sociology*, vol. 7, 886498, May 2022. DOI: 10.3389/fsoc.2022.886498.
[15] Z. Da, J. Engelberg, and P. Gao, “The Sum of All FEARS: Investor Sentiment and Asset Prices,” *The Review of Financial Studies*, vol. 28, no. 1, pp. 1-32, Jan. 2015. DOI: 10.1093/rfs/hhu072.
[16] S. Youk, H. Kim, and Y. Kim, “The impact of COVID-19 on news reporting and public information-seeking about particulate matter: a time-series analysis of issue competition,” *Quality & Quantity*, vol. 60, no. 5, pp. 17507-17528, Jun. 2026. DOI: 10.1007/s11135-026-02870-3.
[17] J. A. Cho, “Does Search Heat Ignite AI-Stock Volatility? Evidence From Korea's AI Supply Chain,” *Asia-Pacific Journal of Financial Studies*, Early View, Sep. 2026. DOI: 10.1111/ajfs.70060.
[18] Y.-H. Jung, Y.-H. Choi, J.-G. Hong, M.-G. Kang, and S.-T. Kim, “The Short-Term Intervals Stock Volatility Prediction System for Supporting Investment Decision-Making based on News,” *Journal of the Korea Academia-Industrial Cooperation Society*, vol. 26, no. 3, pp. 699-704, Mar. 2025. DOI: 10.5762/KAIS.2025.26.3.699. (정용한, 최연호, 홍준기, 강민구, 김순태, “뉴스 기반의 투자 의사 결정 보조를 위한 단기 시점별 주가 변동 예측 시스템,” *한국산학기술학회논문지*, 제26권 제3호, pp. 699-704, 2025.)
[19] Y. Kim and J.-K. Hwangbo, “The Trend Analysis of Drug-Related News Articles with Topic Modeling,” *Journal of the Korea Institute of Information and Communication Engineering*, vol. 28, no. 3, pp. 356-359, Mar. 2024. DOI: 10.6109/jkiice.2024.28.3.356. (김윤하, 황보준권, “토픽 모델링을 이용한 마약 관련 기사의 연도별 동향 분석,” *한국정보통신학회논문지*, 제28권 제3호, pp. 356-359, 2024.)
[20] J. H. Stock and M. W. Watson, *Introduction to Econometrics*, 4th ed. New York, NY: Pearson, 2019.
[21] W. K. Newey and K. D. West, “A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix,” *Econometrica*, vol. 55, no. 3, pp. 703-708, May 1987. DOI: 10.2307/1913610.
[22] J. D. Hamilton, “A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle,” *Econometrica*, vol. 57, no. 2, pp. 357-384, Mar. 1989. DOI: 10.2307/1912559.
[23] D. García, “Sentiment during Recessions,” *The Journal of Finance*, vol. 68, no. 3, pp. 1267-1300, Jun. 2013. DOI: 10.1111/jofi.12027.
[24] R. F. Engle, “Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation,” *Econometrica*, vol. 50, no. 4, pp. 987-1007, Jul. 1982. DOI: 10.2307/1912773.

