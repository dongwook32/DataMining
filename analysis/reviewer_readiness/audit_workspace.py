"""Phase 1: 프로젝트 전수 감사 및 기준 데이터 SHA-256 불변성 매니페스트 생성 스크립트.

기존 데이터·아티팩트를 수정하지 않고, 모든 핵심 파일의 존재 여부, 바이트 크기, SHA-256 해시,
그리고 Phase 5.6 Strict OOS 및 연구 A·B 기준 수치를 실제 파일에서 대조·기록한다.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
RUN_ID = "RUN_20261106_161800"
OUT_DIR = ROOT / "data" / "processed" / "reviewer_readiness" / RUN_ID
OUT_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> None:
    print(f"[Phase 1] Starting workspace audit -> {OUT_DIR}", flush=True)

    # 1. 핵심 파일 목록 및 SHA-256 해시 계산
    tracked_files = [
        # 논문 및 감사 보고서
        ("manuscript_baseline", "docs/PAPER_DRAFT_JKIICE.md"),
        ("manuscript_pre_study_c_backup", "docs/drafts/PAPER_DRAFT_JKIICE_pre_study_c_removal_20261102.md"),
        ("manuscript_pre_final_backup", "docs/drafts/PAPER_DRAFT_JKIICE_pre_final_correction_20261101.md"),
        ("manuscript_pre_supp_backup", "docs/drafts/PAPER_DRAFT_JKIICE_pre_supplemental_20261101.md"),
        ("audit_reconciliation", "docs/PAPER_RESULT_RECONCILIATION_20261101.md"),
        ("audit_final_correction", "docs/PAPER_FINAL_CORRECTION_AUDIT_20261101.md"),
        ("audit_human_removal", "docs/PAPER_HUMAN_VALIDATION_REMOVAL_AUDIT_20261102.md"),
        ("audit_statistical", "docs/PAPER_FINAL_STATISTICAL_AUDIT_20261101.md"),
        ("final_research_results", "docs/FINAL_RESEARCH_RESULTS.md"),
        ("verification_three_final", "docs/verification/verification_three_analyses_final.md"),
        # Phase 5.6 핵심 아티팩트
        ("phase5_6_core_meta", "data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/core_meta.json"),
        ("phase5_6_vocab_idf", "data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/vocab_idf.csv"),
        ("phase5_6_nmf_H", "data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/nmf_H.npy"),
        ("phase5_6_models", "data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/models.joblib"),
        ("phase5_6_fit_sample_ids", "data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/fit_sample_ids.csv"),
        ("phase5_6_monthly_topic_share", "data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/monthly_topic_share.csv"),
        ("phase5_6_topic_regime_mapping", "data/processed/reactions/phase5_6_topic_regime_mapping.csv"),
        ("phase5_6_train_only_regime_monthly", "data/processed/reactions/phase5_6_train_only_regime_monthly.csv"),
        ("phase5_6_pipeline_audit", "data/processed/reactions/phase5_6_pipeline_audit.json"),
        # 검증 CSV 및 보충 실험 CSV
        ("verification_ols_results", "data/processed/reactions/verification_ols_results.csv"),
        ("verification_corr_lag_results", "data/processed/reactions/verification_correlation_lag_results.csv"),
        ("verification_warning_results", "data/processed/reactions/verification_warning_performance_results.csv"),
        ("verification_rate_hike_table", "data/processed/reactions/verification_rate_hike_event_table.csv"),
        ("study_a_metrics", "data/processed/supplemental_validation/single_vs_multi_metrics.csv"),
        ("study_a_monthly", "data/processed/supplemental_validation/single_vs_multi_monthly.csv"),
        ("study_a_combinations", "data/processed/supplemental_validation/single_vs_multi_regime_combinations.csv"),
        ("study_b_weekly_panel", "data/processed/supplemental_validation/news_search_weekly_panel.csv"),
        ("study_b_hac_results", "data/processed/supplemental_validation/news_search_hac_results.csv"),
        ("study_b_anchor_sensitivity", "data/processed/supplemental_validation/news_search_anchor_sensitivity.csv"),
        # 원시 코퍼스 및 거시·검색 데이터
        ("news_corpus_parquet", "data/processed/corpus/news_corpus.parquet"),
        ("monthly_panel_csv", "data/processed/panel/monthly_panel.csv"),
        ("datalab_regime_daily", "data/raw/datalab/datalab_regime_daily.csv"),
        ("datalab_sub_daily", "data/raw/datalab/datalab_sub_daily.csv"),
        ("legacy_regime_monthly_do_not_use", "data/processed/regimes/regime_monthly.csv"),
        # 핵심 스크립트
        ("script_phase5_6_v4", "analysis/validate_strict_oos_forecast_v4.py"),
        ("script_verify_three", "analysis/verify_three_analyses.py"),
        ("script_study_a", "analysis/supplemental_validation/run_study_a.py"),
        ("script_study_b", "analysis/supplemental_validation/run_study_b.py"),
        ("script_study_b_hac", "analysis/supplemental_validation/verify_hac_news_search.py"),
        ("script_study_b_anchor", "analysis/supplemental_validation/verify_anchor_sensitivity.py"),
        ("script_datalab_keywords", "api/datalab_keyword_sets.py"),
    ]

    manifest_rows = []
    for role, rel_path in tracked_files:
        p = ROOT / rel_path
        exists = p.exists()
        size = p.stat().st_size if exists and p.is_file() else 0
        digest = sha256_file(p)
        manifest_rows.append({
            "role": role,
            "relative_path": rel_path,
            "exists": exists,
            "size_bytes": size,
            "sha256": digest,
        })

    manifest_df = pd.DataFrame(manifest_rows)
    manifest_df.to_csv(OUT_DIR / "workspace_baseline_manifest.csv", index=False, encoding="utf-8-sig")

    # 2. core_meta.json 및 models.joblib 직접 검증
    art_dir = ROOT / "data" / "processed" / "phase5_6_artifacts" / "RUN_PHASE5_6_20261027_184959"
    core_meta = json.loads((art_dir / "core_meta.json").read_text(encoding="utf-8"))
    models_obj = joblib.load(art_dir / "models.joblib")
    H_arr = np.load(art_dir / "nmf_H.npy")
    vocab_df = pd.read_csv(art_dir / "vocab_idf.csv")
    fit_ids_df = pd.read_csv(art_dir / "fit_sample_ids.csv")

    nmf_model = models_obj["nmf"]
    tfidf_model = models_obj["tfidf"]

    # 수치 정합성 확인
    reg_monthly = pd.read_csv(ROOT / "data" / "processed" / "reactions" / "phase5_6_train_only_regime_monthly.csv")
    study_a_metrics = pd.read_csv(ROOT / "data" / "processed" / "supplemental_validation" / "single_vs_multi_metrics.csv")
    study_b_hac = pd.read_csv(ROOT / "data" / "processed" / "supplemental_validation" / "news_search_hac_results.csv")
    ols_df = pd.read_csv(ROOT / "data" / "processed" / "reactions" / "verification_ols_results.csv")
    ols_p56 = ols_df[ols_df["model_id"] == "Phase56_StrictOOS_ret_std_67m"].iloc[0]

    # Git 상태 확인
    git_status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stdout.strip()

    pip_list = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()

    env_spec = {
        "audit_timestamp": dt.datetime.now().isoformat(),
        "run_id": RUN_ID,
        "output_directory": str(OUT_DIR),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "phase5_6_verification": {
            "run_id": core_meta["run_id"],
            "raw_rows": core_meta["counts"]["raw_rows"],
            "train_docs": core_meta["counts"]["train_docs"],
            "eval_docs": core_meta["counts"]["eval_docs"],
            "vocab_size_meta": core_meta["vocab_size"],
            "vocab_size_csv": len(vocab_df),
            "n_fit_sample_meta": core_meta["n_fit_sample"],
            "n_fit_sample_csv": len(fit_ids_df),
            "fit_sample_max_month": str(fit_ids_df["month"].max()),
            "nmf_H_shape": list(H_arr.shape),
            "nmf_params_from_joblib": nmf_model.get_params(),
            "tfidf_params_from_joblib": tfidf_model.get_params(),
            "H_max_abs_diff_vs_joblib": float(np.max(np.abs(H_arr - nmf_model.components_))),
            "idf_max_abs_diff_vs_csv": float(np.max(np.abs(vocab_df["idf"].to_numpy() - tfidf_model.idf_))),
        },
        "verified_baseline_numbers": {
            "total_months": len(reg_monthly),
            "train_months": int((reg_monthly["period"] == "train").sum()),
            "eval_months": int((reg_monthly["period"] == "eval").sum()),
            "study_a_full": study_a_metrics[study_a_metrics["split"] == "Full (67m)"].iloc[0].to_dict(),
            "study_a_train": study_a_metrics[study_a_metrics["split"] == "Train (48m)"].iloc[0].to_dict(),
            "study_a_eval": study_a_metrics[study_a_metrics["split"] == "Eval OOS (19m)"].iloc[0].to_dict(),
            "ols_kospi_ret_std_67m": {
                "n_obs": int(ols_p56["sample_n"]),
                "r2": float(ols_p56["r_squared"]),
                "adj_r2": float(ols_p56["adj_r_squared"]),
                "f_stat_hac": float(ols_p56["f_statistic"]),
                "f_pvalue_hac": float(ols_p56["f_pvalue"]),
            },
        },
        "installed_packages": json.loads(pip_list) if pip_list else [],
        "git_status_short": git_status.splitlines(),
    }

    (OUT_DIR / "workspace_environment_spec.json").write_text(
        json.dumps(env_spec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 3. 감사 요약 마크다운 작성
    missing_count = int((~manifest_df["exists"]).sum())
    md = [
        f"# Phase 1: 로컬 워크스페이스 전수 감사 및 불변성 기준 명세 (`{RUN_ID}`)",
        "",
        f"- **감사 일시**: {env_spec['audit_timestamp']}",
        f"- **Python 실행 환경**: `{sys.executable}` (`Python {sys.version.split()[0]}`)",
        f"- **신규 산출물 격리 경로**: `data/processed/reviewer_readiness/{RUN_ID}/`",
        f"- **점검 대상 핵심 파일 수**: {len(manifest_df)}개 (누락 파일: {missing_count}개)",
        "",
        "## 1. Phase 5.6 Strict OOS 아티팩트 무결성 검증",
        "",
        f"- **기준 아티팩트 경로**: `data/processed/phase5_6_artifacts/RUN_PHASE5_6_20261027_184959/`",
        f"- **전체 기사 수**: {core_meta['counts']['raw_rows']:,}건 (학습 2021-01~2024-12: {core_meta['counts']['train_docs']:,}건 / 테스트 2025-01~2026-07: {core_meta['counts']['eval_docs']:,}건)",
        f"- **학습 전용 어휘 사전 크기**: {len(vocab_df):,}개 (`vocab_sha256 = {core_meta['vocab_sha256']}`)",
        f"- **NMF 적합 표본**: {len(fit_ids_df):,}건 (월 3,000건 × 48개월, 최대 월 = `{fit_ids_df['month'].max()}`, `sample_ids_sha256 = {core_meta['sample_ids_sha256']}`)",
        f"- **NMF 모델 파라미터 (`models.joblib` 실측)**: `n_components={nmf_model.n_components}`, `init='{nmf_model.init}'`, `solver='{nmf_model.solver}'`, `beta_loss='{nmf_model.beta_loss}'`, `max_iter={nmf_model.max_iter}`, `random_state={nmf_model.random_state}`, `tol={nmf_model.tol}`",
        f"- **`nmf_H.npy` vs `models.joblib` H 행렬 최대 절대 오차**: `{env_spec['phase5_6_verification']['H_max_abs_diff_vs_joblib']:.3e}`",
        f"- **`vocab_idf.csv` vs `models.joblib` IDF 벡터 최대 절대 오차**: `{env_spec['phase5_6_verification']['idf_max_abs_diff_vs_csv']:.3e}`",
        "",
        "## 2. 핵심 파일 SHA-256 기준 해시 요약",
        "",
        "| 역할 (Role) | 상대 경로 (Relative Path) | 존재 여부 | 크기 (Bytes) | SHA-256 (앞 16자리) |",
        "| :--- | :--- | :---: | ---: | :--- |",
    ]
    for _, r in manifest_df.iterrows():
        md.append(
            f"| `{r['role']}` | `{r['relative_path']}` | {'YES' if r['exists'] else 'NO'} | {r['size_bytes']:,} | `{str(r['sha256'])[:16]}...` |"
        )

    md.extend([
        "",
        "## 3. 불변성 및 격리 실행 원칙 확인",
        "",
        "1. `analysis/detect_regimes.py` 및 `data/regime_monthly.csv` (과거 8개 국면 Legacy 산출물)는 최종 6개 국면 분석 및 신규 실험의 입력으로 사용하지 않음.",
        "2. 기존 `data/processed/phase5_6_artifacts/`, `data/processed/reactions/`, `data/processed/supplemental_validation/`, `docs/PAPER_DRAFT_JKIICE.md`는 수정하거나 덮어쓰지 않음.",
        f"3. 모든 신규 실험 코드는 `analysis/reviewer_readiness/`에, 모든 신규 실험 데이터는 `data/processed/reviewer_readiness/{RUN_ID}/`에 격리 저장함.",
    ])

    (OUT_DIR / "workspace_audit_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[Phase 1] Completed! Checked {len(manifest_df)} files (missing={missing_count}).", flush=True)


if __name__ == "__main__":
    main()
