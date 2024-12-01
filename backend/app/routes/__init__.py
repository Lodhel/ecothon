from fastapi import APIRouter

from backend.app.routes.green_plant_records.green_plant_records_router import green_plant_records_router
from backend.app.routes.user.user_router import user_router

router = APIRouter()
router.include_router(user_router)
router.include_router(green_plant_records_router)

__all__ = ["router"]
