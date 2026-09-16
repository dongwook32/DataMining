# topic_terms.csv — 컬럼 설명

각 토픽 H 행에서 무게가 큰 어휘 상위 25개.

| 컬럼 | 설명 |
|------|------|
| topic | 토픽 번호 0~13 |
| rank | 그 토픽 안에서 무게 순위 (1이 가장 큼) |
| term | 어휘. `doc_term_vocab.csv`의 항 |
| weight | H[topic, term] 값 |
