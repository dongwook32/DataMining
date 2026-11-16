"""Serve the dashboard locally without exposing the rest of the repository."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser

WEB_DIR = Path(__file__).resolve().parent


class QuietHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def serve(port=8090, *, open_browser=False):
    for relative in ('index.html', 'data/research_data.js', 'data/research_data.json'):
        if not (WEB_DIR / relative).is_file():
            raise FileNotFoundError(f'Missing dashboard file: {relative}. Run python run.py rebuild-web.')
    handler = partial(QuietHandler, directory=str(WEB_DIR))
    with ThreadingHTTPServer(('127.0.0.1', port), handler) as server:
        url = f'http://127.0.0.1:{server.server_port}'
        print(f'Research dashboard: {url}\nStop: Ctrl+C', flush=True)
        if open_browser:
            webbrowser.open(url)
        server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, default=8090)
    try:
        serve(parser.parse_args().port)
    except KeyboardInterrupt:
        pass
