"""
Certificate Service for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from __future__ import annotations

import hashlib
import os
import ssl
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional

from app.modules import logger


@dataclass
class CertificateState:
    mode: str
    cert_path: Optional[Path] = None
    key_path: Optional[Path] = None
    fingerprint: Optional[str] = None


class CertificateService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.lock = Lock()
        self.reload_enabled = self._env_bool("FRAMEWORK_CERT_RELOAD_ENABLED", False)
        self.cert_name = os.getenv("FRAMEWORK_CERT_NAME", "").strip()
        self.cert_path: Optional[Path] = None
        self.key_path: Optional[Path] = None
        self._state = CertificateState(mode="http")
        self.refresh()

    def _env_bool(self, key: str, default: bool = False) -> bool:
        raw = os.getenv(key)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    def _valid_cert_pair(self, cert_path: Path, key_path: Path) -> bool:
        if not cert_path.exists() or not key_path.exists():
            return False
        try:
            ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(str(cert_path), str(key_path))
            return True
        except Exception as exc:
            logger.warning(f"证书服务 >>> 证书校验失败: {exc}")
            return False

    def _fingerprint(self, cert_path: Path, key_path: Path) -> str:
        digest = hashlib.sha256()
        digest.update(cert_path.read_bytes())
        digest.update(key_path.read_bytes())
        return digest.hexdigest()

    def _discover_certificate_pair(self) -> tuple[Optional[Path], Optional[Path]]:
        if self.cert_name:
            cert_path = self.data_dir / f"{self.cert_name}.crt"
            key_path = self.data_dir / f"{self.cert_name}.key"
            return cert_path, key_path

        for cert_path in sorted(self.data_dir.glob("*.crt")):
            key_path = cert_path.with_suffix(".key")
            if key_path.exists():
                return cert_path, key_path
        return None, None

    def refresh(self) -> CertificateState:
        with self.lock:
            self.reload_enabled = self._env_bool("FRAMEWORK_CERT_RELOAD_ENABLED", self.reload_enabled)
            self.cert_name = os.getenv("FRAMEWORK_CERT_NAME", self.cert_name).strip()
            self.data_dir.mkdir(parents=True, exist_ok=True)
            cert_path, key_path = self._discover_certificate_pair()
            self.cert_path = cert_path
            self.key_path = key_path

            if cert_path and key_path and self._valid_cert_pair(cert_path, key_path):
                self._state = CertificateState(
                    mode="https",
                    cert_path=cert_path,
                    key_path=key_path,
                    fingerprint=self._fingerprint(cert_path, key_path),
                )
                logger.info(f"证书服务 >>> 已启用 HTTPS 模式: {cert_path.name}, {key_path.name}")
            else:
                self._state = CertificateState(mode="http")
                logger.info("证书服务 >>> 未找到可用证书，已回退到 HTTP 模式")
            return self._state

    def get_state(self) -> CertificateState:
        with self.lock:
            return self._state

    def get_uvicorn_kwargs(self) -> dict:
        state = self.get_state()
        if state.mode != "https" or not state.cert_path or not state.key_path:
            return {}
        return {"ssl_certfile": str(state.cert_path), "ssl_keyfile": str(state.key_path)}

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        state = self.get_state()
        if state.mode != "https" or not state.cert_path or not state.key_path:
            return None
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(state.cert_path), str(state.key_path))
        return context

    def reload_from_payload(self, cert_pem: str, key_pem: str) -> CertificateState:
        if not self.reload_enabled:
            raise PermissionError("Certificate reload is disabled.")

        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.cert_name:
            self.cert_path = self.data_dir / f"{self.cert_name}.crt"
            self.key_path = self.data_dir / f"{self.cert_name}.key"
        else:
            self.cert_name = "server"
            self.cert_path = self.data_dir / "server.crt"
            self.key_path = self.data_dir / "server.key"
        self.cert_path.write_text(cert_pem, encoding="utf-8")
        self.key_path.write_text(key_pem, encoding="utf-8")
        if not self._valid_cert_pair(self.cert_path, self.key_path):
            raise ValueError("Provided certificate files are invalid.")
        return self.refresh()


certificate_service = CertificateService()
