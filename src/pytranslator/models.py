"""Shared models, constants, and configuration for offline translation."""

from pathlib import Path

# ==============================
# Cache Paths
# ==============================

def _default_cache_dir() -> Path:
    """Build and create the default translator cache directory in home."""
    path = Path.home() / f".cache" / "pytranslator"
    path.mkdir(parents=True, exist_ok=True)
    return path


DEFAULT_CACHE = _default_cache_dir()
