"""연구 A: 단일 국면 vs 다중 국면 활성화 비교 실험 스크립트.

기존 Phase 5.6 train-only 표준화 모수와 6개 유효 국면을 바탕으로:
1. 단일 대표 국면 (Unconstrained Argmax vs Hurdle Argmax z>=0.5)
2. 다중 국면 활성화 (z >= 0.5)
를 학습 기간(2021-01~2024-12, 48m)과 테스트 기간(2025-01~2026-07, 19m)에서 비교 분석한다.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_CSV = ROOT / "data" / "processed" / "reactions" / "phase5_6_train_only_regime_monthly.csv"
OUT_DIR = ROOT / "data" / "processed" / "supplemental_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REGIMES = ["macro", "realestate", "aichip", "market", "earnings", "capital"]
REGIME_KR = {
    "macro": "금리·물가",
    "realestate": "부동산",
    "aichip": "AI·반도체",
    "market": "시황",
    "earnings": "기업실적",
    "capital": "자본거래"
}

def run_experiment():
    df = pd.read_csv(INPUT_CSV).sort_values("month").reset_index(drop=True)
    z_cols = [f"z_{r}" for r in REGIMES]
    
    # 1. 월별 활성화 테이블 생성
    records = []
    for idx, row in df.iterrows():
        m = row["month"]
        period = row["period"]
        z_vals = {r: float(row[f"z_{r}"]) for r in REGIMES}
        
        # 방식 A-1: Unconstrained Argmax (무조건 최대값 1개)
        max_r = max(z_vals.keys(), key=lambda k: z_vals[k])
        max_z = z_vals[max_r]
        
        # 방식 A-2: Hurdle Argmax (최대값이 z>=0.5 이상일 때만 활성화, 아니면 None)
        hurdle_r = max_r if max_z >= 0.5 else "none"
        
        # 방식 B: Multi-activation (z >= 0.5 인 모든 국면)
        multi_active = [r for r in REGIMES if z_vals[r] >= 0.5]
        n_multi = len(multi_active)
        
        # 단일 방식에서 제외되는 추가 활성 국면들
        omitted_active = [r for r in multi_active if r != max_r]
        
        records.append({
            "month": m,
            "period": period,
            "argmax_regime": max_r,
            "argmax_z": max_z,
            "hurdle_regime": hurdle_r,
            "multi_regimes": ";".join(multi_active) if multi_active else "none",
            "n_multi_active": n_multi,
            "omitted_active_regimes": ";".join(omitted_active) if omitted_active else "none",
            "n_omitted_active": len(omitted_active),
            **{f"z_{r}": z_vals[r] for r in REGIMES},
            **{f"active_{r}": (1 if z_vals[r] >= 0.5 else 0) for r in REGIMES}
        })
        
    res_df = pd.DataFrame(records)
    res_df.to_csv(OUT_DIR / "single_vs_multi_monthly.csv", index=False, encoding="utf-8-sig")
    
    # 2. 집계 메트릭 계산 (전체, 학습 48m, 테스트 19m)
    metrics = []
    for split_name, split_df in [
        ("Full (67m)", res_df),
        ("Train (48m)", res_df[res_df["period"] == "train"]),
        ("Eval OOS (19m)", res_df[res_df["period"] == "eval"])
    ]:
        n_m = len(split_df)
        # 활성 국면 수 분포
        counts = split_df["n_multi_active"].value_counts().to_dict()
        pct_zero = (split_df["n_multi_active"] == 0).mean() * 100
        pct_one = (split_df["n_multi_active"] == 1).mean() * 100
        pct_multi = (split_df["n_multi_active"] >= 2).mean() * 100
        mean_active = split_df["n_multi_active"].mean()
        
        # 단일 방식이 놓치는 활성 국면 총 개수 및 비율
        total_omitted = split_df["n_omitted_active"].sum()
        total_active_all = split_df["n_multi_active"].sum()
        omitted_ratio = (total_omitted / total_active_all * 100) if total_active_all > 0 else 0.0
        
        # Hurdle 방식에서 비활성화(none) 비율
        pct_hurdle_none = (split_df["hurdle_regime"] == "none").mean() * 100
        
        metrics.append({
            "split": split_name,
            "n_months": n_m,
            "mean_active_regimes": round(mean_active, 3),
            "pct_0_active": round(pct_zero, 2),
            "pct_1_active": round(pct_one, 2),
            "pct_2plus_active": round(pct_multi, 2),
            "pct_hurdle_none": round(pct_hurdle_none, 2),
            "total_active_events": int(total_active_all),
            "total_omitted_by_argmax": int(total_omitted),
            "omitted_information_ratio_pct": round(omitted_ratio, 2)
        })
    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv(OUT_DIR / "single_vs_multi_metrics.csv", index=False, encoding="utf-8-sig")
    
    # 3. 국면 조합(Co-occurrence) 분석
    comb_counts = res_df.groupby(["period", "multi_regimes"]).size().reset_index(name="frequency")
    comb_counts = comb_counts.sort_values(["period", "frequency"], ascending=[True, False])
    comb_counts.to_csv(OUT_DIR / "single_vs_multi_regime_combinations.csv", index=False, encoding="utf-8-sig")
    
    # 4. 품질 관리 및 보고용 마크다운 생성
    table_headers = list(metrics_df.columns)
    table_rows = []
    for _, r in metrics_df.iterrows():
        table_rows.append("| " + " | ".join(str(r[c]) for c in table_headers) + " |")
    md_table = "| " + " | ".join(table_headers) + " |\n| " + " | ".join(["---"] * len(table_headers)) + " |\n" + "\n".join(table_rows)

    md_lines = [
        "# 연구 A: 단일 국면 vs 다중 국면 활성화 비교 분석 QC 보고서 (`single_vs_multi_qc.md`)",
        "",
        "- **분석 일시:** 2026-11-01",
        "- **기준 모델:** Phase 5.6 결정론적 Strict OOS 모델 (`RUN_PHASE5_6_20261027_184959`)",
        "- **데이터:** `data/processed/reactions/phase5_6_train_only_regime_monthly.csv` (학습 48m 모수 고정 표준화)",
        "",
        "## 1. 핵심 비교 메트릭 요약",
        "",
        md_table,
        "",
        "## 2. 주요 정량적 발견 사항",
        "",
        f"1. **복합 국면(2개 이상 동시 활성화)의 빈도:**",
        f"   - 학습 기간(48개월) 중 2개 이상의 국면이 동시 점등된 달은 **{metrics_df.loc[metrics_df['split']=='Train (48m)', 'pct_2plus_active'].values[0]}%**에 달함.",
        f"   - Strict OOS 테스트 기간(19개월)에서도 2개 이상 동시 활성화 비율은 **{metrics_df.loc[metrics_df['split']=='Eval OOS (19m)', 'pct_2plus_active'].values[0]}%**로 유지됨.",
        f"2. **단일 대표 국면(Argmax)의 정보 누락률(Omitted Information Ratio):**",
        f"   - 단일 대표 국면 하나만 선택할 경우, 동일 기준(z >= 0.5)을 만족하는 유효 국면 정보의 **{metrics_df.loc[metrics_df['split']=='Full (67m)', 'omitted_information_ratio_pct'].values[0]}% (전체 {int(metrics_df.loc[metrics_df['split']=='Full (67m)', 'total_active_events'].values[0])}건 중 {int(metrics_df.loc[metrics_df['split']=='Full (67m)', 'total_omitted_by_argmax'].values[0])}건)**가 강제로 절단·누락됨.",
        f"3. **반복적으로 함께 나타나는 국면 조합:**",
        f"   - 고물가·긴축기 동안 `macro;capital` 또는 `macro;realestate`의 동시 점등이 빈번히 관찰됨.",
        f"4. **해석상 주의 및 엄격한 한계:**",
        f"   - 다중 국면 방식이 정의상 더 많은 국면을 살려두는 것은 산술적 당연함(Tautology)일 수 있음.",
        f"   - 따라서 단순히 '더 많은 국면이 켜졌다'는 사실 자체를 우수성의 증거로 포장하지 않으며, 이 추가 정보가 실제 기사의 복합 주제를 반영하는지는 연구 C의 사람 라벨과의 대조를 통해 최종 검증되어야 함.",
        ""
    ]
    (OUT_DIR / "single_vs_multi_qc.md").write_text("\n".join(md_lines), encoding="utf-8")
    print("연구 A 완료: single_vs_multi_*.csv 및 qc.md 생성 완료.")

if __name__ == "__main__":
    run_experiment()
