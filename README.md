# DataMining — 한국형 경제 이슈 국면 탐지

뉴스·검색 데이터로 경제 이슈 국면(물가·금리·부동산·대외 등)을 탐지하고,
국면별 코스피·환율·CCSI 반응 패턴을 분석하는 연구 저장소입니다.

**쉬운 설명 (비전공자·발표):** [`docs/연구_쉬운_요약.md`](docs/연구_쉬운_요약.md)  
**재실행·코드·용어:** [`docs/기술_참고.md`](docs/기술_참고.md) · **문서 목록:** [`docs/README.md`](docs/README.md)  
수치 색인: [`docs/results.md`](docs/results.md) · 브리핑 PDF: [`docs/한국형_경제이슈국면_연구결과보고서.pdf`](docs/한국형_경제이슈국면_연구결과보고서.pdf)  
진행 일지: [`RESEARCH_LOG.md`](RESEARCH_LOG.md) · PDF용 차별점·RQ 요약: [`docs/research_plan.md`](docs/research_plan.md)

## 현재 단계

**Step 4~5 완료** — NMF 국면으로 반응·강건성·RQ4를 돌리고, 그룹 차이가 약하면 LDA 폴백만 켭니다.
BERTopic은 같은 날 표본 비교로 돌렸고, 본국면은 NMF입니다.
논문 본문은 쓰지 않습니다. 표·수치·재현 코드가 산출입니다.

| 단계 | 상태 |
|------|------|
| 1. 설계·파일럿 | 완료 |
| 2. 본데이터 (빅카인즈·ECOS·데이터랩) | 완료 |
| 2.5 전처리 (문서-어휘 행렬 · 월 패널) | 완료 |
| 3. 국면 탐지 모델 (NMF) | 완료 |
| 4. 반응 분석 | 완료 |
| 5. 강건성 · RQ4 · (조건부) LDA 폴백 · BERTopic 비교 | 완료 |

**분석 기간: 2021-01 ~ 2026-07** (빅카인즈 코퍼스 보유 기간, 67개월).
ECOS·데이터랩은 차분·시차용 lead-in을 위해 2016-01부터 받아 둡니다.

**국면 대분류**: 물가 · 금리 · 부동산 · 가계대출 · 대외통상 · AI반도체 · 증시실적 —
코퍼스 토픽 마이닝으로 도출했습니다 (근거는 `api/datalab_keyword_sets.py` 주석).

## 폴더 구조

```text
analysis/          # 본분석 스크립트
api/               # ECOS·네이버 API 클라이언트, 수집기
preprocess/        # 빅카인즈 → 통합 코퍼스, 키워드 마이닝
crawler/           # 수집 유틸 (빅카인즈는 수동 다운로드)
config/            # config.yaml
data/
  raw/
    bigkinds/      # 본연구 뉴스 (수동 투입)
    ecos/          # ECOS 지표
    datalab/       # 네이버 데이터랩
  processed/
    corpus/        # 통합 뉴스 코퍼스 + 키워드 마이닝 + 문서-어휘 행렬
    panel/         # 지표·검색·뉴스량 월 패널 (분석 입력)
    regimes/       # 월별 국면 시계열 (NMF 본분석)
    reactions/     # 국면별 반응표 · RQ4 · 강건성 · pipeline_qc
    regimes_lda/   # 폴백 LDA 국면 (트리거 시에만)
    reactions_lda/ # 폴백 반응 재추정
    regimes_bertopic/   # BERTopic 비교 국면 (표본, NMF 유지)
    reactions_bertopic/ # BERTopic 비교 반응
docs/              # 계획서 · 용어 · 함수 · 파이프라인 · 결과 색인 · 브리핑 PDF
```

## 환경 설정

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # 키 입력
```

## 데이터 투입

```powershell
# 1. 빅카인즈 엑셀은 data/raw/bigkinds/<연도>/ 에 수동 투입 (스펙은 해당 폴더 README)
python -m preprocess.build_corpus --audit   # 투입 상태 점검
python -m preprocess.build_corpus           # 통합 코퍼스 생성

# 2. ECOS 월별 지표
python -m api.collect_ecos

