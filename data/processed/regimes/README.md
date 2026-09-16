# 월별 국면 시계열

`analysis.detect_regimes`가 `doc_term.npz`로 토픽을 추정하고, 월별 국면
라벨과 전환 시점을 만든 곳입니다. IDF는 전량, NMF 적합은 월별 무작위 층화표본,
시계열은 전량 변환입니다. 월 라벨은 국면 비중의 z점수 argmax입니다. Step 4는
`regime_monthly.csv`를 `month` 키로 붙입니다.

탐색용 `data/processed/corpus/topic_monthly_share.csv`(월별 앞 3,000건 표본)는
쓰지 않습니다.

| 파일 | 내용 |
|------|------|
| `topic_monthly_share.csv` | 월 × 14토픽 비중 (행합 = 1) |
| `topic_terms.csv` | 토픽별 상위 어휘 |
| `topic_regime_map.csv` | 토픽 → 국면 7개 매핑 |
| `regime_monthly.csv` | 월별 우세 국면 + 7국면 비중 |
| `changepoints.csv` | PELT 전환 시점 |
| `nmf_H.npy` | 토픽×어휘 성분. `--remap-only` 입력 |
| `regimes_qc.md` | 매 실행마다 갱신되는 점검 리포트 |

컬럼 설명은 각 CSV 옆의 `*.columns.md`에 있습니다.

## 재생성

```powershell
python -m analysis.detect_regimes
python -m analysis.detect_regimes --remap-only   # 매핑·변화점만 다시
```

같은 행렬·같은 sklearn 버전이면 같은 결과가 나옵니다. 매핑 규칙을 손보고 토픽을
다시 적합하지 않을 때는 `--remap-only`를 씁니다.
