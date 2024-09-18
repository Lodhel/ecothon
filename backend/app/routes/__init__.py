from fastapi import APIRouter

from backend.app.routes.user.user_router import user_router

router = APIRouter()
router.include_router(user_router)

__all__ = ["router"]