# 3. 네이버 데이터랩 검색 트렌드
python -m api.collect_datalab
```

## 전처리

수집이 끝난 뒤 분석 입력을 만드는 단계입니다. 둘 다 결정적이라 같은 입력이면 같은 결과가 나옵니다.

```powershell
python -m preprocess.build_doc_matrix   # 코퍼스 전량 → 문서×어휘 행렬 (약 1분 30초)
python -m preprocess.build_panel        # 지표·검색·뉴스량 → 월 패널 + QC 리포트
```

## 국면 탐지

```powershell
python -m analysis.detect_regimes              # TF-IDF + NMF → 월별 국면 + 변화점
python -m analysis.detect_regimes --remap-only # 매핑·변화점만 다시
```

| 산출 | 형태 | 쓰는 곳 |
|------|------|---------|
| `data/processed/corpus/doc_term.npz` | 931,709 × 28,343 희소행렬 | Step 3 토픽모델 |
| `data/processed/panel/monthly_panel.csv` | 127개월 × 54열 | Step 4 반응 분석 |
| `data/processed/panel/panel_qc.md` | 품질 점검 리포트 | 매 실행마다 갱신 |
| `data/processed/regimes/regime_monthly.csv` | 67개월 국면 라벨·비중 | Step 4 조인 |
| `data/processed/regimes/changepoints.csv` | PELT 전환 시점 | Step 4 이벤트 창 |
| `data/processed/regimes/regimes_qc.md` | 매핑·피크·전환 점검 | 매 실행마다 갱신 |

## 반응 · 강건성 · 검색 · 통합 실행

`processed` 캐시가 있으면 raw를 다시 받지 않습니다.

```powershell
python -m analysis.run_pipeline              # 반응 → 강건성 → RQ4 → (조건부) LDA
python -m analysis.measure_reactions         # RQ3만
python -m analysis.robustness                # 2026 제외
python -m analysis.rq4_search                # 뉴스 vs 검색
python -m analysis.fallback_topics           # LDA 폴백만 강제
python -m analysis.fallback_bertopic         # BERTopic 비교 (표본, NMF 유지)
python -m analysis.build_results_report      # docs/ 브리핑 PDF (새 분석 아님)
```

| 산출 | 내용 |
|------|------|
| `data/processed/reactions/regime_reaction.csv` | 국면별 지표 평균·분산 |
| `data/processed/reactions/regime_tests.csv` | KW / ANOVA / Levene |
| `data/processed/reactions/event_study_summary.csv` | 전환 ±3개월 + 플라시보 분위 |
| `data/processed/reactions/robustness_compare.csv` | 전체 vs 2026 제외 KW |
| `data/processed/reactions/rq4_corr.csv` | 뉴스 비중 ↔ 검색 상관 |
| `data/processed/reactions/pipeline_qc.md` | 한 줄 실행 점검·폴백 판정 |

코퍼스에서 국면 후보 어휘를 다시 뽑으려면 (탐색용):

```powershell
python -m preprocess.mine_keywords --stage df
python -m preprocess.mine_keywords --stage monthly
python -m preprocess.mine_keywords --stage topics    # NMF 주제 축
python -m preprocess.mine_keywords --stage cluster   # 월별 동조성 군집
```

## 알려진 제약

- 빅카인즈 `본문`은 내보내기에서 **200자로 잘립니다**(기사 95%). 토픽 입력은 본문이 아니라
  원문 전체를 형태소 분석한 `키워드` 컬럼을 씁니다.
- 코퍼스 언론사가 **매일경제·서울경제·한국경제 3개 경제지**뿐입니다. 종합지를 추가하지
  않기로 했으므로 결과는 **경제지 기준 이슈 국면**으로 읽습니다. 매체 편향은 한계로 남습니다.
- `mine_keywords --stage topics`의 `topic_monthly_share.csv`는 월별 앞 3,000건 표본이라
  **탐색용입니다**. 국면 시계열은 `data/processed/regimes`의 전량 변환 적합입니다.
- 분석 창 끝(2026-03 중동전쟁, 2026-07 대폭락)에 극단적 사건이 몰려 코스피 월수익률
  변동성이 앞 구간의 네 배가 넘습니다. 반응 분석은 `kospi_ret_std`와 2026년 제외 표본으로
  강건성을 함께 봐야 합니다. 상세는 `data/processed/panel/panel_qc.md`.
