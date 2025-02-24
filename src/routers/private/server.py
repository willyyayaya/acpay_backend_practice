from fastapi import APIRouter

from src.routers.private import auth

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
