"""Recompute the submitted v4 analysis in an isolated run directory."""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "RUN_PHASE5_6_20261027_184959"
PAPER_SUPPORT = Path("output/paper_20261116/replication")
LEGACY_PANEL = Path("data/processed/regimes/regime_monthly.csv")
MODEL_ROOT = Path("data/processed/phase5_6_artifacts")
REACTIONS = Path("data/processed/reactions")
INPUT_DIRECTORIES = ("script", "results/docs", "data/raw")

FOLLOWUP = (
    ("다중 국면과 사례", ("core.regimes.run_study_a", "core.regimes.analyze_multi_regime_cases")),
    ("시장 반응과 경보", ("core.market_analysis",)),
    ("주별 뉴스·검색", ("core.search_analysis",)),
    ("토픽 품질과 반복 안정성", ("core.topic_quality.compare_nmf_lda", "core.topic_quality.run_topic_stability")),
    ("강건성, 수렴 및 후속 민감도", ("core.robustness_analysis",)),
)


def stage_inputs(work):
    source = ROOT / "script"
    copies = [
        (ROOT / "data/raw", work / "data/raw"),
        (ROOT / "results/docs", work / "docs"),
        (ROOT / LEGACY_PANEL, work / LEGACY_PANEL),
        (source / "01_collect/collector", work / "collector"),
        (source / "_shared/config", work / "config"),
        (source / "_shared/util", work / "util"),
        (source / "_shared/__init__.py", work / "core/__init__.py"),
        (source / "_shared/v4.py", work / "core/v4.py"),
        (source / "run_all.py", work / "core/reproduce.py"),
    ]
    # Preserve the research modules' import names and audit paths inside each run.
    audit_scripts = {"audit_s1.py", "verify_panels.py"}
    for folder in ("02_preprocess", "03_embed", "04_cluster", "05_validate", "06_analyze"):
        for item in sorted((source / folder).iterdir()):
            if item.name == "__pycache__":
                continue
            relative = PAPER_SUPPORT if item.name in audit_scripts else Path("core")
            copies.append((item, work / relative / item.name))
    for item, target in copies:
        target.parent.mkdir(parents=True, exist_ok=True)
        if item.is_dir():
            shutil.copytree(item, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(item, target)


def reproduce(destination, *, dry_run=False):
    if any(destination.is_relative_to(ROOT / name) for name in INPUT_DIRECTORIES):
        raise ValueError("출력 폴더는 복사하는 입력·코드 폴더 밖에 두어야 합니다.")
    run = destination / datetime.now().strftime("RUN_%Y%m%d_%H%M%S_%f")
    work = run / "work"

    def step(label, commands):
        print(f"\n[{label}]", flush=True)
        for command in commands:
            print(subprocess.list2cmdline(command), flush=True)
            if not dry_run:
                subprocess.run(command, cwd=work, check=True,
                               env={**os.environ, "PYTHONIOENCODING": "utf-8",
                                    "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUNBUFFERED": "1"})

    def module(name, *args):
        return [sys.executable, "-B", "-m", name, *map(str, args)]

    print(f"재현 실행 폴더: {run}", flush=True)
    if not dry_run:
        work.mkdir(parents=True)
        (run / "상태.txt").write_text("진행 중\n", encoding="utf-8")
    try:
        if not dry_run:
            stage_inputs(work)
        step("원자료 전처리", [module("core.preprocess")])
        step("TF-IDF·NMF 재학습, 국면, 예측", [module("core.train")])
        if not dry_run:
            audit = work / REACTIONS / "phase5_6_pipeline_audit.json"
            run_id = json.loads(audit.read_text(encoding="utf-8"))["run_id"]
            # The historical follow-up modules expect this directory name.
            # Its contents come exclusively from the model trained above.
            shutil.copytree(work / MODEL_ROOT / run_id, work / MODEL_ROOT / BASELINE)
        for label, modules in FOLLOWUP:
            step(label, [module(name) for name in modules])
        step("원자료·논문 주요 수치 검산", [
            [sys.executable, "-B", str(PAPER_SUPPORT / name)] for name in ("audit_s1.py", "verify_panels.py")
        ])
        step("이번 실행의 단계별 엑셀 저장", [module("core.reproduction_excel", run)])
    except BaseException:
        if not dry_run:
            (run / "상태.txt").write_text("실패 또는 중단\n", encoding="utf-8")
        raise
    if not dry_run:
        (run / "상태.txt").write_text("완료\n", encoding="utf-8")
    print(f"결과 위치: {run}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="로컬 원자료에서 논문 v4를 다시 계산해 엑셀로 저장합니다.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "reproduction")
    parser.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 명령만 표시")
    args = parser.parse_args()
    try:
        reproduce(args.output_dir.resolve(), dry_run=args.dry_run)
    except subprocess.CalledProcessError as error:
        print(f"재현 단계 실패 (종료 코드 {error.returncode})", file=sys.stderr)
        return error.returncode or 1
    except (OSError, ValueError) as error:
        print(f"재현 실행 오류: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
