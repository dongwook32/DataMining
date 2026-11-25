"""Recompute the submitted v4 analysis in an isolated run directory."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER_SUPPORT = Path("output/paper/replication")
LEGACY_PANEL = Path("data/processed/regimes/regime_monthly.csv")
MODEL_DIR = Path("data/processed/models/base")
REACTIONS = Path("data/processed/reactions")


def pipeline_tasks(work):
    """List the paper's reproduction steps in execution order."""
    def module(name, *args):
        return [sys.executable, "-B", "-m", name, *map(str, args)]

    return [
        dict(label="01. 원자료 전처리", commands=[module("core.preprocess")]),
        dict(label="02. TF-IDF·NMF 재학습, 국면, 예측",
             commands=[module("core.train", "--model-dir", work / MODEL_DIR)]),
        dict(label="03. 다중 국면과 사례", commands=[
            module("core.regimes.run_study_a"),
            module("core.regimes.analyze_multi_regime_cases"),
        ]),
        dict(label="04. 시장 반응과 경보", commands=[module("core.market_analysis")]),
        dict(label="05. 주별 뉴스·검색", commands=[module("core.search_analysis")]),
        dict(label="06. 토픽 품질과 반복 안정성", commands=[
            module("core.topic_quality.compare_nmf_lda"),
            module("core.topic_quality.run_topic_stability"),
        ]),
        dict(label="07. 강건성, 수렴 및 후속 민감도", commands=[module("core.robustness_analysis")]),
        dict(label="08. 원자료·논문 주요 수치 검산", commands=[
            [sys.executable, "-B", str(PAPER_SUPPORT / name)]
            for name in ("audit_s1.py", "verify_panels.py")
        ], verification=True),
    ]


INPUT_DIRECTORIES = ("script", "results/docs", "data/raw")
RESULT_TABLES = {
    "corpus": ("news_counts.csv",),
    "models/base": ("core_meta.json", "monthly_topic_share.csv"),
    "reactions": (
        "audit.json", "forecast.csv", "forecast.md", "topic_map.csv",
        "regime_monthly.csv", "ols.csv", "lag_corr.csv", "warnings.csv",
    ),
    "checks": ("multi_metrics.csv", "multi_monthly.csv", "search_splits.csv", "search_hac.csv"),
    "review/topics": (
        "model_metrics.csv", "stability_summary.csv", "regime_stability.csv",
        "case_months.csv", "hac_lags.csv", "search_ci.csv",
    ),
    "review/convergence": ("convergence_metrics.csv", "topic_alignment.csv", "topic_terms_400.csv"),
    "review/sensitivity": (
        "multi_compare.csv", "hac_compare.csv", "oos_compare.csv", "naver_weekly.csv",
    ),
}
APPENDIX_FILES = ("news_files.csv", "regime_terms.csv", "search_terms.json")
STAGED_MODULE_NAMES = {
    "preprocessing/schema.py": "bigkinds_schema.py",
    "regimes/case_analysis.py": "analyze_multi_regime_cases.py",
    "topic_quality/compare.py": "compare_nmf_lda.py",
    "topic_quality/quality.py": "evaluate_topic_quality.py",
    "topic_quality/stability.py": "run_topic_stability.py",
    "robustness/sensitivity.py": "compare_nmf_downstream_sensitivity.py",
    "robustness/convergence.py": "verify_nmf_convergence.py",
    "robustness/search_checks.py": "verify_search_robustness.py",
    "search/anchor_check.py": "verify_anchor_sensitivity.py",
    "search/hac.py": "verify_hac_news_search.py",
}

