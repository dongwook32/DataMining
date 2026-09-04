# DataMining — 한국형 경제 이슈 국면 탐지

뉴스·검색 데이터로 경제 이슈 국면(물가·금리·부동산·대외 등)을 탐지하고,
국면별 코스피·환율·CCSI 반응 패턴을 분석하는 연구 저장소입니다.

자세한 설계: [`docs/research_plan.md`](docs/research_plan.md)  
파일럿 판정: [`docs/feasibility_report.md`](docs/feasibility_report.md) (Conditional Go)

## 현재 단계

**전처리 완료** — 코퍼스 931,709건이 문서×어휘 행렬(931,709 × 28,343)로, 지표·검색·뉴스량이
월 패널(127개월 × 54열)로 정리됐습니다. Step 3의 입력이 모두 준비된 상태입니다.

| 단계 | 상태 |
|------|------|
| 1. 설계·파일럿 | 완료 (산출물 정리 완료, 본데이터로 전환) |
| 2. 본데이터 (빅카인즈·ECOS·데이터랩) | 완료 |
| 2.5 전처리 (문서-어휘 행렬 · 월 패널) | 완료 |
| 3. 국면 탐지 모델 | 진행 예정 |
| 4. 반응 분석 | 대기 |
| 5. 강건성·논문화 | 대기 |

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
    regimes/       # 월별 국면 시계열
    reactions/     # 국면별 반응표
docs/
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

| 산출 | 형태 | 쓰는 곳 |
|------|------|---------|
| `data/processed/corpus/doc_term.npz` | 931,709 × 28,343 희소행렬 | Step 3 토픽모델 |
| `data/processed/panel/monthly_panel.csv` | 127개월 × 54열 | Step 4 반응 분석 |
| `data/processed/panel/panel_qc.md` | 품질 점검 리포트 | 매 실행마다 갱신 |

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
- 코퍼스 언론사가 **매일경제·서울경제·한국경제 3개 경제지**뿐입니다. 매체 편향 통제가
  불가능하므로 논문 한계에 명시하거나 종합지를 추가 투입해야 합니다.
- `mine_keywords --stage topics`의 `topic_monthly_share.csv`는 월별 앞 3,000건 표본이라
  **탐색용입니다**. 국면 시계열은 표본 없는 `doc_term.npz`로 다시 추정해야 합니다.
- 분석 창 끝(2026-03 중동전쟁, 2026-07 대폭락)에 극단적 사건이 몰려 코스피 월수익률
  변동성이 앞 구간의 네 배가 넘습니다. 반응 분석은 `kospi_ret_std`와 2026년 제외 표본으로
  강건성을 함께 봐야 합니다. 상세는 `data/processed/panel/panel_qc.md`.
