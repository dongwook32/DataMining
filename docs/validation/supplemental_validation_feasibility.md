# 기존 데이터 기반 추가 실증 연구 실행 가능성 감사 보고서 (`supplemental_validation_feasibility.md`)

- **작성 일시:** 2026-11-01
- **분석 환경:** Windows / Python (`.\.venv\Scripts\python.exe`) / Git
- **감사 기준 파이프라인:** Phase 5.6 Strict OOS 결정론적 산출물 (`data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/`)
- **원칙:** 기존 데이터, 모델, 검증 CSV 및 논문 초안 원본을 일절 수정하거나 덮어쓰지 않고, 읽기 전용으로 감사를 수행함.

---

## 1. 프로젝트 상태 및 아티팩트 점검 결과

### 1.1 Git 상태 및 작업 디렉터리
- **현재 디렉터리:** `C:\Users\CDW\1_Project\DataMining`
- **Git 상태:** 기존 파일 수정 및 미추적 파일(검증 아티팩트 등) 보존 상태 확인 완료. (자동 commit/push 금지 준수)

### 1.2 Phase 5.6 Strict OOS 아티팩트 무결성 추적
`data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/` 내 다음 핵심 파일들의 실재와 내용을 전수 확인하였다:
1. `core_meta.json`:
   - 전체 기사: 931,709건
   - 학습 기간(`train_docs`): 643,095건 (2021-01 ~ 2024-12, 48개월)
   - 테스트 기간(`eval_docs`): 288,614건 (2025-01 ~ 2026-07, 19개월)
   - NMF 피팅 표본: 144,000건 (`fit_sample_month_range`: `['2021-01', '2024-12']`)
   - NMF 파라미터: `n_components=14`, `init='nndsvd'`, `random_state=42`, `tol=1e-4`
2. `vocab_idf.csv`: 학습 기간에서만 도출된 어휘 사전(22,193개 단어) 및 학습용 IDF 벡터 저장 확인.
3. `nmf_H.npy`: 학습 기간 144,000개 문서에서 적합된 NMF components $H$ ($14 \times 22,193$) 저장 확인.
4. `models.joblib`: 고정 변환용 sklearn 객체(`tfidf`: TfidfTransformer, `nmf`: NMF, `vocab`: 단어 리스트) 저장 확인.
5. `monthly_topic_share.csv`: 67개월 전체 월별 14개 토픽 점유율 저장 확인.
6. `phase5_6_topic_regime_mapping.csv` 및 `phase5_6_train_only_regime_monthly.csv`:
   - 6개 유효 국면(`macro`, `realestate`, `aichip`, `market`, `earnings`, `capital`) 매핑 및 학습 48개월 고정 표준화 모수($\mu, \sigma$) 저장 확인.
   - 가계부채(`hhdebt`)와 대외통상(`trade`)은 독립 국면 미형성(`unrepresented / NaN`) 상태임이 공식 확인됨.

### 1.3 네이버 검색 데이터랩 자료 점검
- `datalab_regime_daily.csv` (27,055행, 2016-01-01 ~ 2026-07-31, 3,865일, 7개 그룹: 물가, 금리, 부동산, 가계대출, 대외통상, AI반도체, 증시실적)
- `datalab_sub_daily.csv` (108,220행, 2016-01-01 ~ 2026-07-31, 3,865일, 28개 하위 그룹: 소비자물가, 기준금리, 국내증시, 공모주, 기업실적 등)
- `datalab_regime_monthly.csv` (889행, 127개월), `datalab_sub_monthly.csv` (3,556행, 127개월)
- **지표 정의:** `score_rel = score / anchor_score` (앵커 키워드 기준 상대비율 지표로, 그룹 간 절대 크기 비교 불가함을 엄격히 인지).

### 1.4 뉴스 코퍼스 점검
- `data/processed/corpus/news_corpus.parquet`: 931,709건 전수 보존 (`article_id`, `date`, `month`, `source`, `title`, `keywords`, `content` 등 완비).

---

## 2. 세부 연구별 실행 가능성 (Feasibility) 최종 판정

| 연구 과제 | 과제 내용 | 실행 가능성 판정 | 판정 근거 및 필요 조치 |
| :--- | :--- | :---: | :--- |
| **연구 A** | 단일 국면 vs 다중 국면 활성화 비교 실험 | **READY** | `phase5_6_train_only_regime_monthly.csv`에 학습 48개월 고정 표준화 $z$-score가 이미 존재하므로 즉시 단일 대표 국면(Argmax, Hurdle Argmax)과 다중 국면($z \ge 0.5$)의 활성화 행렬, 월별 국면 조합, 정보 보존율 지표를 산출 가능함. |
| **연구 B** | 뉴스와 네이버 검색 관심도의 주별 교차 검증 | **READY** | 일별 뉴스 코퍼스(`news_corpus.parquet`)와 일별 검색 데이터(`datalab_regime_daily.csv`, `datalab_sub_daily.csv`)가 2021-01~2026-07 전 구간에 걸쳐 일치함. ISO week 기준 주별 패널 생성, 1차 차분 상관, 사전 정의 시차($h=-1, 0, +1$) 및 120개 검정 Holm 보정 분석 가능. |
| **연구 C** | 사람의 직접 라벨링을 이용한 경제 국면 의미 타당성 검증 | **READY (표본·블라인드 파일 생성)** / **PARTIAL (최종 평가)** | 테스트 기간(2025-01~2026-07, 19개월, 288,614건)에서 19개월 균등 층화 무작위 추출($N=380$, 월별 20건, 언론사 균등)로 블라인드 평가 파일(Batch A, Batch B), 코드북, 조인키 생성 완비 가능. 단, 실제 사람 2명의 라벨링 입력이 완료되기 전까지는 Cohen's kappa 및 모델 F1 최종 수치 산출을 보류함. |

---

## 3. 작업 로드맵 및 분석 원칙
1. **분석 격리:** 모든 신규 스크립트는 `analysis/supplemental_validation/`, 결과 산출물은 `data/processed/supplemental_validation/`에만 생성한다.
2. **Strict OOS 원칙 준수:** Phase 5.6의 학습 전용 아티팩트와 고정 모수를 엄격히 따르며, 테스트 기간에서 사후 모수를 재계산하지 않는다.
3. **가식적 성과 배제:** 통계적으로 유의하지 않거나 다중 국면이 단일 국면 대비 뚜렷한 장점을 보이지 않더라도 데이터를 있는 그대로 투명하게 보고한다.

