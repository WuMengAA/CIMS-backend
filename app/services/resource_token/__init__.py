"""Resource token service entry point."""

from .creator import create_token
from .resolver import resolve_token

__all__ = ["create_token", "resolve_token"]
