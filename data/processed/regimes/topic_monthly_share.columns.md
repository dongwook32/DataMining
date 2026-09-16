# topic_monthly_share.csv — 컬럼 설명

전량 행렬로 적합한 NMF 14토픽의 월별 비중. 탐색용
`data/processed/corpus/topic_monthly_share.csv`와 파일명은 같으나 **다른 적합**이다.

| 컬럼 | 설명 |
|------|------|
| month | 연-월. 조인 키 |
| topic_0 ~ topic_13 | 그달 문서 토픽 비중의 평균. 한 행의 합 = 1 |

어떤 번호가 어떤 국면인지는 `topic_regime_map.csv`를 본다.
