"""Final paper: reporting. See core/description.md."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import pandas as pd
from config.research import DOMAIN_ORDER, DOMAIN_SPEC, EVAL_END, EVAL_START, EXPECTED_COUNTS, H1_DOMAIN, H2_DOMAIN, MASS_TIE_RATIO, MAX_DF_RATIO, MIN_DF, MIN_MAP_SHARE, NMF_INIT, NMF_MAX_ITER, NMF_SOLVER, N_TOPICS, PER_MONTH_SAMPLE, SCRIPT_VERSION, SEED, STUDY_START, TOP_N_VOCAB, TRAIN_END
from core.forecast_analysis import cont_metrics
from config.research import ACTUAL_COL, MODEL_SPECS
from util.research import fnum, fpct, fratio, improvement, is_nan, verdict_word


def _rel_table(m: dict[str, Any], tag: str, base_exp: str, base_fix: str) -> list[str]:
    spec = MODEL_SPECS[tag]
    z, be = m[f"{tag}_zero"], m[f"{tag}_{base_exp}"]
    same = {"news_exp": base_exp, "news_fix": base_fix}
    lines = []
    for key, name in spec:
        c = m[f"{tag}_{key}"]
        def cell(base: dict[str, float] | None, self_ref: bool) -> tuple[str, str]:
            if self_ref:
                return "기준", "기준"
            if base is None or is_nan(c["rmse"]) or is_nan(base["rmse"]):
                return "N/A", "N/A"
            r, a = improvement(base["rmse"], c["rmse"]), improvement(base["mae"], c["mae"])
            return f"{fpct(r)} ({verdict_word(r)})", f"{fpct(a)} ({verdict_word(a)})"
        vz = cell(z, key == "zero")
        ve = cell(be, key == base_exp)
        if key in same:
            vs = cell(m[f"{tag}_{same[key]}"], False)
        elif key in (base_exp, base_fix):
            vs = ("기준", "기준")
        else:
            vs = ("해당 없음", "해당 없음")
        lines.append(f"| {name} <!--id:{tag}_{key}--> | {fnum(c['rmse'])} | {fnum(c['mae'])} | {fnum(c['bias'])} "
                     f"| {vz[0]} | {vz[1]} | {ve[0]} | {ve[1]} | {vs[0]} | {vs[1]} |")
    return lines


def cross_run_rows(root: Path) -> list[str]:
    reac = root / "data" / "processed" / "reactions"
    files = [("Phase 5 (원본)", "phase5_strict_oos_forecast.csv"), ("Phase 5 (v2)", "phase5_strict_oos_forecast_v2.csv"),
             ("Phase 5.2", "phase5_2_strict_oos_forecast.csv")]
    rows = []
    for label, fn in files:
        p = reac / fn
        if not p.exists():
            rows.append(f"| {label} | 파일 없음 | | | | | |")
            continue
        d = pd.read_csv(p)
        vals = []
        for tag, key in (("h1", "news_exp"), ("h1", "news_fix"), ("h2", "news_exp"), ("h2", "news_fix")):
            col = f"{tag}_{key}_pred"
            vals.append(cont_metrics(d[col].to_numpy(), d[ACTUAL_COL[tag]].to_numpy())["rmse"])
        rows.append(f"| {label} | {fnum(vals[0])} | {fnum(vals[1])} | {fnum(vals[2], 5)} | {fnum(vals[3], 5)} |")
    return rows


def render_markdown(ctx: dict[str, Any]) -> str:
    meta, m, df_map, support = ctx["meta"], ctx["metrics"], ctx["df_map"], ctx["support"]
    L: list[str] = []
    A = L.append
    A(f"# Phase 5.6 — 결정론적 Strict OOS 최종 실험 결과")
    A("")
    A(f"- 실행 ID: `{ctx['run_id']}`")
    A(f"- 스크립트: `core/v4.py` (버전 `{SCRIPT_VERSION}`)")
    A(f"- 실행 시각: {ctx['started_kst']} (KST) / {ctx['started_utc']} (UTC)")
    A(f"- 학습 기간(텍스트 파이프라인·표준화·고정창 회귀): {STUDY_START} ~ {TRAIN_END} (48개월)")
    A(f"- 평가 기간: {EVAL_START} ~ {EVAL_END} ({m['n']}개월)")
    A("")
    A("## 1. 데이터 계보와 표본 수")
    c = meta["counts"]
    A("")
    A(f"- 입력: `{ctx['corpus_rel']}` (SHA-256 `{ctx['corpus_sha']}`)")
    A(f"- 입력: `{ctx['panel_rel']}` (SHA-256 `{ctx['panel_sha']}`)")
    A("")
    A("| 단계 | 건수 |")
    A("| :--- | ---: |")
    A(f"| 원본 행 수 | {c['raw_rows']:,} |")
    A(f"| article_id·month·keywords 결측 / 공백 keywords 제거 | {c['null_article_id'] + c['null_month'] + c['null_keywords'] + c['blank_keywords']:,} |")
    A(f"| article_id 중복 제거(정렬 후 첫 행 유지) | {c['duplicate_article_id_removed']:,} |")
    A(f"| 정리 후 분석 기사 | {c['after_cleaning']:,} |")
    A(f"| 학습 기사 (month ≤ {TRAIN_END}) | {c['train_docs']:,} |")
    A(f"| 평가 기사 (month ≥ {EVAL_START}) | {c['eval_docs']:,} |")
    A(f"| NMF·IDF 적합 표본 (월별 최대 {PER_MONTH_SAMPLE:,}건, seed={SEED}) | {meta['n_fit_sample']:,} |")
    A(f"| 어휘에 해당 토큰이 하나도 없는 기사(월별 비중 분모에서 제외) | {meta['n_zero_in_vocab_term_docs']:,} |")
    A("")
    A("처리 규칙: 정리는 결측·공백 제거와 article_id 중복 제거만 수행한다(본문 중복·매체·길이 필터링 없음). "
      "정렬 키는 (month, article_id, keywords), 안정 정렬(mergesort). 월별 표본은 정렬된 위치에서 "
      "`numpy.random.default_rng(seed)`로 비복원 추출하고 위치 오름차순으로 저장한다. "
      "표본 문서 ID 목록은 아티팩트 `fit_sample_ids.csv`에 있다.")
    ec = EXPECTED_COUNTS
    A("")
    A(f"기대 표본 수와의 대조: 원본 {c['raw_rows']:,}/{ec['raw']:,}, 학습 {c['train_docs']:,}/{ec['train']:,}, "
      f"평가 {c['eval_docs']:,}/{ec['eval']:,}, 적합 표본 {meta['n_fit_sample']:,}/{ec['fit_sample']:,}.")
    A("")
    A("## 2. 텍스트 파이프라인 설정과 아티팩트")
    A("")
    A("| 항목 | 값 |")
    A("| :--- | :--- |")
    A(f"| 어휘 | DF ≥ {MIN_DF}, DF/N ≤ {MAX_DF_RATIO}, 상한 {TOP_N_VOCAB:,}, 정렬 (−DF, 토큰) → {meta['vocab_size']:,}개 |")
    A(f"| 어휘 해시 | `{meta['vocab_sha256']}` |")
    A(f"| IDF 해시 | `{meta['idf_sha256']}` |")
    A(f"| 학습 표본 ID 해시 | `{meta['sample_ids_sha256']}` |")
    A(f"| NMF | n_components={N_TOPICS}, init=`{NMF_INIT}`, solver=`{NMF_SOLVER}`, max_iter={NMF_MAX_ITER}, random_state={SEED} |")
    A(f"| NMF 실제 반복 / 경고 없는 종료 | {meta['nmf_n_iter']} / {meta['nmf_converged_no_warning']} |")
    A(f"| H 행렬 해시 | `{meta['H_sha256']}` |")
    A(f"| 매핑 해시 | `{ctx['map_sha']}` |")
    A(f"| 키워드 사전 해시 | `{meta['dictionary_sha256']}` |")
    env = meta["environment"]
    A(f"| 환경 | Python {env['python']}, NumPy {env['numpy']}, SciPy {env['scipy']}, scikit-learn {env['scikit_learn']}, "
      f"statsmodels {env['statsmodels']}, 스레드 환경변수 {env['thread_env']} |")
    A(f"| 아티팩트 디렉터리 | `{ctx['art_rel']}` |")
    A("")
    A("## 3. 토픽-국면 매핑 (토픽 번호 비의존)")
    A("")
    A(f"규칙: 고정 키워드 사전으로 어휘를 도메인에 배정 → 토픽별 도메인 질량 계산 → 최고 도메인 점유율 < {MIN_MAP_SHARE}이면 "
      f"`residual`, 2위/1위 질량비 ≥ {MASS_TIE_RATIO}이면 `ambiguous`, 그 외 `assigned`. 신뢰도 = 1 − (2위/1위).")
    A("")
    A("| 토픽 | 상위 단어(12) | 판정 | 배정 국면 | 1위 도메인 (점유율) | 2위 도메인 | 2위/1위 | 신뢰도 | 우세 그룹 | 사유 |")
    A("| ---: | :--- | :--- | :--- | :--- | :--- | ---: | ---: | :--- | :--- |")
    for _, r in df_map.iterrows():
        tt = ", ".join(str(r["top_terms"]).split(", ")[:12])
        A(f"| {int(r['topic'])} | {tt} | {r['status']} | {r['assigned_label'] or '—'} | "
          f"{r['best_slug']} ({r['best_share']:.4f}) | {r['second_slug']} | {fnum(r['mass_ratio'], 3)} | "
          f"{fnum(r['confidence'], 3)} | {r['dominant_group']} | {r['reason']} |")
    A("")
    A("### 8개 국면 지원 상태")
    A("")
    A("| 국면 | 코드 | 상태 | 연결 토픽 | 비고 |")
    A("| :--- | :--- | :--- | :--- | :--- |")
    for s in DOMAIN_ORDER:
        sp = support[s]
        A(f"| {DOMAIN_SPEC[s]['label']} | `{s}` | {sp['status']} | {sp['topics'] or '—'} | {sp['note']} |")
    A("")
    A("미지원(`unrepresented`) 국면의 월별 비중은 CSV에서 0이 아니라 빈 값(NaN)이다. 그 토픽 질량은 `residual_share`에 포함된다.")
    A("월별 비중 정의: 문서별 토픽 비중 w_k/Σw를 만들고(Σw=0 문서 제외) 월 평균 topic_k(m)을 구한 뒤, "
      "share_d(m)=Σ_{k∈d} topic_k(m), residual_share(m)=Σ_{k 미배정} topic_k(m). 합은 1이다.")
    A("")
    A("### 회귀 특징 연결")
    A("")
    A(f"- H1 뉴스 특징: 국면 `{H1_DOMAIN}` → 토픽 {support[H1_DOMAIN]['topics']} → 열 `share_{H1_DOMAIN}` (시차 1, 2)")
    A(f"- H2 뉴스 특징: 국면 `{H2_DOMAIN}` → 토픽 {support[H2_DOMAIN]['topics']} → 열 `share_{H2_DOMAIN}` (시차 1)")
    A("")
    A("## 4. H1 — 코스피 월간 수익률 예측")
    A("")
    A("개선율 = 100 × (기준 오차 − 모형 오차) / 기준 오차. 양수는 오차 감소, 음수는 오차 증가. "
      "‘동일창 AR 대비’는 확장창 모형은 확장창 AR(2), 고정창 모형은 고정창 AR(2)를 분모로 쓴다.")
    A("")
    A("| 모형 | RMSE | MAE | Bias | Zero 대비 RMSE | Zero 대비 MAE | 확장창 AR(2) 대비 RMSE | 확장창 AR(2) 대비 MAE | 동일창 AR(2) 대비 RMSE | 동일창 AR(2) 대비 MAE |")
    A("| :--- | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- |")
    L.extend(_rel_table(m, "h1", "ar2_exp", "ar2_fix"))
    A("")
    cl = m["class"]
    n_pos = (cl["always_pos"] or cl["always_neg"])["n_pos"]
    n_neg = (cl["always_pos"] or cl["always_neg"])["n_neg"]
    A(f"### H1 방향 분류 (양성=하락월: 실제 < 0, 평가 {m['n']}개월 중 하락월 {n_pos}, 비하락월 {n_neg})")
    A("")
    A("| 모형 | TP | TN | FP | FN | 방향 적중 | 하락 재현율 | 하락 정밀도 | 특이도 | 균형 정확도 |")
    A("| :--- | ---: | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- |")
    for key, name in (("always_pos", "Always Positive"), ("always_neg", "Always Negative"),
                      ("exp_base", "[확장창] AR(2)"), ("exp_news", "[확장창] AR(2)+News"),
                      ("fix_base", "[고정창] AR(2)"), ("fix_news", "[고정창] AR(2)+News")):
        r = cl[key]
        if r is None:
            A(f"| {name} <!--cls:{key}--> | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |")
            continue
        A(f"| {name} <!--cls:{key}--> | {r['tp']} | {r['tn']} | {r['fp']} | {r['fn']} | {fratio(r['hits'], r['n'])} | "
          f"{fratio(r['tp'], r['tp'] + r['fn'])} | {fratio(r['tp'], r['tp'] + r['fp'])} | "
          f"{fratio(r['tn'], r['tn'] + r['fp'])} | {'정의 불가' if is_nan(r['balanced']) else f'{100 * r['balanced']:.1f}%'} |")
    A("")
    A("## 5. H2 — 한국은행 기준금리 변화 예측")
    A("")
    A("| 모형 | RMSE | MAE | Bias | Zero-change 대비 RMSE | Zero-change 대비 MAE | 확장창 AR(1) 대비 RMSE | 확장창 AR(1) 대비 MAE | 동일창 AR(1) 대비 RMSE | 동일창 AR(1) 대비 MAE |")
    A("| :--- | ---: | ---: | ---: | :--- | :--- | :--- | :--- | :--- | :--- |")
    L.extend(_rel_table(m, "h2", "ar1_exp", "ar1_fix"))
    A("")
    A("## 6. 관찰 요약 (표본 내 관찰이며 통계 검정은 수행하지 않음)")
    A("")
    e_r = improvement(m["h1_ar2_exp"]["rmse"], m["h1_news_exp"]["rmse"])
    f_r = improvement(m["h1_ar2_fix"]["rmse"], m["h1_news_fix"]["rmse"])
    A(f"- H1 확장창: 가계대출 뉴스 추가 시 동일창 AR(2) 대비 RMSE {fpct(e_r)} ({verdict_word(e_r)}).")
    A(f"- H1 고정창: 동일창 AR(2) 대비 RMSE {fpct(f_r)} ({verdict_word(f_r)}).")
    he_r = improvement(m["h2_ar1_exp"]["rmse"], m["h2_news_exp"]["rmse"])
    hf_r = improvement(m["h2_ar1_fix"]["rmse"], m["h2_news_fix"]["rmse"])
    A(f"- H2 확장창: 금리·물가 뉴스 추가 시 동일창 AR(1) 대비 RMSE {fpct(he_r)} ({verdict_word(he_r)}).")
    A(f"- H2 고정창: 동일창 AR(1) 대비 RMSE {fpct(hf_r)} ({verdict_word(hf_r)}).")
    zr = {k: improvement(m["h2_zero"]["rmse"], m[f"h2_{k}"]["rmse"]) for k in ("ar1_exp", "news_exp", "ar1_fix", "news_fix")}
    A("- H2 Zero-change 대비 RMSE: " + ", ".join(f"{k} {fpct(v)}" for k, v in zr.items()) + ".")
    ce = cl["exp_news"]
    if ce:
        A(f"- H1 확장창 News 방향 적중 {ce['hits']}/{ce['n']}, 하락 정밀도 {fratio(ce['tp'], ce['tp'] + ce['fp'])}, "
          f"단순 상승 기준선 적중 {cl['always_pos']['hits']}/{ce['n']}.")
    A("")
    A("## 7. 이전 실행과의 비교 (뉴스 모형 RMSE, 각 CSV에서 재계산)")
    A("")
    A("| 실행 | H1 확장창 News | H1 고정창 News | H2 확장창 News | H2 고정창 News |")
    A("| :--- | ---: | ---: | ---: | ---: |")
    L.extend(ctx["cross_rows"])
    A(f"| **Phase 5.6 (본 실행)** | {fnum(m['h1_news_exp']['rmse'])} | {fnum(m['h1_news_fix']['rmse'])} | "
      f"{fnum(m['h2_news_exp']['rmse'], 5)} | {fnum(m['h2_news_fix']['rmse'], 5)} |")
    A("")
    A("## 8. 자동 감사 요약")
    A("")
    A("| 번호 | 항목 | 판정 | 근거 |")
    A("| :--- | :--- | :--- | :--- |")
    for name, ch in ctx["checks"].items():
        A(f"| {name.split('_', 1)[0]} | {name.split('_', 1)[1]} | {ch['status']} | {ch['detail']} |")
    A("")
    A("보고서 지표와 CSV의 일치, 산출물 간 실행 ID 일치, 최종 파일 해시는 이 파일이 작성된 뒤 JSON 감사에서 추가로 확인한다.")
    A("")
    A("## 9. 한계")
    A("")
    A(f"- 평가 표본은 {m['n']}개월이고 하락월은 {n_pos}개월이다. 통계적 유의성 검정은 수행하지 않았으므로 "
      "위 차이를 유의한 개선 또는 일반화 가능한 예측력으로 해석하지 않는다.")
    A("- 키워드 사전 기반 국면 매핑은 사전의 어휘 범위에 의존한다. 사전의 해석 적합성은 상위 단어로 사람이 확인해야 하며 "
      "자동 감사는 규칙 재현성만 검증한다.")
    A("- 같은 코드·입력의 반복 실행 일치는 이 환경(스레드 1개)에서 확인한 것이며 다른 환경에서의 일치는 확인하지 않았다.")
    return "\n".join(L) + "\n"
