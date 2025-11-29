"""v1 API package.

Expose the FastAPI `app` object at `app.api.v1.app` so code like
`from app.api.v1 import app` works (main.py expects this).
"""

from ..api import app

__all__ = ("app",)
