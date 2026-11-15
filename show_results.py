#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
[DataMining 프로젝트] 한국형 경제 이슈 국면 탐지 및 시장·심리 반응 분석
CMD(터미널) 원클릭 연구 결과 종합 출력 스크립트 (show_results.py)
================================================================================
실행 방법:
  python show_results.py
  또는
  run_results.bat 더블클릭 / 실행
"""

import json
import sys
from pathlib import Path

# Windows CMD 한글 및 특수문자 깨짐 방지
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
DATA_JSON = ROOT / "research_web" / "data" / "research_data.json"

REGIME_KR = {
    "macro": "거시·금리·물가(Macro)",
    "realestate": "부동산·주택(RealEstate)",
    "aichip": "AI·반도체(AIChip)",
    "market": "금융시장·증시(Market)",
    "earnings": "기업실적·수출(Earnings)",
    "capital": "자본·지배구조(Capital)",
    "hhdebt": "가계부채·대출(HHDebt)",
    "residual": "기타·일반뉴스(Residual)",
}


def line(char="═", width=96):
    print(char * width)


def subline(char="─", width=96):
    print(char * width)


def section_title(num, title, subtitle=""):
    print()
    line("═")
    print(f"  [{num}] {title}")
    if subtitle:
        print(f"      └─ {subtitle}")
    line("═")


def sig_mark(p):
    if p is None:
        return "-"
    if p < 0.001:
        return "*** (p<0.001)"
    if p < 0.01:
        return "**  (p<0.01)"
    if p < 0.05:
        return "*   (p<0.05)"
    if p < 0.10:
        return "+   (p<0.10)"
    return "ns  (비유의)"


def main():
    if not DATA_JSON.exists():
        print("[알림] 연구 결과 데이터 파일을 먼저 빌드합니다...")
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "research_web" / "build_web_data.py")], check=True)

    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data["meta"]
    panel = data["study_panel_67m"]
    align = data["topic_alignment"]
    terms400 = {t["topic_id"]: t for t in data["topic_terms_400"]}
    hac_reg = data["hac_regression"]
    multiregime = data["multiregime_comparison"]
    cases = data["case_studies_monthly"]
    weekly_comp = data["naver_weekly_comparison"]
    oos_warn = data["strict_oos_early_warning"]

    print()
    line("█", 96)
    print("  📊 뉴스·검색 데이터 기반 한국형 경제 이슈 국면 탐지 및 시장·심리 반응 연구 결과 보고서")
    print("     (목표 학술지: 한국정보통신학회논문지 JKIICE | 최종 기준: Zero-Leakage NMF-400 & A-6.1 검증본)")
    line("█", 96)

    # -------------------------------------------------------------------------
    # 1. 연구 데이터 규모 및 Zero-Leakage 실험 설계
    # -------------------------------------------------------------------------
    section_title(
        "1",
        "연구 데이터 규모 및 Zero-Leakage(미래 정보 누수 차단) 실험 설계",
        "2021~2024년 데이터로만 AI 모델을 학습·고정하고, 2025~2026년 미래 데이터에 외삽 적용하여 검증"
    )
    print(f"  • 전체 분석 기간 : 2021-01 ~ 2026-07 (총 {meta['total_months']}개월 / 주별 {meta['weekly_raw_total']}주, 차분 {meta['weekly_diff_total']}주)")
    print(f"  • 학습 구간(Train): 2021-01 ~ 2024-12 ({meta['train_months']}개월) -> 뉴스 {meta['train_docs']:,}건 (층화표본 {meta['stratified_sample_docs']:,}건으로 NMF 학습)")
    print(f"  • 검증 구간(OOS)  : 2025-01 ~ 2026-07 ({meta['oos_months']}개월) -> 뉴스 {meta['oos_docs']:,}건 (사전·가중치 재학습 없이 고정 투영)")
    print(f"  • 전체 유효 뉴스  : 총 {meta['total_docs_valid']:,}건 (원본 {meta['total_docs_raw']:,}건) | 학습 고정 어휘 사전: {meta['vocab_size_train']:,}개")
    print(f"  • 도출 토픽/국면  : K={meta['nmf_k']}개 NMF 토픽 추출 -> {meta['core_regimes_count']}대 핵심 경제 국면(Regime)으로 매핑")

    # -------------------------------------------------------------------------
    # 2. 14개 토픽 및 6대 경제 국면 분류 + NMF-800 수렴 검증
    # -------------------------------------------------------------------------
    section_title(
        "2",
        "AI(NMF-400)가 추출한 14개 토픽 및 6대 경제 국면 매핑 (NMF-800 완전수렴 비교)",
        "max_iter=400 기준 모델과 max_iter=800(447회 완전수렴) 모델 간 토픽별 코사인 유사도"
    )
    print(f"  {'토픽':<5} | {'배정 국면(NMF-400)':<24} | {'코사인 유사도':<13} | {'대표 핵심 키워드 (Top 6)'}")
    subline()
    for a in align:
        tid = a["topic_a"]
        slug = a["slug_a"] if a["slug_a"] else "residual"
        r_kr = REGIME_KR.get(slug, slug)
        cos = f"{a['cosine_similarity']:.6f}"
        t_info = terms400.get(tid, {})
        top_words = ", ".join(str(t_info.get("top_10_terms", a["top10_a"])).split(", ")[:6])
        print(f"  T{tid:02d}   | {r_kr:<22} | {cos:<13} | {top_words}")
    subline()
    print(f"  ✔ [수렴 오차 검증] NMF-400 재구성 오차({meta['nmf400_err']:.4f}) vs NMF-800({meta['nmf800_err']:.4f}, 447회 수렴) -> 차이 {meta['err_diff_pct']:.4f}%에 불과")
    print(f"  ✔ [토픽 일치 검증] 전체 14개 토픽 평균 코사인 유사도 = {meta['cosine_mean_14']:.6f}")
    print(f"  ✔ [13개 토픽 일치] 가계부채 분화 토픽(T02, 0.7846) 제외 13개 토픽 평균 = {meta['cosine_mean_13']:.6f} (중앙값 {meta['cosine_median_13']:.6f})")

    # -------------------------------------------------------------------------
    # 3. 67개월간 6대 국면 출현 빈도 및 다중 국면(Multi-Regime) 분석
    # -------------------------------------------------------------------------
    section_title(
        "3",
        "67개월간 경제 국면 출현 빈도 및 다중 국면(Multi-Regime) 동시 발생 분석",
        "단일 1위 국면(Argmax)만 선택할 때 누락되는 복합 경제 위기 신호 정량화"
    )
    dom_counts = {}
    active_counts = {k: 0 for k in ["macro", "realestate", "aichip", "market", "earnings", "capital"]}
    for row in panel:
        dom = row["argmax_regime"]
        dom_counts[dom] = dom_counts.get(dom, 0) + 1
        for k in active_counts:
            if row.get(f"active_{k}") == 1:
                active_counts[k] += 1

    print(f"  {'경제 국면명':<24} | {'1위 우세 월수 (67개월 중)':<24} | {'활성 국면(z>=0.5) 출현 월수':<24} | {'1위 비중 그래프'}")
    subline()
    for rk in ["macro", "realestate", "aichip", "market", "earnings", "capital"]:
        r_kr = REGIME_KR[rk]
        c_dom = dom_counts.get(rk, 0)
        pct_dom = c_dom / 67.0 * 100
        c_act = active_counts[rk]
        pct_act = c_act / 67.0 * 100
        bar = "█" * int(round(pct_dom / 2.5))
        print(f"  {r_kr:<22} | {c_dom:>2}개월 ({pct_dom:>5.1f}%)          | {c_act:>2}개월 ({pct_act:>5.1f}%)          | {bar}")
    subline()
    mr_400 = next(m for m in multiregime if m["model_panel"].startswith("NMF-400") and m["split"] == "Full (67m)")
    mr_800_6 = next(m for m in multiregime if "Legacy 6" in m["model_panel"] and m["split"] == "Full (67m)")
    mr_800_7 = next(m for m in multiregime if "7 Regimes" in m["model_panel"] and m["split"] == "Full (67m)")
    print(f"  📌 [다중 국면 핵심 발견]")
    print(f"     • 67개월 중 2개 이상 국면이 동시에 활성(z>=0.5)된 복합 국면 월: {mr_400['months_2plus_active']}/67개월 ({mr_400['pct_2plus_active']:.2f}%)")
    print(f"     • 단일 1위(Argmax)만 선택할 경우 전체 활성 신호({mr_400['total_active_signals']}건) 중 {mr_400['omitted_signals_by_single_argmax']}건({mr_400['omitted_ratio_pct']:.2f}%)이 누락됨")
    print(f"     • NMF-800 Legacy-6에서도 누락률은 {mr_800_6['omitted_ratio_pct']:.2f}%로 일관되며, 7국면 확장 시 {mr_800_7['omitted_ratio_pct']:.2f}%가 누락됨")

    print("\n  [대표적인 다중 국면 동시 발생 5대 사례 월]")
    subline()
    for c in cases:
        ym = c["month"]
        p_tag = "학습" if c["period"] == "train" else "검증OOS"
        arg_kr = f"{c['argmax_regime_kr']}({c['argmax_z']:+.2f}z)"
        omit_kr = c["omitted_active_regimes_kr"]
        kospi_r = f"KOSPI {c['kospi_ret_pct']:+.1f}%"
        rate_bp = f"금리 {c['base_rate_diff_bp']:+.0f}bp"
        print(f"  • [{ym} | {p_tag:<5}] 1위: {arg_kr:<16} | 단일선택 시 누락된 핵심 국면: {omit_kr:<24} | ({kospi_r}, {rate_bp})")

    # -------------------------------------------------------------------------
    # 4. 뉴스 국면 -> 금융시장(KOSPI 변동성 조정 수익률) 다중회귀 검정 (HAC + Holm)
    # -------------------------------------------------------------------------
    section_title(
        "4",
        "[시장 반응 검증] 6대 뉴스 국면이 주식시장(KOSPI 위험조정수익률)에 미치는 영향",
        "Newey-West HAC(lag=3) 강건 표준오차 및 Holm 다중검정 보정 회귀분석 (종속변수: kospi_ret_std)"
    )
    reg_400_full = [r for r in hac_reg if r["model_spec"] == "NMF400_6Regime" and r["sample_split"] == "Full_67m" and r["dep_var"] == "kospi_ret_std" and r["variable"] != "const"]
    reg_800_full = {r["variable"]: r for r in hac_reg if r["model_spec"] == "NMF800_Legacy6" and r["sample_split"] == "Full_67m" and r["dep_var"] == "kospi_ret_std"}

    print(f"  {'독립변수 (뉴스 국면 z-점수)':<26} | {'회귀계수(β)':<12} | {'HAC 표준오차':<12} | {'t-통계량':<10} | {'HAC p값':<10} | {'Holm 보정 p':<12} | {'NMF-800 β'}")
    subline()
    for r in reg_400_full:
        var = r["variable"]
        rk = var.replace("z_", "")
        label = f"{REGIME_KR.get(rk, var)}"
        coef = f"{r['coef']:+.4f}"
        se = f"{r['hac_se']:.4f}"
        t_val = f"{r['t_stat']:+.3f}"
        p_raw = f"{r['p_value_raw']:.4f}"
        p_holm = f"{r['p_value_holm']:.4f} {sig_mark(r['p_value_holm'])}"
        r800_b = f"{reg_800_full[var]['coef']:+.4f}" if var in reg_800_full else "-"
        print(f"  {label:<24} | {coef:<12} | {se:<12} | {t_val:<10} | {p_raw:<10} | {p_holm:<18} | {r800_b}")
    subline()
    meta_reg = reg_400_full[0]
    print(f"  ✔ 모형 적합도: R² = {meta_reg['r_squared']:.4f}, HAC F-통계량 = {meta_reg['hac_f_stat']:.3f} (p = {meta_reg['hac_f_pvalue']:.6f})")
    print("  📌 [핵심 해석] 거시·금리·물가 뉴스 국면(z_macro)이 1표준편차 급증할 때 KOSPI 변동성 조정 수익률은")
    print("     β = -0.7418 (HAC p = 0.0004, Holm 보정 p = 0.0024)로 통계적으로 유의하게 하락함 (NMF-800에서도 β = -0.7399로 완벽히 일치).")

    # -------------------------------------------------------------------------
    # 5. Strict OOS 조기경보(Early Warning) 성능 검증
    # -------------------------------------------------------------------------
    section_title(
        "5",
        "[조기경보 검증] 거시 국면 과열(z_macro >= 0.5) 발생 후 1~2개월 내 증시 급락 탐지력",
        "학습 구간 규칙을 고정한 뒤 1~2개월 선행 KOSPI 급락(ret <= -3%) 포착 성능 비교"
    )
    ew_rows = [w for w in oos_warn if w["category"] == "Early_Warning_Window_Classification" and w["model"] == "NMF-400" and "Crash_1to2m" in w["target_event"]]
    print(f"  {'경보 규칙':<30} | {'평가 구간':<26} | {'경보월수':<8} | {'정밀도(Precision)':<17} | {'기저율 대비 향상':<15} | {'평균 선행개월'}")
    subline()
    for w in ew_rows:
        rule = w["rule_or_spec"].replace(" (Macro-Only)", "").replace(" (Macro+Market)", "")
        sp = "전체 65개월(21.01~26.05)" if "Full" in w["sample_split"] else "Strict OOS 17개월(25.01~26.05)"
        wm = f"{int(w['warning_months'])}개월"
        prec = f"{w['precision']*100:.1f}% (기저율 {w['base_rate']*100:.1f}%)"
        gain = f"{w['gain_over_base_rate']*100:+.1f}%p"
        lead = f"{w['mean_lead_time_months']:.2f}개월" if w["mean_lead_time_months"] else "-"
        print(f"  {rule:<30} | {sp:<24} | {wm:<8} | {prec:<21} | {gain:<15} | {lead}")

    # -------------------------------------------------------------------------
    # 6. 주별(292주) 뉴스 국면 vs 네이버 검색량 동조성 검정 (수준 vs 1차 차분)
    # -------------------------------------------------------------------------
    section_title(
        "6",
        "[대중 관심 동조성] 주별(292주) 언론 뉴스 비중 vs 네이버 검색량 상관 및 1차 차분(Δ) 검정",
        "장기 추세로 인한 가성상관을 통제하기 위해 주별 원자료에 1차 차분을 적용한 엄밀 검정 (HAC lag=4 & 블록 부트스트랩)"
    )
    print("  [A] 전체 기간 (1차 차분 291주, 동시 시차 lag=0) — NMF-400 vs NMF-800 비교")
    subline()
    print(f"  {'비교 쌍 (뉴스 국면 ↔ 네이버 검색어)':<36} | {'표본수':<6} | {'NMF-400 r':<11} | {'HAC p(lag4)':<11} | {'Holm 보정 p':<18} | {'95% 부트스트랩 CI'}")
    subline()
    for w in weekly_comp:
        if w["split"] != "Full" or w["lag_h"] != 0 or w["r_400"] is None:
            continue
        pl = w["pair_label"]
        n_obs = f"{w['sample_n']}주"
        r400 = f"{w['r_400']:+.4f}"
        p_raw = f"{w['hac_p_raw_lag4_400']:.4f}"
        p_holm = f"{w['hac_p_holm_lag4_400']:.4f} {sig_mark(w['hac_p_holm_lag4_400'])}"
        ci = f"[{w['mbb_L4_ci95_low_400']:+.3f}, {w['mbb_L4_ci95_high_400']:+.3f}]"
        print(f"  {pl:<34} | {n_obs:<6} | {r400:<11} | {p_raw:<11} | {p_holm:<18} | {ci}")

    print("\n  [B] 미래 검증 구간 Strict OOS (1차 차분 82주, 동시 시차 lag=0) — 재학습 없는 미래 외삽 검정")
    subline()
    for w in weekly_comp:
        if "OOS" not in w["split"] or w["lag_h"] != 0 or w["r_400"] is None:
            continue
        pl = w["pair_label"]
        n_obs = f"{w['sample_n']}주"
        r400 = f"{w['r_400']:+.4f}"
        p_raw = f"{w['hac_p_raw_lag4_400']:.4f}"
        p_holm = f"{w['hac_p_holm_lag4_400']:.4f} {sig_mark(w['hac_p_holm_lag4_400'])}"
        ci = f"[{w['mbb_L4_ci95_low_400']:+.3f}, {w['mbb_L4_ci95_high_400']:+.3f}]"
        print(f"  {pl:<34} | {n_obs:<6} | {r400:<11} | {p_raw:<11} | {p_holm:<18} | {ci}")
    subline()
    print("  📌 [핵심 해석]")
    print("     1) 주별 1차 차분(Δ, 291주) 후에도 금리 뉴스↔금리 검색(r=+0.5026, Holm p<0.0001), 시황 뉴스↔국내증시 검색(r=+0.4868,")
    print("        Holm p=0.0001), 기업실적 뉴스↔실적 검색(r=+0.2795, Holm p<0.0001)은 주간 단위로 즉각 동조함을 입증함.")
    print("     2) Strict OOS(82주 차분)에서도 기업실적 검색(r=+0.4718, HAC Holm p=0.0011)과 시황↔국내증시 검색(r=+0.4984,")
    print("        HAC lag=4 Holm p=0.0432, 부트스트랩 95% CI [+0.208, +0.637]) 및 금리 검색(r=+0.3397, 부트스트랩 95% CI [+0.132, +0.505])이 양(+)의 동조성을 유지함.")
    print("     3) 반면 부동산(차분 r=+0.1008, Holm p=1.000)과 AI·반도체(차분 r=+0.0609, Holm p=1.000)는 단기 주간 충격보다")
    print("        중장기 추세를 통해 언론 보도와 대중 관심이 공유됨을 명확히 구분함.")

    print()
    line("█", 96)
    print("  ✅ 이상 논문의 모든 핵심 수치·회귀검정·주별 차분 검정·수렴성 결과가 콘솔에 출력되었습니다.")
    print("  💻 언제든 CMD에서 `run_results.bat` 또는 `python show_results.py`를 치시면 이 화면이 즉시 출력됩니다.")
    print("  🌐 인터랙티브 그래프(14종) 화면은 브라우저에서 http://localhost:8090 으로 확인하실 수 있습니다.")
    line("█", 96)
    print()


if __name__ == "__main__":
    main()
