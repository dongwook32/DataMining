# 국면별 반응 · RQ4 · 강건성

`analysis.measure_reactions` · `robustness` · `rq4_search` · `run_pipeline`이 쓰는 폴더입니다.
본분석 국면은 `../regimes/regime_monthly.csv`(NMF, z-우세)입니다.

| 파일 | 내용 |
|------|------|
| `regime_reaction.csv` | 국면 × 종속변수 기술통계 |
| `regime_tests.csv` | KW / ANOVA / Levene |
| `pairwise_tests.csv` | 국면쌍 Mann-Whitney (Holm) |
| `share_regression.csv` | 비중 z → HAC OLS |
| `regime_regression.csv` | 국면 더미 + 통제 HAC |
| `event_study.csv` | 전환 ±3개월 경로 |
| `event_study_summary.csv` | 누적 변화 + 플라시보 분위 |
| `robustness_no2026_*.csv` | 2026 제외 재추정 |
| `robustness_compare.csv` | 전체 vs 제외 KW 비교 |
| `rq4_corr.csv` | 뉴스 비중 ↔ 검색 상관 |
| `rq4_concordance.csv` | 라벨 일치율 |
| `rq4_monthly.csv` | 월별 뉴스·검색 라벨 |
| `fallback_decision.json` | 폴백 트리거 판정 |
| `*_qc.md` | 점검 리포트 |

폴백 LDA 산출은 `../regimes_lda`, `../reactions_lda`에 있습니다.
