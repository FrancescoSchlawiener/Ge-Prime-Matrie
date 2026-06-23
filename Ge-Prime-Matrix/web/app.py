import sys
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from db.repository import WordRepository
from ge_prime.config import ROOT
from web.handlers import register_routes
from web.url_prefix import active_prefix

app = Flask(
    __name__,
    template_folder=str(WEB_DIR / "templates"),
    static_folder=str(WEB_DIR / "static"),
)
repo = WordRepository()

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["APP_ROOT"] = str(ROOT)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)


@app.context_processor
def _inject_url_prefix():
    return {"url_prefix": active_prefix()}


@app.after_request
def _cache_headers(response):
    from flask import request

    if request.path.startswith("/api/") or request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
    return response


@app.route("/favicon.ico")
def favicon():
    resp = app.send_static_file("favicon.svg")
    resp.headers["Content-Type"] = "image/svg+xml"
    return resp


register_routes(app, repo)


def main():
    import subprocess

    script = ROOT / "scripts" / "run_server.py"
    raise SystemExit(subprocess.call([sys.executable, str(script)]))


if __name__ == "__main__":
    main()
