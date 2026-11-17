"""Write the intermediate workbooks and the six-section result of a fresh run."""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import pandas as pd

from core.excel_export import json_rows, read_json, write_workbook
from core.forecast_analysis import compute_all_metrics
from core.reproduce import MODEL_ROOT, PAPER_SUPPORT, REACTIONS
from util.paths import ROOT

CONVERGENCE = "RUN_20261106_NMF_CONVERGENCE_01"
DOWNSTREAM = "RUN_20261106_NMF_DOWNSTREAM_SENSITIVITY_01"
REVIEW = "RUN_20261106_161800"
REGIMES = dict(macro="금리·물가", realestate="부동산", aichip="첨단산업",
               market="시황", earnings="기업실적", capital="자본거래")


def section(name, description, table, headers=None):
    values = table.astype(object).where(table.notna(), None)
    return name, headers or list(values.columns), values.itertuples(index=False, name=None), description


def final_sections(meta, counts, processed):
    reviewer = processed / "reviewer_readiness"

    def csv(directory, name):
        return pd.read_csv(directory / (name + ".csv"), encoding="utf-8-sig")

    topics = csv(reviewer / CONVERGENCE, "topic_alignment")
    topics = topics.loc[topics.pair.eq("NMF-400_vs_NMF-800"), ["topic_a", "slug_a", "cosine_similarity", "top10_a"]].copy()
    terms = csv(reviewer / CONVERGENCE, "topic_terms_400").set_index("topic_id")
    topics["top10_a"] = topics.topic_a.map(terms.top_10_terms).fillna(topics.top10_a).map(
        lambda words: ", ".join(words.split(", ")[:6])
    )
    topics["slug_a"] = topics.slug_a.map(REGIMES).fillna("기타·일반뉴스")
    convergence = csv(reviewer / CONVERGENCE, "convergence_metrics")
    convergence = convergence.loc[convergence.max_iter.isin([400, 800]),
                                  ["max_iter", "n_iter_actual", "reconstruction_err", "err_improvement_vs_400_pct"]]

    monthly = csv(processed / "supplemental_validation", "single_vs_multi_monthly")
    weekly = csv(processed / "supplemental_validation", "news_search_weekly_panel")
    occurrence = pd.DataFrame([
        (label, (monthly.argmax_regime == slug).sum(), monthly[f"active_{slug}"].sum())
        for slug, label in REGIMES.items()
    ])
    occurrence[3] = occurrence[1] / len(monthly) * 100
    occurrence[4] = occurrence[2] / len(monthly) * 100
    multi = csv(reviewer / DOWNSTREAM, "multiregime_comparison")
    multi = multi.loc[multi.split.eq("Full (67m)"), [
        "model_panel", "n_months", "months_2plus_active", "pct_2plus_active",
        "total_active_signals", "omitted_signals_by_single_argmax", "omitted_ratio_pct",
    ]]
    cases = csv(reviewer / REVIEW, "multi_regime_case_monthly")[[
        "month", "period", "argmax_regime_kr", "argmax_z", "omitted_active_regimes_kr",
        "kospi_ret_pct", "base_rate_diff_bp",
    ]]
    regression = csv(reviewer / DOWNSTREAM, "hac_regression_comparison")
    regression = regression.loc[regression.sample_split.eq("Full_67m")
                                & regression.dep_var.eq("kospi_ret_std") & regression.variable.ne("const")]
    regression_800 = regression.loc[regression.model_spec.eq("NMF800_Legacy6_CombinedRE"),
                                    ["variable", "coef"]].rename(columns={"coef": "coef_800"})
    regression = regression.loc[regression.model_spec.eq("NMF400_6Regime"), [
        "variable", "coef", "hac_se", "t_stat", "p_value_raw", "p_value_holm", "r_squared",
        "hac_f_stat", "hac_f_pvalue",
    ]].merge(regression_800, on="variable", validate="one_to_one")
    regression["variable"] = regression.variable.str.removeprefix("z_").map(REGIMES)
    warning = csv(reviewer / DOWNSTREAM, "strict_oos_comparison")
    warning = warning.loc[
        warning.category.eq("Early_Warning_Window_Classification") & warning.model.eq("NMF-400")
        & warning.target_event.str.contains("Crash_1to2m", na=False),
        ["rule_or_spec", "sample_split", "evaluable_months", "warning_months", "tp", "fp", "fn",
         "tn", "precision", "base_rate", "gain_over_base_rate", "mean_lead_time_months"],
    ]
    search = csv(reviewer / DOWNSTREAM, "naver_weekly_comparison")
    search = search.loc[
        (search.split.eq("Full") | search.split.str.contains("OOS", na=False))
        & search.lag_h.eq(0) & search.r_400.notna(),
        ["split", "pair_label", "sample_n", "r_400", "hac_p_raw_lag4_400", "hac_p_holm_lag4_400",
         "mbb_L4_ci95_low_400", "mbb_L4_ci95_high_400"],
    ]
    train = monthly.loc[monthly.period.eq("train"), "month"]
    test = monthly.loc[monthly.period.eq("eval"), "month"]
    design = pd.DataFrame([
        ("원본 XLSX 파일 수", len(counts)),
        ("원본 XLSX 기사 행 수", counts.rows.sum()),
        ("전처리 후 전체 기사 수", meta["counts"]["after_cleaning"]),
        ("학습 기사 수", meta["counts"]["train_docs"]),
        ("검증 기사 수", meta["counts"]["eval_docs"]),
        ("모델 학습 표본 수", meta["n_fit_sample"]),
        ("학습 어휘 수", meta["vocab_size"]),
        ("월별 분석 기간 (개월)", len(monthly)),
        ("학습 기간", f"{train.min()} ~ {train.max()} ({len(train)}개월)"),
        ("검증 기간", f"{test.min()} ~ {test.max()} ({len(test)}개월)"),
        ("주별 관측값 수", len(weekly)),
        ("전주 대비 변화를 계산한 주 수", int(search.loc[search.split.eq("Full"), "sample_n"].max())),
        ("추출한 토픽 수", len(topics)),
        ("배정된 경제 이슈 국면 수", len(REGIMES)),
    ])
    tables = [
        section("01 연구 데이터와 실험 설계", "빅카인즈 원본 검산과 이번 실행의 학습 기록에서 집계", design,
                ["항목", "값"]),
        section("02 토픽과 국면 매핑", "NMF-400과 800 재학습 결과를 토픽별로 비교", topics,
                ["토픽 번호", "배정 국면", "코사인 유사도", "대표 단어 6개"]),
        section("03 국면 출현과 다중 활성", "월별 국면을 기준으로 대표 및 활성 월 수를 집계", occurrence,
                ["국면", "1위 월 수", "활성 월 수", "1위 비율 (%)", "활성 비율 (%)"]),
        section("04 코스피 회귀", "같은 달에 관측된 뉴스 국면과 변동성 조정 수익률의 관계", regression,
                ["국면", "NMF-400 회귀계수", "HAC 표준오차", "t 통계량", "보정 전 p값", "Holm 보정 p값",
                 "결정계수", "HAC F 통계량", "모형 p값", "NMF-800 회귀계수"]),
        section("05 코스피 급락 조기경보", "경보 이후 1~2개월 내 월 수익률 -3% 이하 발생을 평가", warning,
                ["경보 규칙", "평가 구간", "평가 월 수", "경보 월 수", "적중", "오경보", "놓친 급락",
                 "급락 없음", "적중률 (0~1)", "기저율 (0~1)", "기저율 대비 차이 (비율)", "평균 선행 개월"]),
        section("06 주별 뉴스와 검색", "전주 대비 뉴스 비중과 검색지수 변화의 같은 주 상관", search,
                ["평가 구간", "뉴스·검색 조합", "관측 주 수", "상관계수", "HAC p값", "Holm 보정 p값",
                 "95% 신뢰구간 하한", "95% 신뢰구간 상한"]),
        section("02 반복 상한과 수렴", "반복 상한, 실제 반복 횟수와 학습 재구성 오차", convergence,
                ["반복 상한", "실제 반복 횟수", "재구성 오차", "NMF-400 대비 개선율 (%)"]),
        section("03 활성 신호와 누락률", "모델별로 한 달에 이슈를 하나만 고를 때 누락되는 신호", multi,
                ["모델", "월 수", "두 국면 이상 활성 월 수", "두 국면 이상 활성 비율 (%)", "전체 활성 신호",
                 "누락 신호", "누락률 (%)"]),
        section("03 대표 사례 월", "다중 국면이 동시에 나타난 월의 사례", cases,
                ["연월", "분석 구간", "대표 국면", "대표 국면 z점수", "누락된 활성 국면",
                 "코스피 월 수익률 (%)", "기준금리 변동 (bp)"]),
    ]
    print(f"1. 유효 기사 {meta['counts']['after_cleaning']:,}건, 학습 표본 {meta['n_fit_sample']:,}건")
    print(f"2. 토픽 {len(topics)}개, NMF-400·800 평균 유사도 {topics.cosine_similarity.mean():.6f}")
    print(f"3. 월별 국면 {len(monthly)}개월, 다중 활성 사례 {len(cases)}개월")
    print(f"4. 코스피 HAC 회귀 {len(regression)}개 국면, 결정계수 {regression.r_squared.iloc[0]:.4f}")
    print(f"5. 급락 조기경보 {len(warning)}개 구간·규칙 비교")
    print(f"6. 주별 뉴스·검색 {len(search)}개 구간·조합 비교")
    return tables


