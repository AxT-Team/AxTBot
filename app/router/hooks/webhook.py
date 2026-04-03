"""
Tencent-QQ Webhook Endpoint for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.classes import BasePayload, ValidationEvent
from app.service import service_validation
from app.service import service_validation_msg

router = APIRouter(prefix="/webhook", tags=["Webhook"])
@router.get("")
async def webhook():
    """
    GET方式请求该接口会返回405错误，提示使用POST方式发送Webhook事件
    """
    return JSONResponse(
        content={"code": 405, "message": "This endpoint is for POST requests only. Please use POST to send webhook events."}, 
        status_code=405
    )

@router.post("")
async def webhook(request: Request):
    """
    POST方式请求该接口会处理Webhook事件，并返回事件数据
    """
    try:
        body = await request.body()
        payload = await request.json()
        payload = BasePayload(**payload)
        if payload.op == 13:
            validate = ValidationEvent(**payload.d)
            plain_token, signature = await service_validation(validate, request.headers, body)
            if plain_token and signature:
                return JSONResponse(
                    content={"plain_token": plain_token, "signature": signature},
                    status_code=200
                )
        elif payload.op == 0:
            result = await service_validation_msg(request.headers, body)
            if result:
                # Just give me a second to verify this code....
                return JSONResponse(
                    content={"op_code": 12, "d": {"event_id": payload.id, "status": 0, "message": "success"}},
                    status_code=200
                )

    except Exception as e:
        raise e