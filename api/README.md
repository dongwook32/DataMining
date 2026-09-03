# API 클라이언트

## 한국은행 ECOS
- `api/ecos_client.py` — StatisticSearch / StatisticItemList / StatisticTableList
- `api/ecos_indicators.py` — 수집 지표 정의 (통계표·항목 코드)
- `python -m api.collect_ecos` — 월별 지표 수집
- `python -m api.collect_ecos --list-items 511Y002` — 항목코드 조회

### 키 (.env)
| 변수 | 용도 |
|------|------|
| `ECOS_API_KEY` | ECOS Open API |

### 산출
- `data/raw/ecos/ecos_monthly.csv` (월당 1행, 지표별 컬럼)
- 지표: CCSI, KOSPI, USD_KRW, BASE_RATE, CPI

## 네이버
- `api/naver_client.py` — Search Trend(데이터랩). 뉴스 검색은 본연구에서 쓰지 않음
- `api/datalab_keyword_sets.py` — 국면 대분류 7 × 세부 4 검색어 세트 + 앵커
- `python -m api.collect_datalab` — 검색어 트렌드 수집 (월간·일간)
- `python -m api.collect_datalab --calibrate` — 앵커 후보 비교

### 키 (.env)
| 변수 | 용도 |
|------|------|
| `NAVER_HUB_CLIENT_ID` / `NAVER_HUB_CLIENT_SECRET` | NCP NAVER API HUB (검색어 트렌드) |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | HUB 키가 없을 때 대용 |

검색어 트렌드는 개발자센터 신규 신청이 막혀 있어 **API HUB** 키를 사용합니다.

### 산출
- `data/raw/datalab/datalab_{regime,sub}_{monthly,daily}.csv`
- 요청 1건 = 대상 그룹 1개 + 앵커 그룹(`은행`) 1개.
  분석에는 원값 `score`가 아니라 `score_rel = score / anchor_score`를 쓴다.
  이유는 `data/raw/datalab/README.md` 참고.
- 조회 구간은 `config.yaml`에서 읽어 고정한다 (수집일에 따라 값이 바뀌면 안 되므로).
