from fastapi import APIRouter, Depends

from server.core.fastapi.dependencies.authentication import AuthenticationRequired

health_router = APIRouter()


@health_router.get("/health", dependencies=[Depends(AuthenticationRequired)])
def health_check():
    """返回服务存活状态"""
    return {"status": "ok"}
