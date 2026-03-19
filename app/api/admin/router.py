"""Admin API composite router.

Registers all administrative sub-modules into a single
top-level router for the admin application.
"""

from fastapi import APIRouter
from .auth_routes import router as auth_router
from .tenant_crud import router as crud_router
from .tenant_detail import router as detail_router
from .tenant_actions import router as action_router
from .tenant_token import router as token_router

router = APIRouter()

# Authentication sub-routes
router.include_router(auth_router, prefix="/auth")

# Tenant CRUD and Actions
router.include_router(crud_router, prefix="/tenants")
router.include_router(detail_router, prefix="/tenants")
router.include_router(action_router, prefix="/tenants")
router.include_router(token_router, prefix="/tenants")
