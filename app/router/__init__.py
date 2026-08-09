"""
Entry File for Tencent-QQ Webhook Endpoint

Author: Shanshui2024
Organization: AxT-Team
"""
from app.router.api.certificate import router as certificate_router
from app.router.api.heartbeat import router as heartbeat_router
from app.router.hooks.webhook import router as webhook_router

# 瀵煎嚭鎵€鏈夎矾鐢卞櫒
__all__ = [webhook_router, heartbeat_router, certificate_router]
