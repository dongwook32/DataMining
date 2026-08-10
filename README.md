# DataMining — 한국형 경제 이슈 국면 탐지

뉴스·검색 데이터로 경제 이슈 국면(물가·금리·부동산·대외 등)을 탐지하고,
국면별 코스피·환율·CCSI 반응 패턴을 분석하는 연구 저장소입니다.

자세한 설계: [`docs/research_plan.md`](docs/research_plan.md)  
파일럿 판정: [`docs/feasibility_report.md`](docs/feasibility_report.md) (Conditional Go)

## 현재 단계

**Step 2 직전 (본데이터 구축)** — Step 1 파일럿·골격 검증 완료. 산출물은 `_archive_pilot`에 보관.

| 단계 | 상태 |
|------|------|
| 1. 설계·파일럿 | 완료 |
| 2. 본데이터 (빅카인즈·ECOS·데이터랩) | 대기 |
| 3. 국면 탐지 모델 | 대기 |
| 4. 반응 분석 | 대기 |
| 5. 강건성·논문화 | 대기 |

## 폴더 구조

```text
analysis/          # 본분석 스크립트
  pilot/           # Step 1 파일럿 (재실행용, 본연구 데이터와 분리)
api/               # ECOS·외부 API 클라이언트
crawler/           # 수집 유틸 (빅카인즈는 수동 다운로드)
config/            # config.yaml
data/
  raw/
    bigkinds/      # 본연구 뉴스 (수동 투입)
    ecos/          # ECOS 지표
    datalab/       # 네이버 데이터랩 (선택)
    _archive_pilot/
  processed/
    regimes/       # 월별 국면 시계열
    reactions/     # 국면별 반응표
    _archive_pilot/
docs/
```

## 환경 설정

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # 키 입력
```

## 데이터 투입 (본연구)

1. 빅카인즈 CSV → `data/raw/bigkinds/` (스펙은 해당 폴더 README)
2. ECOS 월별 지표 → `data/raw/ecos/`
3. (권장) 데이터랩 트렌드 → `data/raw/datalab/`

합성·RSS 파일럿 데이터는 논문 분석에 쓰지 마세요.

## 파일럿 재실행 (선택)

```powershell
python -m analysis.pilot.run_feasibility_regime
python -m analysis.pilot.run_datamining_test
```
