"""
Entry File for Tencent-QQ Webhook Endpoint

Author: Shanshui2024
Organization: AxT-Team
"""
from .hooks.webhook import router as webhook_router
from .api.heartbeat import router as heartbeat_router

# 导出所有路由器
__all__ = ["webhook_router", "heartbeat_router"]