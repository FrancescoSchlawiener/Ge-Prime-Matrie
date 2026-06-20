"""Flask-Route-Registrierung nach API-Bereichen."""

__all__ = ["register_routes"]

from flask import Flask

from web.handlers import cipher, compare, decode, diff, encode, gpm, hierarchy, icurve, size, spectroscope, system


def register_routes(app: Flask, repo) -> None:
    system.register(app, repo)
    encode.register(app, repo)
    decode.register(app, repo)
    compare.register(app, repo)
    diff.register(app, repo)
    icurve.register(app, repo)
    hierarchy.register(app, repo)
    spectroscope.register(app, repo)
    cipher.register(app, repo)
    gpm.register(app, repo)
    size.register(app, repo)
