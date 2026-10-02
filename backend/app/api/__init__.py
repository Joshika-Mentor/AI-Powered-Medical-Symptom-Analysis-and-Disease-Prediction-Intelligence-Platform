from fastapi import APIRouter
from .auth import router as auth_router
from .medical import router as medical_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(medical_router, prefix="/medical", tags=["Medical Engine"])
