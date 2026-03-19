"""Pydantic definition for class item metadata.

Describes the relationship between a class interval and its subject content.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class ClassInfo(BaseModel):
    """Specific content mapping for a scheduled class slot."""

    SubjectId: str
    IsChangedClass: bool
    AttachedObjects: Optional[Dict[str, Any]] = None
