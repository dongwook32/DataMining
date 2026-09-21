"""processed 캐시부터 반응·강건성·RQ4·(조건부) 폴백까지 한 번에.

  python -m analysis.run_pipeline
  python -m analysis.run_pipeline --force-fallback
  python -m analysis.run_pipeline --skip-fallback

raw 재수집·NMF 재적합은 하지 않는다. 입력은 이미 있는
`doc_term.npz` · `monthly_panel.csv` · `regime_monthly.csv` 이다.

폴백 트리거 (둘 중 하나면 LDA):
  1. 주 종속변수 3개(kospi_ret, usdkrw_ret, ccsi_diff)의 KW가 모두 p>=0.05
  2. 2026 제외 표본에서 위 3개 중 하나라도 유의 여부(p<0.05)가 뒤집힘

산출:
  data/processed/reactions/  (본분석 + RQ4 + 강건성)
  data/processed/regimes_lda/, reactions_lda/  (트리거 시에만)
  data/processed/reactions/pipeline_qc.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from analysis.measure_reactions import PRIMARY_DEPS, analyze, load_joined
from analysis.robustness import run as run_robustness
from analysis.rq4_search import run as run_rq4
from config import load_config, project_root

ROOT = project_root()
PANEL = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
REGIME = ROOT / "data" / "processed" / "regimes" / "regime_monthly.csv"
CP = ROOT / "data" / "processed" / "regimes" / "changepoints.csv"
MATRIX = ROOT / "data" / "processed" / "corpus" / "doc_term.npz"
OUT_DIR = ROOT / "data" / "processed" / "reactions"
QC_PATH = OUT_DIR / "pipeline_qc.md"
DECISION_PATH = OUT_DIR / "fallback_decision.json"

ALPHA = 0.05
REQUIRED = [PANEL, REGIME, CP, MATRIX]


def check_cache() -> list[str]:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.exists()]
    return missing


def decide_fallback(tests: pd.DataFrame, compare: pd.DataFrame) -> dict:
    kw = tests[tests["test"] == "kruskal"].set_index("dep_var")
    primary_p = {d: float(kw.loc[d, "p_value"]) for d in PRIMARY_DEPS if d in kw.index}
    any_sig = any(p < ALPHA for p in primary_p.values())
    reasons: list[str] = []
    if not any_sig:
        reasons.append(
            "주 종속변수 3개 KW가 모두 p>=0.05 — 단일 라벨 그룹 차이만으로는 약함"
        )
    flips = compare[compare["dep_var"].isin(PRIMARY_DEPS) & compare["flipped"]]
    if not flips.empty:
        names = ", ".join(flips["dep_var"].tolist())
        reasons.append(f"2026 제외에서 주 종속변수 유의 여부 뒤집힘: {names}")
    return {
        "trigger": bool(reasons),
        "reasons": reasons,
        "primary_p": primary_p,
        "any_primary_kw_sig": any_sig,
        "alpha": ALPHA,
    }


def write_qc(decision: dict, steps: list[str], bertopic_note: str | None) -> None:
    lines: list[str] = []
    add = lines.append
    add("# 통합 파이프라인 점검")
    add("")
    add(f"생성: `analysis.run_pipeline` · {pd.Timestamp.now():%Y-%m-%d %H:%M}")
    add("")
    add("본분석 국면은 NMF다. raw 재수집과 NMF 재적합은 하지 않았다.")
    add("")
    add("## 1. 실행한 단계")
    add("")
    for s in steps:
        add(f"- {s}")
    add("")
    add("## 2. 폴백 판정")
    add("")
    add("| 항목 | 값 |")
    add("|------|-----|")
    add(f"| 트리거 | {'켜짐' if decision['trigger'] else '꺼짐'} |")
    add(f"| 기준 α | {decision['alpha']} |")
    add(f"| 주 종속 KW 유의 하나라도 | {'예' if decision['any_primary_kw_sig'] else '아니오'} |")
    for d, p in decision["primary_p"].items():
        add(f"| KW p `{d}` | {p:.4f} |")
    add("")
    if decision["reasons"]:
        add("이유:")
        for r in decision["reasons"]:
            add(f"- {r}")
    else:
        add("폴백을 켜지 않았다.")
    add("")
    if bertopic_note:
        add(f"BERTopic: {bertopic_note}")
        add("")
    add("## 3. 산출 위치")
    add("")
    add("| 단계 | 경로 |")
    add("|------|------|")
    add("| 본분석 반응 | `data/processed/reactions/` |")
    add("| 강건성 | `robustness_*.csv`, `robustness_qc.md` |")
    add("| RQ4 | `rq4_*.csv`, `rq4_qc.md` |")
    if decision.get("fallback_ran"):
        add("| 폴백 LDA 국면 | `data/processed/regimes_lda/` |")
        add("| 폴백 반응 | `data/processed/reactions_lda/` |")
    add("")
    QC_PATH.write_text("\n".join(lines), encoding="utf-8")


def run(*, force_fallback: bool, skip_fallback: bool) -> dict:
    missing = check_cache()
    if missing:
        raise FileNotFoundError(
            "processed 캐시가 없다. raw 재수집은 하지 않는다. 없는 파일: "
            + ", ".join(missing)
        )

    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    steps: list[str] = []

    print("=== [1] NMF 국면 반응 ===", flush=True)
    df = load_joined(labels, slugs)
    cps = pd.read_csv(CP, dtype={"cp_month": str})
    rx = analyze(df, cps, labels, slugs, OUT_DIR)
    steps.append("measure_reactions (NMF 국면 × 패널)")

    print("\n=== [2] 강건성 2026 제외 ===", flush=True)
    rob = run_robustness()
    steps.append("robustness (2026-01 이후 제외)")

    print("\n=== [3] RQ4 검색 정합 ===", flush=True)
    rq4 = run_rq4()
    steps.append("rq4_search (뉴스 비중·라벨 vs 데이터랩)")

    decision = decide_fallback(rx["tests"], rob["compare"])
    if force_fallback:
        decision["reasons"].append("--force-fallback")
        decision["trigger"] = True
    if skip_fallback:
        decision["reasons"].append("--skip-fallback 로 실행 생략")
        decision["trigger"] = False

    bertopic_note = None
    decision["fallback_ran"] = False
    if decision["trigger"]:
        print("\n=== [4] 폴백 LDA ===", flush=True)
        from analysis.fallback_topics import run_fallback_reactions, run_lda, try_bertopic
        from analysis.detect_regimes import FIT_PER_MONTH

        tm = cfg["topic_model"]
        run_lda(
            int(tm["n_topics"]), int(tm["random_state"]),
            15, FIT_PER_MONTH, 2048,
        )
        steps.append("fallback_topics LDA (같은 행렬, 매핑 규칙 동일, 수동 덮어쓰기 없음)")
        bt = try_bertopic()
        bertopic_note = bt["reason"]
        run_fallback_reactions()
        steps.append("measure_reactions on LDA 국면 → reactions_lda/")
        decision["fallback_ran"] = True
    else:
        print("\n=== [4] 폴백 생략 ===", flush=True)
        steps.append("폴백 생략 (트리거 아님 또는 --skip-fallback)")

    DECISION_PATH.write_text(
        json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    write_qc(decision, steps, bertopic_note)
    print(f"\n판정 → {DECISION_PATH}")
    print(f"QC   → {QC_PATH}")
    return {"reactions": rx, "robustness": rob, "rq4": rq4, "decision": decision}


def main() -> None:
    p = argparse.ArgumentParser(description="processed 캐시부터 최종 분석까지")
    p.add_argument("--force-fallback", action="store_true")
    p.add_argument("--skip-fallback", action="store_true")
    a = p.parse_args()
    if a.force_fallback and a.skip_fallback:
        raise SystemExit("--force-fallback 과 --skip-fallback 을 같이 쓸 수 없다")
    run(force_fallback=a.force_fallback, skip_fallback=a.skip_fallback)


if __name__ == "__main__":
    main()
