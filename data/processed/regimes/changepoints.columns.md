# changepoints.csv — 컬럼 설명

PELT(L2)가 토픽 비중 벡터·국면 비중 벡터에서 찾은 전환. 페널티는
`dim × ln(n)` (BIC)으로 미리 고정한다. 결과에 맞춰 바꾸지 않는다.

| 컬럼 | 설명 |
|------|------|
| signal | `topics` (14차원) 또는 `regimes` (7차원) |
| model | `l2_z` (열별 z점수 뒤 L2) |
| penalty | 사용한 페널티 값 |
| cp_month | 새 구간의 첫 달 (전환이 드러난 달) |
| from_label | 이전 구간, 표준화 신호 평균의 최대 축 |
| to_label | 이후 구간, 표준화 신호 평균의 최대 축 |
| segment_start | 이전 구간의 첫 달 |
| segment_end | 이전 구간의 마지막 달 |

마지막 구간 끝은 신호 길이와 같으므로 행으로 두지 않는다.
최소 구간은 3개월이다.
