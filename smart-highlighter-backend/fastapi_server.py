from __future__ import annotations
"""Compatibility shim for the FastAPI entrypoint.

The original repository used a top-level module called
``fastapi_server``. To remain compatible with existing developer
commands (and uvicorn reload import strings) we expose a thin shim
that imports the application instance from ``src.main``.
"""

from src.main import app  # re-export application (keeps old import path)

__all__ = ["app"]

if __name__ == "__main__":
    # When run directly, delegate to uvicorn via the src.main import
    import os
    import uvicorn

    use_https = os.getenv("HTTPS", "").lower() in ("1", "true", "yes")
    reload = os.getenv("RELOAD", "1") == "1"
    host = "127.0.0.1"
    port = 8443 if use_https else 8000

    cert = key = None
    if use_https:
        try:
            from certs import ensure_dev_cert

            _, cert, key = ensure_dev_cert()
        except Exception:
            cert = key = None

    if reload:
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=True,
            ssl_certfile=str(cert) if cert is not None else None,
            ssl_keyfile=str(key) if key is not None else None,
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            ssl_certfile=str(cert) if cert is not None else None,
            ssl_keyfile=str(key) if key is not None else None,
        )
        
