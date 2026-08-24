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

# ── 插件路由注册（供插件挂载管理面板等额外路由）──
plugin_routers: list = []


def register_plugin_router(router) -> None:
    """插件调用此函数，将自身的 APIRouter 注册到主应用中。"""
    plugin_routers.append(router)
    try:
        from app.modules import logger

        logger.debug(f"FastAPI >>> 插件注册路由: {getattr(router, 'prefix', '') or '/'}")
    except Exception:
        pass
