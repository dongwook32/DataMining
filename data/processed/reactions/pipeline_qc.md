# 통합 파이프라인 점검

생성: `analysis.run_pipeline` · 2026-09-19 09:38

본분석 국면은 NMF다. raw 재수집과 NMF 재적합은 하지 않았다.

## 1. 실행한 단계

- measure_reactions (NMF 국면 × 패널)
- robustness (2026-01 이후 제외)
- rq4_search (뉴스 비중·라벨 vs 데이터랩)
- fallback_topics LDA (같은 행렬, 매핑 규칙 동일, 수동 덮어쓰기 없음)
- measure_reactions on LDA 국면 → reactions_lda/

## 2. 폴백 판정

| 항목 | 값 |
|------|-----|
| 트리거 | 켜짐 |
| 기준 α | 0.05 |
| 주 종속 KW 유의 하나라도 | 아니오 |
| KW p `kospi_ret` | 0.1295 |
| KW p `usdkrw_ret` | 0.9212 |
| KW p `ccsi_diff` | 0.3169 |

이유:
- 주 종속변수 3개 KW가 모두 p>=0.05 — 단일 라벨 그룹 차이만으로는 약함

BERTopic: bertopic 미설치 — 폴백 2순위 건너뜀. LDA만 실행.

## 3. 산출 위치

| 단계 | 경로 |
|------|------|
| 본분석 반응 | `data/processed/reactions/` |
| 강건성 | `robustness_*.csv`, `robustness_qc.md` |
| RQ4 | `rq4_*.csv`, `rq4_qc.md` |
| 폴백 LDA 국면 | `data/processed/regimes_lda/` |
| 폴백 반응 | `data/processed/reactions_lda/` |
