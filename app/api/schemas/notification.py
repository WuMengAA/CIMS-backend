"""Remote notification payload definition.

Detailed options for triggering on-screen notifications on client devices.
"""

from pydantic import BaseModel


class NotificationPayload(BaseModel):
    """Structured data for a broadcast message."""

    MessageMask: str = ""
    MessageContent: str = ""
    OverlayIconLeft: int = 0
    OverlayIconRight: int = 0
    IsEmergency: bool = False
    IsSpeechEnabled: bool = False
    IsEffectEnabled: bool = False
    IsSoundEnabled: bool = False
    IsTopmost: bool = False
    DurationSeconds: float = 5.0
    RepeatCounts: int = 1
