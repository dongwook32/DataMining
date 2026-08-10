# ECOS 경제지표

한국은행 ECOS에서 받은 월별 시계열을 둡니다.
API 수집 시에도 최종 산출물은 이 폴더의 CSV로 저장하세요.

## 권장 파일
- `ecos_monthly.csv`

## 스키마
| 컬럼 | 설명 |
|------|------|
| date | YYYY-MM-DD (월초 또는 월말 통일) |
| indicator | CCSI / KOSPI / USD_KRW / BASE_RATE 등 |
| value | 수치 |

`.env`의 `ECOS_API_KEY` 설정 후 API 모듈로 받을 수 있습니다.
