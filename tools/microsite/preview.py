#!/usr/bin/env python3
"""Private loopback preview; noindex headers are never part of deployable HTML."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
class Preview(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('X-Robots-Tag', 'noindex, nofollow')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()
root=Path(__file__).resolve().parents[2]
server=ThreadingHTTPServer(('127.0.0.1',4173),partial(Preview,directory=str(root)))
print('Private preview: http://127.0.0.1:4173/chance-darts/',flush=True)
server.serve_forever()
