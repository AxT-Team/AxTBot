"""
Certificate Management Endpoint for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.service import certificate_service

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/certificate/status")
async def certificate_status():
    state = certificate_service.get_state()
    return JSONResponse(
        content={
            "code": 200,
            "mode": state.mode,
            "reload_enabled": certificate_service.reload_enabled,
            "cert_name": certificate_service.cert_name,
        }
    )


@router.post("/certificate/reload")
async def reload_certificate(
    crt: UploadFile = File(...),
    key: UploadFile = File(...),
    cert_name: str | None = Form(default=None),
):
    if not certificate_service.reload_enabled:
        return JSONResponse(
            content={"code": 403, "message": "Certificate reload is disabled."},
            status_code=403,
        )

    cert_name = (cert_name or certificate_service.cert_name or "server").strip()

    cert_text = (await crt.read()).decode("utf-8", errors="strict").strip()
    key_text = (await key.read()).decode("utf-8", errors="strict").strip()
    if "BEGIN CERTIFICATE" not in cert_text or "BEGIN" not in key_text:
        return JSONResponse(
            content={"code": 400, "message": "Invalid certificate payload."},
            status_code=400,
        )

    try:
        certificate_service.cert_name = cert_name
        state = certificate_service.reload_from_payload(cert_text, key_text)
    except Exception as exc:
        return JSONResponse(
            content={"code": 400, "message": f"Reload failed: {exc}"},
            status_code=400,
        )

    return JSONResponse(
        content={
            "code": 200,
            "message": "Certificate reloaded.",
            "mode": state.mode,
            "fingerprint": state.fingerprint,
        }
    )