def stage_inputs(work):
    source = ROOT / "script"
    copies = [
        (ROOT / "data/raw", work / "data/raw"),
        (ROOT / "results/docs", work / "docs"),
        (ROOT / LEGACY_PANEL, work / LEGACY_PANEL),
        (source / "01_inputs/collector", work / "collector"),
        (source / "_shared/config", work / "config"),
        (source / "_shared/util", work / "util"),
        (source / "_shared/__init__.py", work / "core/__init__.py"),
        (source / "_shared/v4.py", work / "core/v4.py"),
        (source / "run_all.py", work / "core/reproduce.py"),
    ]
    # Preserve the research modules' import names and audit paths inside each run.
    audit_scripts = {"audit_s1.py", "verify_panels.py"}
    for folder in ("02_preprocess", "03_train", "04_regimes", "05_validate", "06_analyze"):
        for item in sorted((source / folder).iterdir()):
            if item.name in {"__pycache__", "run_excel.py"}:
                continue
            relative = PAPER_SUPPORT if item.name in audit_scripts else Path("core")
            copies.append((item, work / relative / item.name))
    for item, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        if item.is_dir():
            shutil.copytree(item, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(item, target)
    for relative, original_name in STAGED_MODULE_NAMES.items():
        short_path = work / "core" / relative
        short_path.rename(short_path.with_name(original_name))


def is_local_directory(path, parent):
    return (path.is_dir() and not path.is_symlink() and not path.is_junction()
            and path.resolve() == parent.resolve() / path.name)


def remove_numbered_runs(destination):
    for entry in destination.glob("run_*"):
        if (entry.name[4:].isdigit() and is_local_directory(entry, destination)
                and any((entry / name).is_file() for name in ("status.txt", "상태.txt"))):
            shutil.rmtree(entry)


def save_results(run, *, keep_full):
    work = run / "work"
    if work.resolve() != run.resolve() / "work" or work.is_symlink() or work.is_junction():
        raise ValueError("정리할 작업 폴더의 경로가 실행 폴더와 일치하지 않습니다.")

    processed = work / "data/processed"
    copies = [
        (processed / folder / name, run / "tables" / folder / name)
        for folder, names in RESULT_TABLES.items()
        for name in names
    ]
    copies.extend((work / PAPER_SUPPORT / name, run / "checks" / name) for name in APPENDIX_FILES)
    missing = [source.relative_to(work).as_posix() for source, _ in copies if not source.is_file()]
    if missing:
        raise FileNotFoundError(f"보관할 결과 파일을 찾을 수 없습니다: {', '.join(missing)}")
    for source, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    if not keep_full:
        try:
            shutil.rmtree(work)
        except OSError as error:
            print(f"결과는 저장했지만 작업 폴더 정리가 완료되지 않았습니다: {error}", file=sys.stderr)


def execute_pipeline(run, *, dry_run, keep_full):
    work = run / "work"

    def step(label, commands, *, verification=False):
        print(f"\n[{label}]", flush=True)
        for command in commands:
            print(subprocess.list2cmdline(command), flush=True)
            if not dry_run:
                environment = {**os.environ, "PYTHONIOENCODING": "utf-8",
                               "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"}
                if verification:
                    log = run / "checks/verification.txt"
                    log.parent.mkdir(exist_ok=True)
                    result = subprocess.run(command, cwd=work, env=environment, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, encoding="utf-8")
                    print(result.stdout, end="", flush=True)
                    with log.open("a", encoding="utf-8") as handle:
                        handle.write(result.stdout)
                    result.check_returncode()
                else:
                    subprocess.run(command, cwd=work, check=True, env=environment)

    if not dry_run:
        work.mkdir(parents=True)
        (run / "status.txt").write_text("진행 중\n", encoding="utf-8")
        stage_inputs(work)
    for task in pipeline_tasks(work):
        step(**task)
    print("\n[09. 핵심 결과 저장 · 작업 폴더 " + ("보관]" if keep_full else "정리]"), flush=True)
    if not dry_run:
        save_results(run, keep_full=keep_full)
        (run / "status.txt").write_text("완료\n", encoding="utf-8")


def reproduce(destination, *, dry_run=False, keep_full=False):
    destination = destination.resolve()
    if any(destination.is_relative_to(ROOT / name) for name in INPUT_DIRECTORIES):
        raise ValueError("출력 폴더는 복사하는 입력·코드 폴더 밖에 두어야 합니다.")
    latest = destination / "latest"
    staging = destination / ".running"
    run = staging / "result"
    previous = staging / "previous"

    print(f"재현 결과 폴더: {latest}", flush=True)
    if dry_run:
        execute_pipeline(run, dry_run=True, keep_full=keep_full)
        print(f"결과 위치: {latest}", flush=True)
        return

    # The exclusive directory also prevents simultaneous runs from replacing each other.
    staging.mkdir(parents=True)
    published = False
    try:
        if latest.exists() or latest.is_symlink() or latest.is_junction():
            status = latest / "status.txt"
            if (not is_local_directory(latest, destination) or not status.is_file()
                    or status.read_text(encoding="utf-8").strip() != "완료"):
                raise ValueError(f"이전 재현 실행으로 확인할 수 없는 폴더입니다: {latest}")

        execute_pipeline(run, dry_run=False, keep_full=keep_full)
        try:
            if latest.exists():
                latest.rename(previous)
            run.rename(latest)
        except BaseException:
            if previous.exists() and not latest.exists():
                previous.rename(latest)
            raise
        published = True
        print(f"결과 위치: {latest}", flush=True)
        remove_numbered_runs(destination)
    finally:
        # Preserve the previous result if replacement and rollback both fail.
        if (published or not previous.exists()) and is_local_directory(staging, destination):
            shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description="로컬 원자료에서 논문 v4를 다시 계산합니다.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "reproduction")
    parser.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 명령만 표시")
    parser.add_argument("--keep-full", action="store_true", help="모델, 중간 결과와 전체 작업 폴더도 보관")
    args = parser.parse_args()
    try:
        reproduce(args.output_dir.resolve(), dry_run=args.dry_run, keep_full=args.keep_full)
    except subprocess.CalledProcessError as error:
        print(f"재현 단계 실패 (종료 코드 {error.returncode})", file=sys.stderr)
        return error.returncode or 1
    except (OSError, ValueError) as error:
        print(f"재현 실행 오류: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
