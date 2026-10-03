from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class SiteHandler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)

        try:
            body = (Path(self.directory) / "404.html").read_bytes()
        except OSError:
            return super().send_error(code, message, explain)

        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if self.command != "HEAD":
            self.wfile.write(body)


if __name__ == "__main__":
    docs = Path(__file__).parent / "docs"
    handler = partial(SiteHandler, directory=str(docs))

    with ThreadingHTTPServer(("127.0.0.1", 8000), handler) as server:
        print("Serving at http://127.0.0.1:8000")
        server.serve_forever()