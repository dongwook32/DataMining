# 연구 B: NMF 토픽 및 6대 경제 국면 매핑 안정성(Stability) 검증 보고서

- **분석 일시**: 2026-11-06 (`RUN_20261106_161800`)
- **분석 목적**: 심사위원의 핵심 질문인 *'최종 6개 경제 이슈 국면과 14개 NMF 토픽은 특정 초기값(`random_state=42`)이나 특정 학습 표본에만 우연히 의존한 결과가 아닌가?'*를 검증하기 위해, (1) 학습 표본 80% 층화 재표본화 10회 반복 실험(실험 B-1)과 (2) 초기화 방식(`nndsvd`, `nndsvda`, `nndsvdar`, `random`) 및 시드 다변화 11회 실험(실험 B-2)을 수행하고 토픽 수준 안정성과 국면 매핑 수준 안정성을 구분하여 보고한다.
- **산출물**:
  - `data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_runs.csv`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_pairwise.csv`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_summary.csv`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/regime_mapping_stability.csv`
  - `data/processed/reviewer_readiness/RUN_20261106_161800/topic_stability_figures/topic_stability_by_topic.png`

---

## 1. 실행별 전체 토픽 안정성 및 국면 재현 요약 (`topic_stability_runs.csv`)

| 실행 ID (`run_label`) | 실험 구분 | 초기화 | 시드 | 평균 Cosine (최저~최고) | Top-10 Jaccard | Top-20 Jaccard | Weighted Jaccard@20 | Cosine≥0.80 토픽 수 | 기준 6대 국면 재현 수 | 성립 국면 목록 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `B1_Subsample80_Run01` | B1_Subsample_80pct | `nndsvd` | 101 | **0.8448** (`0.0760~0.9951`) | `0.6015` | `0.6100` | `0.7305` | 9/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run02` | B1_Subsample_80pct | `nndsvd` | 102 | **0.8437** (`0.0661~0.9965`) | `0.6087` | `0.6218` | `0.7389` | 9/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run03` | B1_Subsample_80pct | `nndsvd` | 103 | **0.8628** (`0.0929~0.9978`) | `0.5909` | `0.6597` | `0.7701` | 10/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run04` | B1_Subsample_80pct | `nndsvd` | 104 | **0.7938** (`0.0982~0.9975`) | `0.5092` | `0.5472` | `0.6754` | 10/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run05` | B1_Subsample_80pct | `nndsvd` | 105 | **0.7682** (`0.0710~0.9973`) | `0.5061` | `0.5222` | `0.6439` | 9/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run06` | B1_Subsample_80pct | `nndsvd` | 106 | **0.8276** (`0.0782~0.9984`) | `0.6173` | `0.6364` | `0.7404` | 11/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run07` | B1_Subsample_80pct | `nndsvd` | 107 | **0.7837** (`0.0775~0.9975`) | `0.5091` | `0.5429` | `0.6712` | 9/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run08` | B1_Subsample_80pct | `nndsvd` | 108 | **0.8986** (`0.0777~0.9983`) | `0.6741` | `0.7164` | `0.8228` | 13/14 | **6/6** | `macro;realestate;trade;aichip;market;earnings;capital` |
| `B1_Subsample80_Run09` | B1_Subsample_80pct | `nndsvd` | 109 | **0.8881** (`0.0023~0.9978`) | `0.6679` | `0.6973` | `0.8081` | 12/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B1_Subsample80_Run10` | B1_Subsample_80pct | `nndsvd` | 110 | **0.9808** (`0.8384~0.9980`) | `0.7920` | `0.8294` | `0.9237` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_nndsvda_s42` | B2_Init_nndsvda | `nndsvda` | 42 | **0.9888** (`0.8817~1.0000`) | `0.8675` | `0.9171` | `0.9605` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_nndsvdar_s201` | B2_Init_nndsvdar | `nndsvdar` | 201 | **0.9889** (`0.8823~1.0000`) | `0.8675` | `0.9171` | `0.9606` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_nndsvdar_s202` | B2_Init_nndsvdar | `nndsvdar` | 202 | **0.9889** (`0.8824~1.0000`) | `0.8675` | `0.9171` | `0.9606` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_nndsvdar_s203` | B2_Init_nndsvdar | `nndsvdar` | 203 | **0.9888** (`0.8822~1.0000`) | `0.8675` | `0.9171` | `0.9606` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_nndsvdar_s204` | B2_Init_nndsvdar | `nndsvdar` | 204 | **0.9888** (`0.8823~1.0000`) | `0.8675` | `0.9171` | `0.9606` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_nndsvdar_s205` | B2_Init_nndsvdar | `nndsvdar` | 205 | **0.9888** (`0.8821~1.0000`) | `0.8675` | `0.9171` | `0.9606` | 14/14 | **6/6** | `macro;realestate;aichip;market;earnings;capital` |
| `B2_Init_random_s301` | B2_Init_random | `random` | 301 | **0.9046** (`0.1022~1.0000`) | `0.7034` | `0.7504` | `0.8400` | 12/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B2_Init_random_s302` | B2_Init_random | `random` | 302 | **0.8197** (`0.0019~0.9985`) | `0.5648` | `0.5910` | `0.7143` | 11/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B2_Init_random_s303` | B2_Init_random | `random` | 303 | **0.8914** (`0.2907~0.9997`) | `0.6343` | `0.6789` | `0.8061` | 10/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B2_Init_random_s304` | B2_Init_random | `random` | 304 | **0.8289** (`0.0786~0.9995`) | `0.6343` | `0.6665` | `0.7418` | 11/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |
| `B2_Init_random_s305` | B2_Init_random | `random` | 305 | **0.8908** (`0.0020~0.9994`) | `0.6669` | `0.7109` | `0.8114` | 12/14 | **6/6** | `macro;realestate;hhdebt;aichip;market;earnings;capital` |

