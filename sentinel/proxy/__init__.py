"""
Sentinel Proxy — Cloudflare for AI.
"""

from .config import ProxyConfig


def create_app(config=None):
    from .server import create_app as _create_app

    return _create_app(config)


def run(host: str = "0.0.0.0", port: int = 8741):
    from .server import run as _run

    return _run(host=host, port=port)


__all__ = ["create_app", "run", "ProxyConfig"]
