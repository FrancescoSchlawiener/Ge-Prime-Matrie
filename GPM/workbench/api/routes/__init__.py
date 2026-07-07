"""Route registration."""

from __future__ import annotations

from api.routes import calc, cipher, code, compare, editor, jobs, size, system, tensorraum


def register_routes(app) -> None:
    app.include_router(system.router)
    app.include_router(calc.router)
    app.include_router(editor.router)
    app.include_router(compare.router)
    app.include_router(cipher.router)
    app.include_router(jobs.router)
    app.include_router(size.router)
    app.include_router(code.router)
    app.include_router(tensorraum.router)