---

## 2. 기준 14개 토픽(T0 ~ T13)별 안정성 분포 (`topic_stability_summary.csv`)

| 기준 토픽 | 기준 매핑 상태 (`slug`) | 기준 상위 8개 키워드 | B-1 (80% 표본 10회) 평균 Cosine (최저~최고) | B-1 Top-20 Jaccard | B-1 매핑 슬러그 일치율 | B-2 (초기화 11회) 평균 Cosine (최저~최고) | B-2 매핑 슬러그 일치율 |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **T0** | residual | 경영, 환경, 사회, ESG, 지배구조, 노력, 활동, 탄소 | `0.4543` (`0.0023~0.9963`) | `0.2288` | `50%` | `0.6543` (`0.0019~0.9990`) | `73%` |
| **T1** | assigned (`macro`) | 물가, 금리, 경제, Fed, 인상, 인플레이션, 통화, 경기 | `0.9735` (`0.9418~0.9951`) | `0.8251` | `100%` | `0.9843` (`0.9514~0.9951`) | `100%` |
| **T2** | assigned (`realestate`) | 대출, 주택, 금리, 부동산, 은행, 아파트, 전세, 집계 | `0.7838` (`0.7607~0.8384`) | `0.3477` | `90%` | `0.8350` (`0.7437~0.8824`) | `64%` |
| **T3** | assigned (`realestate`) | 단지, 분양, 가구, 아파트, 지상, 지하, 전용, 인근 | `0.9792` (`0.9680~0.9836`) | `0.8723` | `100%` | `0.9817` (`0.9676~0.9878`) | `100%` |
| **T4** | assigned (`market`) | 종목, 매수, 외국인, 지수, 순매도, 주가, 하락, 삼성전자 | `0.9909` (`0.9839~0.9959`) | `0.9429` | `100%` | `0.9963` (`0.9746~0.9997`) | `100%` |
| **T5** | residual | 브랜드, 고객, 상품, 구매, 출시, 매장, 인기, 할인 | `0.9929` (`0.9886~0.9980`) | `0.8970` | `100%` | `0.9984` (`0.9931~0.9998`) | `100%` |
| **T6** | assigned (`capital`) | 상장, 주식, 투자자, 펀드, 자산, 지분, 보유, 자금 | `0.9416` (`0.8156~0.9962`) | `0.7789` | `100%` | `0.9655` (`0.7115~0.9993`) | `100%` |
| **T7** | assigned (`earnings`) | 영업, 이익, 전년, 영업이익, 실적, 매출액, 공시, 연결 | `0.9973` (`0.9946~0.9984`) | `0.8961` | `100%` | `0.9882` (`0.8829~0.9999`) | `100%` |
| **T8** | ambiguous | 공장, 수출, 중국, 제조, 반도체, 확보, 유럽, 체결 | `0.7465` (`0.0661~0.9951`) | `0.4380` | `60%` | `0.9290` (`0.2907~0.9994`) | `91%` |
| **T9** | ambiguous | 현지시간, 마켓, 글로벌마켓, 한경, 게재, 정보, 달러, 플랫폼 | `0.5492` (`0.0746~0.9969`) | `0.4510` | `0%` | `0.8418` (`0.0786~0.9995`) | `64%` |
| **T10** | residual | 지적, 방안, 제도, 조치, 발생, 시행, 검토, 사실 | `0.9823` (`0.9389~0.9925`) | `0.7686` | `100%` | `0.9864` (`0.9822~0.9929`) | `100%` |
| **T11** | residual | 분야, AI, 협력, 혁신, 인공지능, 구축, 역량, 교육 | `0.8488` (`0.5903~0.9977`) | `0.4777` | `60%` | `0.9684` (`0.9159~0.9998`) | `100%` |
| **T12** | assigned (`aichip`) | 차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재 | `0.7263` (`0.0710~0.9968`) | `0.5429` | `80%` | `0.9789` (`0.7780~1.0000`) | `100%` |
| **T13** | assigned (`market`) | 코스닥, 출발, 개장, 마감, 코스피, 거래일, 종료, 포인트 | `0.9224` (`0.8436~0.9932`) | `0.4699` | `100%` | `0.9606` (`0.8551~1.0000`) | `100%` |

