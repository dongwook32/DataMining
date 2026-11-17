"""Final paper: train. See core/description.md."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any
from util.paths import ROOT
from config.research import EVAL_END, EVAL_START, H1_DOMAIN, H2_DOMAIN, KST, MASS_TIE_RATIO, MAX_DF_RATIO, MIN_DF, MIN_MAP_SHARE, NMF_INIT, NMF_MAX_ITER, N_TOPICS, PER_MONTH_SAMPLE, SCRIPT_VERSION, SEED, STUDY_START, TOP_N_VOCAB, TRAIN_END
from core.regime_analysis import build_regime_monthly, domain_support, map_topics, mapping_hash
from core.forecast_analysis import compute_all_metrics, run_forecasts
from core.reporting import cross_run_rows, render_markdown
from core.validation import overall_verdict, post_md_checks, pre_md_checks
from core.topic_analysis import run_core
from util.research import safe_path, sha256_file


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--core-only", action="store_true")
    ap.add_argument("--artifact-root", default=str(ROOT / "data" / "processed" / "phase5_6_artifacts"))
    ap.add_argument("--deliver-dir", default=str(ROOT / "data" / "processed" / "reactions"))
    ap.add_argument("--rerun-dir", default=None)
    ap.add_argument("--excel-dir", type=Path, help="이번 실행의 결과 엑셀을 저장할 상위 폴더")
    ap.add_argument("--subsample", type=int, default=1, help="개발용: N번째 문서마다 사용(최종 실행은 1)")
    args = ap.parse_args()
    if args.core_only and args.excel_dir is not None:
        ap.error("--excel-dir은 전체 v4 분석에서 사용합니다.")

    now = dt.datetime.now(KST)
    stamp = now.strftime("%Y%m%d_%H%M%S")
    corpus_path = ROOT / "data" / "processed" / "corpus" / "news_corpus.parquet"
    panel_path = ROOT / "data" / "processed" / "panel" / "monthly_panel.csv"
    art_root = Path(args.artifact_root)

    if args.core_only:
        run_id = f"RUN_PHASE5_6_CORE_{stamp}"
        run_core(corpus_path, run_id, art_root / run_id, args.subsample)
        print(f"\ncore-only 완료: {art_root / run_id}")
        return

    run_id = f"RUN_PHASE5_6_{stamp}"
    deliver = Path(args.deliver_dir)
    deliver.mkdir(parents=True, exist_ok=True)
    art_dir = art_root / run_id
    corpus_sha, panel_sha = sha256_file(corpus_path), sha256_file(panel_path)
    print(f"corpus sha={corpus_sha}\npanel  sha={panel_sha}", flush=True)

    core = run_core(corpus_path, run_id, art_dir, args.subsample)
    meta, H, vocab = core["meta"], core["H"], core["vocab"]

    df_map = map_topics(H, vocab)
    map_sha = mapping_hash(df_map)
    support = domain_support(df_map)
    df_map.insert(0, "run_id", run_id)
    paths = {k: safe_path(deliver / f"phase5_6_{v}") for k, v in {
        "forecast": "strict_oos_forecast.csv", "regime": "train_only_regime_monthly.csv",
        "mapping": "topic_regime_mapping.csv", "audit": "pipeline_audit.json", "md": "strict_oos_forecast.md"}.items()}
    df_map.to_csv(paths["mapping"], index=False, encoding="utf-8-sig")
    print(df_map[["topic", "status", "assigned_slug", "best_slug", "best_share", "mass_ratio"]].to_string(), flush=True)

    df_regime = build_regime_monthly(core["df_topic"], df_map, run_id)
    df_regime.to_csv(paths["regime"], index=False, encoding="utf-8-sig")
    panel_loaded_after_mapping = True  # 패널은 아래에서 처음 읽는다(run_forecasts 내부)

    ok_h1, ok_h2 = support[H1_DOMAIN]["status"].startswith("supported"), support[H2_DOMAIN]["status"].startswith("supported")
    df_f, df_study = run_forecasts(df_regime, panel_path, run_id, f"share_{H1_DOMAIN}", f"share_{H2_DOMAIN}", ok_h1, ok_h2)
    df_f.to_csv(paths["forecast"], index=False, encoding="utf-8-sig")
    metrics = compute_all_metrics(df_f)

    ctx: dict[str, Any] = {
        "run_id": run_id, "meta": meta, "H": H, "vocab": vocab, "df_map": df_map, "support": support, "map_sha": map_sha,
        "metrics": metrics, "art_dir": art_dir, "regime_path": paths["regime"], "forecast_path": paths["forecast"],
        "df_study": df_study, "rerun_dir": args.rerun_dir, "panel_loaded_after_mapping": panel_loaded_after_mapping,
        "started_kst": now.strftime("%Y-%m-%d %H:%M:%S"), "started_utc": now.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "corpus_rel": str(corpus_path.relative_to(ROOT)).replace("\\", "/"), "corpus_sha": corpus_sha,
        "panel_rel": str(panel_path.relative_to(ROOT)).replace("\\", "/"), "panel_sha": panel_sha,
        "art_rel": str(art_dir.relative_to(ROOT)).replace("\\", "/") if art_dir.is_relative_to(ROOT) else str(art_dir),
        "cross_rows": cross_run_rows(ROOT),
    }
    pre = pre_md_checks(ctx)
    ctx["checks"] = pre
    paths["md"].write_text(render_markdown(ctx), encoding="utf-8")
    post = post_md_checks(ctx, paths["md"], {k: paths[k] for k in ("forecast", "regime", "mapping", "md")})
    checks = {**pre, **post}
    verdict = overall_verdict(checks)

    audit = {
        "run_id": run_id, "script_version": SCRIPT_VERSION,
        "started_kst": ctx["started_kst"], "started_utc": ctx["started_utc"],
        "inputs": {"news_corpus": {"path": ctx["corpus_rel"], "sha256": corpus_sha},
                   "monthly_panel": {"path": ctx["panel_rel"], "sha256": panel_sha}},
        "design": {"train": [STUDY_START, TRAIN_END], "eval": [EVAL_START, EVAL_END], "seed": SEED,
                   "min_df": MIN_DF, "max_df_ratio": MAX_DF_RATIO, "top_n_vocab": TOP_N_VOCAB, "n_topics": N_TOPICS,
                   "per_month_sample": PER_MONTH_SAMPLE, "nmf_max_iter": NMF_MAX_ITER, "nmf_init": NMF_INIT,
                   "min_map_share": MIN_MAP_SHARE, "mass_tie_ratio": MASS_TIE_RATIO},
        "core": meta,
        "mapping": {"sha256": map_sha, "domain_support": support,
                    "feature_links": {"H1": {"domain": H1_DOMAIN, "topics": support[H1_DOMAIN]["topics"], "column": f"share_{H1_DOMAIN}", "lags": [1, 2]},
                                      "H2": {"domain": H2_DOMAIN, "topics": support[H2_DOMAIN]["topics"], "column": f"share_{H2_DOMAIN}", "lags": [1]}}},
        "artifacts": {p.name: sha256_file(p) for p in sorted(art_dir.iterdir())},
        "deliverables": {k: {"path": str(paths[k].name), "sha256": sha256_file(paths[k])} for k in ("forecast", "regime", "mapping", "md")},
        "checks": checks,
        "overall_verdict": verdict,
        "notes": ["MD 작성 이후 항목(16~18)은 MD 파일 생성 뒤 실행됨", "이 JSON 자신의 해시는 포함되지 않음"],
    }
    paths["audit"].write_text(json.dumps(audit, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("\n=== AUDIT ===")
    for k, v in checks.items():
        print(f"{v['status']:<22} {k}  :: {v['detail'][:140]}")
    print(f"\nOVERALL: {verdict}\nrun_id={run_id}")
    for k, p in paths.items():
        print(f"{k}: {p}")
    if args.excel_dir is not None:
        from core.excel_export import export_results

        for output in export_results(
            art_dir, paths["audit"], args.excel_dir / run_id, study=df_study, metrics=metrics,
        ):
            print(f"excel: {output}")


run = main

if __name__ == "__main__":
    main()

