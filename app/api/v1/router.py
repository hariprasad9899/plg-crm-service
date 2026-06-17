from fastapi import APIRouter
from .auth import router as auth_router
from .tenant import router as tenant_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(tenant_router)