"""
Main File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
from fastapi import FastAPI
from app.router import __all__ as routers
from app.modules import logger

app = FastAPI(
    title="AxTBot API",
    description="AxTBot Webhook Service for OpenAPI",
    version="2.1.1"
)

for i in routers:
    app.include_router(i)
    logger.debug(f"Included router: {i}")