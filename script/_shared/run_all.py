"""Run the paper workflow in explicit, reproducible stages. See description.md."""
import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from util.execution import run_commands
from util.paths import BASELINE, ROOT, RESULTS

STAGES = {
    'preprocess': ('core.preprocess',),
    'train': ('core.train',),
    'topics': ('core.topic_quality.compare_nmf_lda', 'core.topic_quality.run_topic_stability'),
    'regimes': ('core.regimes.run_study_a', 'core.regimes.analyze_multi_regime_cases'),
    'market': ('core.market_analysis',),
    'search': ('core.search_analysis',),
    'robustness': ('core.robustness_analysis',),
    'verify': (),
    'export': ('core.export_results',),
}
PROFILES = {
    'paper': ('verify', 'export'),
    'analyses': ('topics', 'regimes', 'market', 'search', 'robustness', 'verify', 'export'),
    'train': ('preprocess', 'train'),
}


def run(stages, *, dry_run=False, output_dir=None):
    if 'train' in stages and any(s in stages for s in ('topics', 'regimes', 'market', 'search', 'robustness', 'verify', 'export')):
        raise ValueError('새 학습과 기준 논문 후속 분석은 별도 실행해야 합니다.')
    destination = Path(output_dir).resolve() if output_dir else RESULTS
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    for stage in stages:
        print(f'\n[{stage}]', flush=True)
        if stage == 'verify':
            commands = [[sys.executable, '-B', str(ROOT / 'output/paper_20261116/replication/verify_panels.py')]]
        else:
            commands = [[sys.executable, '-B', '-m', module] for module in STAGES[stage]]
            if stage == 'train':
                run_dir = destination / 'runs' / stamp
                commands[0] += ['--artifact-root', str(run_dir / 'models'), '--deliver-dir', str(run_dir / 'tables'),
                                '--excel-dir', str(run_dir / 'excel'),
                                '--rerun-dir', str(ROOT / 'data/processed/phase5_6_artifacts' / BASELINE)]
            elif stage == 'export':
                commands[0] += ['--output-dir', str(destination / 'paper')]
        run_commands(commands, dry_run=dry_run)


def main(argv=None):
    parser = argparse.ArgumentParser(description='최종 논문 실행: 기본값은 저장된 기준 결과 검산·정리입니다.')
    parser.add_argument('--profile', choices=PROFILES, default='paper',
                        help='paper: 검산·출력 / analyses: 기준 모델 후속 분석 재실행 / train: 전처리·새 학습')
    parser.add_argument('--stage', choices=STAGES, help='선택한 한 단계만 실행')
    parser.add_argument('--dry-run', action='store_true', help='계산하거나 저장하지 않고 실행 순서 표시')
    parser.add_argument('--output-dir', type=Path, help='정리 결과 또는 새 학습 결과를 저장할 상위 폴더')
    args = parser.parse_args(argv)
    stages = (args.stage,) if args.stage else PROFILES[args.profile]
    try:
        run(stages, dry_run=args.dry_run, output_dir=args.output_dir)
    except subprocess.CalledProcessError as error:
        print(f'단계 실패: 종료 코드 {error.returncode}. 후속 단계는 실행하지 않았습니다.', file=sys.stderr)
        return error.returncode or 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