def export(run):
    run = run.resolve()
    if ROOT != run / "work":
        raise ValueError("이번 실행의 작업 폴더에서만 결과를 내보낼 수 있습니다.")
    processed = ROOT / "data/processed"
    audit = ROOT / REACTIONS / "phase5_6_pipeline_audit.json"
    run_id = read_json(audit)["run_id"]
    model = ROOT / MODEL_ROOT / run_id
    meta = read_json(model / "core_meta.json")
    if meta["run_id"] != run_id:
        raise ValueError("학습과 분석의 실행 ID가 일치하지 않습니다.")
    collection = ROOT / PAPER_SUPPORT / "S1_bigkinds_manifest.csv"
    preprocessing = [
        (collection, "원본 XLSX별 수집 범위와 기사 행 수"),
        (processed / "corpus/corpus_monthly_counts.csv", "전처리 후 월별 기사 수"),
        (processed / "panel/monthly_panel.csv", "경제지표와 검색지수를 합친 월별 입력"),
        (processed / "panel/monthly_panel_search_sub.csv", "검색 하위 그룹의 월별 지수"),
        (model / "core_meta.json", "학습 설정, 기사 및 어휘 집계"),
        (model / "fit_sample_ids.csv", "모델에 들어간 기사 식별자와 순서"),
        (model / "vocab_idf.csv", "어휘, 학습 문서 빈도, IDF 가중치"),
        (model / "nmf_H.npy", "토픽·어휘별 학습 가중치"),
        (model / "monthly_topic_share.csv", "월별 토픽 비중"),
    ]
    followup = [(audit, "입력·산출물 해시와 학습·예측 검산")]
    for folder, text in (
        (ROOT / REACTIONS, "월별 국면, 예측 및 시장 반응"),
        (processed / "supplemental_validation", "다중 활성, 주별 뉴스·검색"),
        (processed / "reviewer_readiness", "품질·안정성·강건성·수렴 비교"),
    ):
        followup.extend((source, text) for source in sorted(folder.rglob("*.csv")))
    reviewer = processed / "reviewer_readiness"
    followup.extend((source, "비교 모델의 어휘별 학습 가중치")
                    for source in sorted((reviewer / CONVERGENCE).glob("nmf_H_*.npy")))
    followup.extend((source, "재학습 또는 후속 분석에 사용된 실행 환경")
                    for source in sorted(reviewer.rglob("environment_spec.json")))
    followup.append((ROOT / PAPER_SUPPORT / "S5_domain_dictionary.csv", "이슈 배정에 사용한 사전"))
    predictions = pd.read_csv(ROOT / REACTIONS / "phase5_6_strict_oos_forecast.csv")
    evaluation = [("표본 외 예측 평가", ["항목", "값"], json_rows(compute_all_metrics(predictions)),
                   "이번 실행의 코스피·기준금리 예측 평가")]
    final = final_sections(meta, pd.read_csv(collection), processed)
    with TemporaryDirectory(prefix=".excel-", dir=run) as tmp:
        stage = Path(tmp)
        write_workbook(stage / "01_전처리_학습.xlsx", run_id, preprocessing)
        write_workbook(stage / "02_중간_분석_검증.xlsx", run_id, followup, evaluation)
        write_workbook(stage / "03_최종_결과.xlsx", run_id, [], final)
        for workbook in sorted(stage.glob("*.xlsx")):
            workbook.replace(run / workbook.name)


if __name__ == "__main__":
    export(Path(sys.argv[1]))
