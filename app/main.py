"""
Main File for the FastAPI Application

Author: Shanshui2023
Organization: AxT-Team
"""
from fastapi import FastAPI
from app.router import __all__ as routers

app = FastAPI(
    title="AxTBot API",
    description="AxTBot Webhook Service for OpenAPI",
    version="2.1.1"
)

for i in routers:
    app.include_router(i)