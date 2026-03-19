"""Pydantic definition for ClassIsland time recurrence rules.

Specifies weekday patterns and count-based divisions for automatic scheduling.
"""

from pydantic import BaseModel


class TimeRule(BaseModel):
    """Configuration for when a class schedule repeats."""

    WeekDay: int
    WeekCountDiv: int
    WeekCountDivTotal: int