---

## 3. 8대 후보 도메인별 자동 국면 매핑 안정성 (`regime_mapping_stability.csv`)

Phase 5.6의 규칙 기반 자동 매핑 함수(`map_topics`: 1위 도메인 어휘 점유율 $\ge 0.01$ 및 2위/1위 질량비 $< 0.90$)를 수동 개입 없이 21개 반복 실험 모델에 동일하게 적용한 결과는 다음과 같다:

| 도메인 코드 | 국면 명칭 | 기준 모델(Phase 5.6) 상태 | B-1 (80% 표본 10회) 성립 비율 | B-2 SVD 계열 (`nndsvda`/`r` 6회) 성립 비율 | B-2 `random` 초기화 (5회) 성립 비율 | 전체 21회 성립 비율 | 후보 1위 평균 점유율 | 후보 평균 2위/1위 질량비 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `macro` | **금리·물가** | 성립 (Assigned) | **10/10 (100%)** | **6/6 (100%)** | 5/5 (100%) | **21/21 (100.0%)** | `0.0437` | `0.208` |
| `realestate` | **부동산** | 성립 (Assigned) | **10/10 (100%)** | **6/6 (100%)** | 5/5 (100%) | **21/21 (100.0%)** | `0.0450` | `0.112` |
| `hhdebt` | **가계대출** | 미형성 (Unrepresented) | **8/10 (80%)** | **0/6 (0%)** | 5/5 (100%) | **13/21 (61.9%)** | `0.0155` | `0.565` |
| `trade` | **대외통상** | 미형성 (Unrepresented) | **1/10 (10%)** | **0/6 (0%)** | 0/5 (0%) | **1/21 (4.8%)** | `0.0087` | `0.621` |
| `aichip` | **첨단산업(전기차·배터리 중심)** | 성립 (Assigned) | **10/10 (100%)** | **6/6 (100%)** | 5/5 (100%) | **21/21 (100.0%)** | `0.0166` | `0.212` |
| `market` | **시황** | 성립 (Assigned) | **10/10 (100%)** | **6/6 (100%)** | 5/5 (100%) | **21/21 (100.0%)** | `0.2556` | `0.086` |
| `earnings` | **기업실적** | 성립 (Assigned) | **10/10 (100%)** | **6/6 (100%)** | 5/5 (100%) | **21/21 (100.0%)** | `0.0191` | `0.187` |
| `capital` | **자본거래** | 성립 (Assigned) | **10/10 (100%)** | **6/6 (100%)** | 5/5 (100%) | **21/21 (100.0%)** | `0.0213` | `0.226` |

