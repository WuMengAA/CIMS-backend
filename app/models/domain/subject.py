"""Pydantic definition for Subject entities.

Defines instructional subject metadata like teacher name and outdoors status.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel


class Subject(BaseModel):
    """Metadata for a single instructional subject."""

    Name: str
    Initial: str
    TeacherName: str
    IsOutDoor: bool
    AttachedObjects: Optional[Dict[str, Any]] = None
