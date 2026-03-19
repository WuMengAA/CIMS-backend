"""Pydantic definition for ClassPlan entities.

Contains the full structure of a class timetable, including
active rules and content overrides.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from .time_rule import TimeRule
from .class_info import ClassInfo


class ClassPlan(BaseModel):
    """The master configuration for a single timetable."""

    TimeLayoutId: str
    TimeRule: TimeRule
    Classes: List[ClassInfo]
    Name: str
    IsOverlay: bool
    OverlaySourceId: Optional[str] = None
    OverlaySetupTime: datetime
    IsEnabled: bool
    AssociatedGroup: str
    AttachedObjects: Optional[Dict[str, Any]] = None
