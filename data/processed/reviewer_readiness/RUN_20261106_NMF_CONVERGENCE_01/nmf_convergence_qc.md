# NMF 수렴성 독립 검증 QC 보고서 (`RUN_20261106_NMF_CONVERGENCE_01`)

- **검증 일시**: 2026-11-06T18:52:02.953084+09:00
- **보호 대상 파일 해시 점검**: 총 12개 파일 검사, **변경 0건 (PASS)**
- **Phase 2 기준 모델(`NMF-400`) 재현성**:
  - 기존 `nmf_H.npy` 대비 최대 절대 오차: `0.000e+00` (**PASS**)
  - 기존 `H_sha256` (`7EF961B1E32FEE1D7A03ADA4B82AFBD310043531D5DBF130283C640B1A14FECF`) 일치 여부: `True` (**PASS**)
- **실행된 `max_iter` 설정**: `[400, 800, 1200]`
- **14개 토픽 매핑 상태(`status` 및 `assigned_slug`) 전수 일치 여부**:
  - `NMF-400` vs `NMF-800`: `False`
  - `NMF-400` vs `NMF-1200`: `False`