"""Client API composite router.

Aggregates manifest discovery and resource access endpoints
for the main Client API application.
"""

from fastapi import APIRouter
from .manifest import router as manifest_router
from .resource import router as resource_router

router = APIRouter()

router.include_router(manifest_router)
router.include_router(resource_router)
