"""
Main File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
from fastapi import FastAPI
from .router import webhook_router, heartbeat_router

app = FastAPI(
    title="AxTBot API",
    description="AxTBot Webhook Service for Tencent-QQ",
    version="1.0.0"
)
app.include_router(webhook_router)
app.include_router(heartbeat_router)