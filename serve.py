"""Serve Claudy Day on localhost, open it, and hand it your live Claude Code stats.

    python serve.py [port] [--no-open]

Serves this folder, plus /stats-cache.json read fresh from ~/.claude (or $CLAUDE_CONFIG_DIR)
on every request, trimmed to the per-model token counts the page draws. Nothing else from
~/.claude is reachable, and it listens on 127.0.0.1 only.
"""
import http.server
import json
import os
import pathlib
import sys
import threading
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG = pathlib.Path(os.environ.get('CLAUDE_CONFIG_DIR') or pathlib.Path.home() / '.claude')
STATS = CONFIG / 'stats-cache.json'


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.split('?', 1)[0] != '/stats-cache.json':
            return super().do_GET()
        try:
            stats = json.loads(STATS.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return self.send_error(404, f'No readable stats file at {STATS}')
        body = json.dumps({k: stats.get(k) for k in ('lastComputedDate', 'modelUsage')}).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    port = int(args[0]) if args else 8765
    url = f'http://localhost:{port}/'
    should_open = '--no-open' not in sys.argv
    try:
        server = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
    except OSError:  # already running (e.g. launched twice): just show it
        print(f'Port {port} is busy; assuming Claudy Day is already running at {url}')
        if should_open:
            webbrowser.open(url)
        sys.exit(0)
    print(f'Claudy Day on {url}  (stats: {STATS})')
    if should_open:
        threading.Timer(0.3, webbrowser.open, (url,)).start()
    server.serve_forever()
