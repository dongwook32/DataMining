# 경제 이슈 국면 탐지 논문 재현

## 실행

Python 3.13 환경에서 `python -m pip install -r requirements.txt`로 의존성을 설치합니다. DataMining 폴더에서 다음 명령을 실행합니다.

```cmd
python run.py reproduce
```

`python script\run_all.py`로도 같은 실행을 시작할 수 있습니다. `--dry-run`은 실행 순서를 표시하고, `--output-dir`는 결과 위치를 지정합니다.

기본 실행은 정상 종료 후 핵심 표와 검산 기록을 `latest/`에 저장합니다. 새 실행이 완료되면 직전 결과를 교체하고, 실패하면 직전 완료 결과를 유지합니다. 모델과 전체 중간 파일을 함께 남길 때는 다음 명령을 사용합니다.

```cmd
python run.py reproduce --keep-full
```

## 폴더 구조

- `data/`는 빅카인즈 원본 XLSX, 저장된 ECOS·데이터랩 CSV, 논문 기준 자료를 담습니다.
- `results/reproduction/latest/tables/`에는 최신 완료 실행에서 계산한 핵심 분석표, 그림에 쓰인 수치, 학습 메타데이터와 `reactions/audit.json`이 저장됩니다.
- `latest/checks/`에는 원본 목록, 국면 사전, 검색어 명세, 검산 로그가 저장됩니다. `latest/status.txt`에서 완료 상태를 확인할 수 있습니다.
- `--keep-full`을 지정하면 최신 완료 실행의 `latest/work/data/processed/`에 모델, 코퍼스, 패널, 전체 검증 파일도 보관합니다.
- `results/submission/`은 제출 PDF와 기존 결과표를, `results/docs/`는 분석 안내와 과거 검증 기록을 보관합니다.
- [실행 순서와 스크립트별 역할](script/description.md)

전체 실행은 저장된 원자료에서 코퍼스와 월별 패널을 다시 만들고, TF-IDF·NMF를 새로 학습합니다. 이어 국면 분석, 시장 반응·조기경보, 뉴스·검색 검증, 토픽 품질·안정성 및 수렴 비교를 계산합니다. 이전 8국면과의 비교에 한해 별도 보관된 8국면 패널을 입력으로 사용합니다. 수집 API 키 없이 실행할 수 있습니다.

이전 프로젝트와 제출본은 `.backups/legacy-root-20261117/`에 보관했습니다. 저장된 결과는 `python run.py terminal`로 조회할 수 있습니다.
