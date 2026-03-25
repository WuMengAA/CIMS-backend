"""账户模型输出辅助。"""

from app.api.schemas.account_out import AccountOut


def _out(acct) -> AccountOut:
    """将 Account 模型转换为响应模型。"""
    return AccountOut(
        id=acct.id,
        name=acct.name,
        slug=acct.slug,
        api_key=acct.api_key,
        is_active=acct.is_active,
        created_at=str(acct.created_at),
    )
