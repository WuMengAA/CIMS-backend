"""Authentication service entry point.

Simplified imports for token lifecycle management.
"""

from .generator import generate_token
from .validator import validate_and_refresh
from .revoker import revoke_token

__all__ = ["generate_token", "validate_and_refresh", "revoke_token"]
