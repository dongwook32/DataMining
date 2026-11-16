"""Lightweight CLI; analysis dependencies are loaded only when requested."""
import argparse
import subprocess
import sys

from .paths import ROOT


def port_number(value):
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError('port must be between 1 and 65535')
    return port


def main(argv=None):
    parser = argparse.ArgumentParser(description='DataMining research results (default: web)')
    commands = parser.add_subparsers(dest='command')
    web = commands.add_parser('web', help='Open the saved research dashboard')
    web.add_argument('--port', type=port_number, default=8090)
    web.add_argument('--no-browser', action='store_true')
    commands.add_parser('terminal', help='Print saved research results')
    commands.add_parser('summary', help='Recalculate the legacy summary CSV and charts')
    commands.add_parser('pipeline', help='Rerun the existing analysis pipeline using local data')
    commands.add_parser('rebuild-web', help='Rebuild dashboard data (requires origin/main artifacts)')
    args = parser.parse_args(argv)
    try:
        if args.command in (None, 'web'):
            from research_web.server import serve
            serve(getattr(args, 'port', 8090), open_browser=not getattr(args, 'no_browser', False))
        elif args.command == 'terminal':
            from .console import main as show
            show()
        else:
            modules = {'summary': 'datamining.summary', 'pipeline': 'analysis.run_pipeline',
                       'rebuild-web': 'research_web.build_web_data'}
            candidates = [ROOT / '.venv' / 'Scripts' / 'python.exe', ROOT / '.venv' / 'bin' / 'python']
            python = next((str(p) for p in candidates if p.is_file()), sys.executable)
            return subprocess.call([python, '-m', modules[args.command]], cwd=ROOT)
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('\nServer stopped.')
    return 0
