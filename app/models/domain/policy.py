"""Pydantic definition for ManagementPolicy entities.

Stores permission restrictions for client devices (e.g. disabling editing).
"""

from pydantic import BaseModel


class ManagementPolicy(BaseModel):
    """Enforceable restrictions for the management server client."""

    DisableProfileEditing: bool
    DisableProfileClassPlanEditing: bool
    DisableProfileTimeLayoutEditing: bool
    DisableProfileSubjectsEditing: bool
    DisableSettingsEditing: bool
    DisableSplashCustomize: bool
    DisableDebugMenu: bool
    AllowExitManagement: bool
    DisableEasterEggs: bool
