# DataMining — 한국형 경제 이슈 국면 탐지

뉴스·검색 데이터로 경제 이슈 국면(물가·금리·부동산·대외 등)을 탐지하고,
국면별 코스피·환율·CCSI 반응 패턴을 분석하는 연구 저장소입니다.

**이전 8국면 분석 보고서:** [`docs/이전_8국면_실증분석_보고서.md`](docs/이전_8국면_실증분석_보고서.md)
**이전 분석의 쉬운 설명:** [`docs/연구_쉬운_요약.md`](docs/연구_쉬운_요약.md)
**재실행·코드·용어:** [`docs/분석_재현_기술_안내.md`](docs/분석_재현_기술_안내.md) · **문서 목록:** [`docs/README.md`](docs/README.md)
수치 색인: [`docs/이전_8국면_결과_수치_색인.md`](docs/이전_8국면_결과_수치_색인.md) · 진행 일지: [`docs/연구_결정_일지.md`](docs/연구_결정_일지.md)

**최신 연구 결과:** [경제이슈국면탐지 v4 (PDF)](output/paper_20261116/경제이슈국면탐지_v4_JKIICE2026_양식적용.pdf)

## 바로 실행

프로젝트 폴더의 PowerShell 또는 CMD에서:

```powershell
python run.py
```

저장된 연구 결과 대시보드를 브라우저로 엽니다. 종료는 터미널에서 `Ctrl+C`.
기본 포트는 8090이며, 사용 중이면 `python run.py web --port 8091`로 실행합니다.
기본 실행과 터미널 출력에는 Python 표준 라이브러리만 필요합니다.
차트(Plotly)와 웹 폰트는 기존 CDN을 사용하므로 인터넷 연결이 필요합니다.

| 명령 | 동작 |
|---|---|
| `python run.py` | 저장된 결과 웹 화면 열기 |
| `python run.py terminal` | 저장된 연구 결과를 터미널에 출력 |
| `python run.py summary` | 기존 8국면 요약 분석 재계산 → `output/summary/` |
| `python run.py pipeline` | 기존 로컬 데이터로 반응·강건성·RQ4 파이프라인 실행 |
| `python run.py rebuild-web` | 웹 데이터 재생성 (로컬 원자료 및 `origin/main`의 연구 산출물 필요) |
| `python run.py web --no-browser` | 브라우저 자동 실행 없이 서버만 시작 |

`summary`와 `pipeline`은 분석용 의존성이 필요하며 기존 `.venv`가 있으면 자동 사용합니다.
`summary`는 과거 8국면 분석이고 웹 화면의 최종 모형과 구분됩니다.
기본 실행은 저장된 결과 조회이며 새 분석을 수행하지 않습니다.
`run_results.bat` 더블클릭도 기본 웹 실행과 같습니다.

## 정리된 파일과 복원

- `datamining/`: 공통 경로, 명령 처리, 콘솔 표시, 요약 분석
- `analysis/`, `api/`, `preprocess/`, `config/`: 기존 연구 모듈
- `research_web/`: 대시보드 화면·데이터·서버
- `docs/검증/`: 검증 보고서와 감사 CSV
- `docs/templates/`: 학회 제출 양식 원본
- `docs/연구_결정_일지.md`, `docs/history/`: 연구·작업 기록
- `output/summary/`: 재생성 가능한 요약 CSV·차트
- `output/paper_20261116/`: 기존 논문 결과물 보존
- `tests/`: 실행 회귀 테스트 (`python -m unittest discover -s tests -v`)

정리 직전 파일은 로컬 `.backups/cleanup-20261116/before.zip`에 보관했습니다.
이 백업은 Git에 포함되지 않으므로 되돌리기가 필요하면 보관하세요.

```powershell
python .backups/cleanup-20261116/restore.py --check
python .backups/cleanup-20261116/restore.py
```

첫 명령은 복원 가능 여부만 점검하고, 두 번째는 이번 정리로 바뀐 파일만 복원합니다.
정리 이후 추가 수정된 파일이 있으면 충돌 목록을 출력하고 복원을 중단합니다.
`.git`, `.venv`, 연구 데이터는 이번 작업의 변경·복원 대상이 아닙니다.

후속 문서 이름 정리는 먼저 `python .backups/docs-20261116/restore.py`로 되돌릴 수 있습니다.

## 현재 단계

**전체 실증 분석 완료** — NMF 14토픽 결합 8대 국면 체계 및 다중 활성화(`z >= 0.5`) 기반 반응·회귀 분석(HAC OLS, $R^2=22.8\%$, $F=4.75$, $p=0.00016$)과 1~2개월 시차 선행성(소비심리, 기준금리, 코스피) 실증 완료.

| 단계 | 상태 |
|------|------|
| 1. 설계·파일럿 | 완료 |
| 2. 본데이터 (빅카인즈·ECOS·데이터랩) | 완료 |
| 2.5 전처리 (문서-어휘 행렬 · 월 패널) | 완료 |
| 3. 국면 탐지 모델 (NMF 8대 국면 다중 활성화) | 완료 |
| 4. 반응 및 시차 선행성 분석 (HAC OLS & 교차상관) | 완료 |
| 5. 강건성 검정 (z 임계값 민감도 & 2026 제외 표본) | 완료 |

**분석 기간: 2021-01 ~ 2026-07** (빅카인즈 코퍼스 보유 기간, 67개월).  
ECOS·데이터랩은 차분·시차용 lead-in을 위해 2016-01부터 받아 둡니다.

**공식 8대 국면:** 금리·물가 · 부동산 · 가계대출 · 대외통상 · AI반도체 · 시황 · 기업실적 · 자본거래.  
8대 국면 다중 활성화(`z >= 0.5`) 기반 반응·회귀 분석 및 시차 선행성 실증이 완료되었습니다.

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
  변동성이 앞 구간의 네 배가 넘습니다. 반응 분석은 `kospi_ret_std`(과거 12개월 변동성 기준 표준화 월간 수익률)와 2026년 제외 표본으로
  강건성을 함께 봐야 합니다. 상세는 `data/processed/panel/panel_qc.md`.
