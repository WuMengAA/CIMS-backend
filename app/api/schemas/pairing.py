"""配对码响应模型。"""

from pydantic import BaseModel


class PairingCodeOut(BaseModel):
    """配对码响应。"""

    id: str
    code: str
    client_uid: str
    approved: bool
    used: bool
    created_at: str
