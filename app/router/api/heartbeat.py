"""
Server HeartBeat Endpoint for AxTBot

Author: Shanshui2023
Organization: AxT-Team
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["API"])
@router.get("/heartbeat")
async def heartbeat():
    """
    GET方式请求心跳接口会有相关回包，可用于确保框架是否在线
    """
    return JSONResponse(
        content={"code": 200, "message": "I'm here~"}
    )