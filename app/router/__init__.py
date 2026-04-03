"""
Entry File for Tencent-QQ Webhook Endpoint

Author: Shanshui2023
Organization: AxT-Team
"""
from app.router.hooks.webhook import router as webhook_router
from app.router.api.heartbeat import router as heartbeat_router

# 导出所有路由器
__all__ = [webhook_router, heartbeat_router]