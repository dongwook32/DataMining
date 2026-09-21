# 연구 결과 색인 (수치 원본은 CSV·QC)

이 문서는 초고가 아니다. 표의 위치와 확인한 수치만 가리킨다.
반올림한 값은 QC 표용이고, 인용은 CSV 원값을 쓴다.

본분석 국면은 NMF다. LDA는 폴백이다. BERTopic은 표본 비교이며 본국면을 대체하지 않는다.

같은 수치를 그림·표로 묶은 브리핑은 `docs/한국형_경제이슈국면_연구결과보고서.pdf`다.
재생성: `python -m analysis.build_results_report`. 새 분석이 아니다.

## RQ3 — 국면별 반응 (NMF, 6그룹)

원본: `data/processed/reactions/regime_reaction.csv`, `regime_tests.csv`, `reactions_qc.md`

| 종속변수 | KW H | p | epsilon² |
|----------|------|---|----------|
| kospi_ret | 8.527401658920496 | 0.12946540630153042 | 0.057826256703614694 |
| usdkrw_ret | 1.4278825432687938 | 0.9212390971597227 | -0.058559302569364036 |
| ccsi_diff | 5.89205337576037 | 0.31686473210419364 | 0.014623825832137215 |
| base_rate_diff | 13.211952271720104 | 0.021471472012258595 | 0.13462216838885416 |
| kospi_ret_std | 9.92737970984237 | 0.07731925491451119 | 0.08077671655479295 |

주 3개(코스피·환율·CCSI)는 KW p≥0.05. Holm 보정 후 국면쌍 p<0.05는 0/60.
`base_rate_diff`만 KW p<0.05. 금리 국면 10개월 평균 `kospi_ret` = -3.73788236578104,
AI반도체 13개월 = 7.738230536251667 (`regime_reaction.csv`).

전환 이벤트: `event_study_summary.csv`. 국면 신호 전환 4건(2022-03, 2023-02, 2025-02, 2025-11).
2026-03·07은 PELT에 없음.

## 강건성

원본: `robustness_compare.csv`, `robustness_qc.md`

2026 제외 60개월. 주 3개와 `base_rate_diff`의 유의 여부(p<0.05)는 뒤집히지 않음.
`kospi_ret` p 0.1294654063015304 → 0.3042894090839844.

## RQ4 — 검색

원본: `rq4_corr.csv`, `rq4_concordance.csv`, `rq4_qc.md`

뉴스 비중 vs 검색 z Pearson (n=67): 금리 0.524986317017003, 부동산 0.5582036473886888,
가계대출 0.4211041078805555, 대외통상 0.33789074546753217, AI반도체 0.7505857678829452,
증시실적 0.11345264061465014. 물가는 뉴스 비중 분산 0.

라벨 일치율(검색 z argmax): 22/67 = 0.3283582089552239. 7국면 균등 무작위는 1/7.

## 폴백 LDA (본분석 대체 아님)

원본: `data/processed/regimes_lda/`, `data/processed/reactions_lda/`

트리거: 주 3개 KW p≥0.05 (`fallback_decision.json`).
LDA는 금리·가계대출·물가 토픽을 매핑하지 못함 → 그룹 4개(부동산 17, 대외통상 18, AI반도체 14, 증시실적 18).
`kospi_ret` KW H=11.810272660425, p=0.00806216709795685.
Holm p<0.05: 대외통상 vs AI반도체, 대외통상 vs 증시실적 (`kospi_ret`), 대외통상 vs AI반도체 (`kospi_ret_std`).
환율·CCSI는 여전히 p≥0.05.

행렬 sha256은 NMF와 같음: `ceb9483da92f409928619a4bfda24dc140adcdf6073c321f0319b87dc1f28cff`.

## 폴백 BERTopic (본분석 대체 아님)

원본: `data/processed/regimes_bertopic/`, `data/processed/reactions_bertopic/`

명령: `python -m analysis.fallback_bertopic`
표본 67,000건(월 1,000, seed 42). 임베딩 `paraphrase-multilingual-MiniLM-L12-v2`, 656.6480297999951s.
HDBSCAN이 토픽 6개(+이상치 48)만 남김. 요청 14보다 적음. 시계열은 전량 변환이 아니라 이 표본.
같은 키워드 질량 매핑에서 5토픽이 증시실적, 1토픽이 기타. z-우세는 67개월 전부 증시실적.
그룹이 1개라 KW는 정의되지 않음 (`regime_tests.csv` 통계량 결측).
NMF 6국면 RQ3를 대체하는 결과가 아니다.