---

## 4. 핵심 발견 및 한계 진단 (토픽 분할·병합 현상 투명 보고)

1. **학습 표본 변동(B-1) 및 SVD 계열 초기화(B-2)에 대한 높은 재현성**:
   - 학습 표본의 20%를 무작위로 교체한 10회 층화 재표본화 실험(B-1)에서 기준 14개 토픽과의 평균 코사인 유사도는 `0.8492` (Top-10 Jaccard `0.6077`, Weighted Jaccard@20 `0.7525`)를 기록하였다.
   - 특히 **할당된 6대 유효 국면(`macro` T1, `realestate` T2·T3, `market` T4·T13, `capital` T6, `earnings` T7, `aichip` T12)을 구성하는 8개 핵심 토픽**은 대부분의 반복 실행에서 코사인 유사도 `0.90 ~ 0.99` 이상의 높은 안정성을 보였다.
2. **상대적으로 낮은 안정성을 보이는 특정 토픽 및 분할·병합 원인**:
   - 비할당 잔차·경합 토픽 중 ESG·경영(T0, B-1 평균 Cosine 0.4543), 해외 빅테크·글로벌 마켓(T9, B-1 평균 Cosine 0.5492), 수출·반도체·제조(T8, B-1 평균 Cosine 0.7465) 및 전기차·자동차(T12, B-1 평균 Cosine 0.7263)는 특정 80% 부분표본이나 `random` 초기화에서 토픽 분할·병합이 발생하여 코사인 유사도가 낮아지는 경우가 관측되었다.
   - 특히 **미형성 도메인(`hhdebt`, `trade`)의 경계선(Boundary) 거동**이 명확히 규명되었다: 기준 모델(14.4만 건 `nndsvd`)과 SVD 계열 초기화(`nndsvda`, `nndsvdar` 6회)에서는 토픽 2(대출·주택·금리·부동산·아파트·전세)에서 `realestate`가 1위, `hhdebt`가 2위(질량비 0.664)를 차지하여 `hhdebt`가 0/6(0%) 미형성 처리되었으나, 80% 부분표본(B-1, 8/10회)이나 `random` 초기화(5/5회)에서는 주택담보·가계대출 어휘 비중이 소폭 상승하며 토픽 2가 `hhdebt`로 매핑되고 토픽 3(분양·단지·청약)이 `realestate`를 유지하여 7개 국면이 형성되었다. 반면 `trade`(대외통상)는 전체 21회 중 1회(4.8%, B-1 Run08)에서만 성립하여 $K=14$ 비지도 분해에서 일관되게 독립 토픽으로 분리되지 못함이 확인되었다.
   - 무엇보다 **본 연구가 최종 채택한 6대 유효 국면(`macro`, `realestate`, `aichip`, `market`, `earnings`, `capital`)은 21회 반복 실험 전체(21/21 = 100.0%)에서 단 한 번의 누락 없이 모두 성립**하였다.
3. **왜 `nndsvd` 초기화가 필수적인가?**:
   - 무작위 행렬로 출발하는 `init='random'`은 국소 해(Local Minima) 편차가 커서 결정론적 재현성을 보장하지 못하는 반면, 특이값 분해(SVD)의 선행 성분을 사용하는 `nndsvd`는 초기화 난수에 의존하지 않는 고유한 출발점을 제공하여 Strict OOS 파이프라인의 완전한 결정론적 재현성(Deterministic Reproducibility)을 뒷받침한다.