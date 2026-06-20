"""System-Routen: Startseite, Health, Version, DB-Statistik."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template

from db.language import lang_stats_rows
from ge_prime.config import APP_VERSION, GPM_VERSION, REQUIRED_API_ROUTES, ROOT, STATIC_ASSET_VERSION
from ge_prime.core import PRIME_MAP
from pipeline.normalize import (
    CIPHER_HELP,
    DIFF_HELP,
    INDEX_HELP,
    MATCHING_HELP,
    NORMALIZATION_HELP,
    TAB_GUIDE,
)


from web.handlers._repo import get_repo


def register(app: Flask, repo) -> None:
    web_dir = Path(app.root_path)

    @app.route("/api/health")
    def api_health():
        repo = get_repo()
        repo.init_db()
        rules = {r.rule for r in app.url_map.iter_rules()}
        route_flags = {
            route.removeprefix("/api/").replace("/", "_").replace("-", "_"): route in rules
            for route in REQUIRED_API_ROUTES
        }
        return jsonify(
            {
                "ok": True,
                "version": APP_VERSION,
                "gpm_version": GPM_VERSION,
                "root": str(ROOT),
                "db_path": str(repo.db_path),
                "db_words": repo.total_count(),
                "routes": route_flags,
            }
        )

    @app.route("/api/version")
    def api_version():
        template_path = web_dir / "templates" / "index.html"
        snippet = template_path.read_text(encoding="utf-8") if template_path.exists() else ""
        return jsonify(
            {
                "version": APP_VERSION,
                "gpm_version": GPM_VERSION,
                "root": str(ROOT),
                "template": str(template_path),
                "has_gpm_tab": 'data-tab="gpm"' in snippet,
                "tab_count": snippet.count('class="tab-btn'),
            }
        )

    @app.route("/api/db/stats")
    def api_db_stats():
        repo = get_repo()
        repo.init_db()
        raw_stats = repo.count_by_language()
        return jsonify(
            {
                "total_words": repo.total_count(),
                "lang_stats": [
                    {"label": label, "count": cnt}
                    for label, cnt in lang_stats_rows(raw_stats)
                ],
            }
        )

    @app.route("/")
    def index():
        repo = get_repo()
        repo.init_db()
        raw_stats = repo.count_by_language()
        lang_stats = lang_stats_rows(raw_stats)
        resp = app.make_response(
            render_template(
                "index.html",
                total_words=repo.total_count(),
                lang_stats=lang_stats,
                prime_map=sorted(PRIME_MAP.items(), key=lambda x: x[1]),
                norm_help=NORMALIZATION_HELP,
                tab_guide=TAB_GUIDE,
                match_help=MATCHING_HELP,
                diff_help=DIFF_HELP,
                index_help=INDEX_HELP,
                cipher_help=CIPHER_HELP,
                app_version=APP_VERSION,
                static_version=STATIC_ASSET_VERSION,
            )
        )
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        return resp
