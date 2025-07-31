"""Helpers to enable remote debugging with debugpy."""

from __future__ import annotations

import debugpy


def start(port: int = 5678) -> None:
    """Start a debugpy server without blocking."""
    debugpy.listen(("0.0.0.0", port))
    print(f"debugpy listening on {port}; attach your debugger.", flush=True)
