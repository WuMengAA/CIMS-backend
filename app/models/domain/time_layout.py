"""Pydantic definition for TimeLayout entities.

Defines the chronological structure of a school day (start/end times).
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class TimeLayoutItem(BaseModel):
    """A singular time block within a daily layout (e.g., Lesson 1)."""

    StartSecond: str
    EndSecond: str
    TimeType: int
    IsHideDefault: bool
    DefaultClassId: str
    BreakName: str
    ActionSet: Optional[Dict[str, Any]] = None
    AttachedObjects: Optional[Dict[str, Any]] = None


class TimeLayout(BaseModel):
    """Daily schedule structure containing multiple time blocks."""

    Name: str
    Layouts: List[TimeLayoutItem]
    AttachedObjects: Optional[Dict[str, Any]] = None
