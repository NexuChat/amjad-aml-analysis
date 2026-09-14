import base64, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
USER, PASSWORD = "amjad", (ROOT / ".password").read_text().strip()
TOKEN = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)
    def _authorized(self):
        return self.headers.get("Authorization") == f"Basic {TOKEN}"
    def do_HEAD(self):
        if not self._authorized(): return self._challenge()
        super().do_HEAD()
    def do_GET(self):
        if self.path.startswith("/.") or self.path.endswith("serve.py"):
            self.send_error(404); return
        if not self._authorized(): return self._challenge()
        super().do_GET()
    def _challenge(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Amjad AML analysis", charset="UTF-8"')
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers(); self.wfile.write("Password required.\n".encode())
    def log_message(self, *a): pass

ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
