from fastapi import APIRouter, Depends

from src.dependencies.auth import get_current_user
from src.routers.private import server as private_server
from src.routers.public import server as public_server

router = APIRouter()

router.include_router(public_server.router, prefix="/public")
router.include_router(private_server.router, prefix="/private", dependencies=[Depends(get_current_user)])
