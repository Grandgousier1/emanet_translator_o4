"""Helpers to enable remote debugging with debugpy."""
from __future__ import annotations

import debugpy


def start(port: int = 5678) -> None:
    """Start a debugpy server and wait for a client to attach."""
    debugpy.listen(("0.0.0.0", port))
    print(f"debugpy listening on {port}; waiting for client...", flush=True)
    debugpy.wait_for_client()
