# DataMining — 한국형 경제 이슈 국면 탐지

뉴스·검색 데이터로 경제 이슈 국면(물가·금리·부동산·대외 등)을 탐지하고,
국면별 코스피·환율·CCSI 반응 패턴을 분석하는 연구 저장소입니다.

자세한 설계: [`docs/research_plan.md`](docs/research_plan.md)  
파일럿 판정: [`docs/feasibility_report.md`](docs/feasibility_report.md) (Conditional Go)

## 현재 단계

**Step 2 완료** — 뉴스 코퍼스 931,709건 구축, 지표·검색 데이터 정합. 다음은 국면 탐지 모델.

| 단계 | 상태 |
|------|------|
| 1. 설계·파일럿 | 완료 (산출물 정리 완료, 본데이터로 전환) |
| 2. 본데이터 (빅카인즈·ECOS·데이터랩) | 완료 |
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
    corpus/        # 통합 뉴스 코퍼스 + 키워드 마이닝 산출
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

코퍼스에서 국면 후보 어휘를 다시 뽑으려면:

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
