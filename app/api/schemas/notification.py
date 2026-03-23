"""远程通知负载定义。

触发客户端设备屏幕通知的详细选项。
"""

from pydantic import BaseModel, Field


class NotificationPayload(BaseModel):
    """广播消息的结构化数据。"""

    MessageMask: str = Field(default="", max_length=4096)
    MessageContent: str = Field(default="", max_length=4096)
    OverlayIconLeft: int = Field(default=0, ge=0)
    OverlayIconRight: int = Field(default=0, ge=0)
    IsEmergency: bool = False
    IsSpeechEnabled: bool = False
    IsEffectEnabled: bool = False
    IsSoundEnabled: bool = False
    IsTopmost: bool = False
    DurationSeconds: float = Field(default=5.0, ge=0, le=3600)
    RepeatCounts: int = Field(default=1, ge=0, le=100)
