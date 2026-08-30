"""
Rich Media Upload Service for QQ Bot

Author: Shanshui2024
Organization: AxT-Team

设计目标（面向插件开发者）：
  把本地/网络图片上传到 QQ 远端，拿到平台托管的可访问链接（raw_url），
  并按「来源」缓存到数据库（带 TTL），后续直接复用链接嵌入 Markdown 发送，
  避免每次重复上传。

两种底层上传方式（详见官方文档「富媒体消息概述」）：
  - URL 上传      ：传入公网可访问的 URL，平台自动下载转存（仅返回 file_info，无 raw_url）
  - 本地分片上传  ：upload_prepare -> 预签名 PUT -> upload_part_finish -> files 合并
                    （图片/视频/语音会额外返回 raw_url，即 COS 预签名 GET 链接）

为稳定拿到可嵌入 Markdown 的 raw_url，upload_image_link 统一走「分片上传」路径：
  - 本地文件：直接读字节分片上传
  - 网络图片：先下载字节，再分片上传

单聊与群聊文件相互隔离，请分别使用 scene="user" / scene="group"。

参考文档：
  https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/rich-media.html
"""
from __future__ import annotations

import hashlib
import io
import time
from pathlib import Path
from typing import Optional, Union

import aiohttp

from app.modules import logger

API_BASE = "https://api.bot.qq.com"

# 分片大小兜底（服务端未返回 block_size 时使用，默认 5MB）
DEFAULT_BLOCK_SIZE = 5 * 1024 * 1024
# 计算 md5_10m 所需的文件头部字节数（约 10MB，官方取值 10002432）
MD5_10M_HEAD = 10002432
# ttl 为 0 时（长期有效）的兜底过期时间：10 年
FOREVER = 10 * 365 * 24 * 3600


def _headers() -> dict:
    from app.service.qq_service.AccessToken import accesstoken

    return {
        "Authorization": f"QQBot {accesstoken.access_token}",
        "Content-Type": "application/json",
    }


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def _guess_file_type(name: str, file_type: Optional[int]) -> int:
    if file_type is not None:
        return file_type
    lower = name.lower()
    if lower.endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
        return 1
    if lower.endswith(".mp4"):
        return 2
    if lower.endswith(".silk"):
        return 3
    return 4


def _is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def _sniff_file_type(data: bytes, name: str, file_type: Optional[int]) -> int:
    """
    优先用调用方指定的 file_type；否则按文件头魔数推断真实类型，
    再退化为按扩展名推断。这样能避免「内容是 gif 却按 png 上传」导致的
    850019 富媒体格式不支持。
    """
    if file_type is not None:
        return file_type
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return 1
    if data[:3] == b"\xff\xd8\xff":
        return 1
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return 1
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return 1
    if data[:2] == b"BM":
        return 1
    if data[:4] == b"%PDF":
        return 4
    if data[:4] == b"ID3" or data[:2] == b"\xff\xfb" or data[:4] == b"Ogg ":
        return 3
    if data[:4] == b"ftyp":
        return 2
    return _guess_file_type(name, None)


def _normalize_file_name(name: str, ftype: int) -> str:
    """根据真实类型把文件名后缀矫正为平台可识别的扩展名。"""
    known_img = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
    low = name.lower()
    if ftype == 1 and low.endswith(known_img):
        return name
    if ftype == 2 and low.endswith(".mp4"):
        return name
    if ftype == 3 and low.endswith(".silk"):
        return name
    ext = {1: ".png", 2: ".mp4", 3: ".silk", 4: ""}.get(ftype, "")
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return stem + ext


def _is_supported_image(data: bytes) -> bool:
    """QQ 图片上传（file_type=1）支持的图片格式：png/jpg/gif/webp/bmp（gif 保留动图）。"""
    return (
        data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:3] == b"\xff\xd8\xff"
        or data[:6] in (b"GIF87a", b"GIF89a")
        or (data[:4] == b"RIFF" and data[8:12] == b"WEBP")
        or data[:2] == b"BM"
    )


def _image_ext(data: bytes) -> str:
    """按真实图片格式返回对应扩展名。"""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    if data[:2] == b"BM":
        return ".bmp"
    return ".png"


def _ensure_png(data: bytes) -> bytes:
    """
    仅当图片格式 QQ 不支持时才转 PNG（如 tiff/heic 等）。
    png/jpg/gif/webp/bmp 受支持，原样返回（gif 保留动图）。
    """
    if _is_supported_image(data):
        return data
    try:
        from PIL import Image
    except ImportError:
        logger.error("上传 >>> 需要 Pillow 来转换非 png/jpg 图片，请执行: uv pip install pillow")
        return data
    try:
        img = Image.open(io.BytesIO(data))
        img = img.convert("RGBA") if img.mode in ("P", "RGBA", "LA") else img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception as e:
        logger.error(f"上传 >>> 图片转换 PNG 失败: {e}")
        return data


def _cache_media(source: str, url: str, ttl: int, file_info: "str | None") -> None:
    """把分片上传拿到的 raw_url 写入缓存表（带 TTL），供后续复用。"""
    try:
        import time

        from app.modules import get_db

        db = get_db()
        now = int(time.time())
        expire = now + (ttl if ttl and ttl > 0 else 10 * 365 * 24 * 3600)
        db.add_cached_media(
            source=source,
            url=url,
            file_info=file_info,
            ttl=ttl,
            create_time=str(now),
            expire_time=str(expire),
        )
    except Exception as e:
        logger.warning(f"上传 >>> 写入媒体缓存失败（不影响本次发送）: {e}")


def _filename_from_url(url: str) -> str:
    last = url.split("?")[0].rstrip("/").split("/")[-1]
    return last or "upload.bin"


async def _download(url: str) -> Optional[bytes]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                if resp.status != 200:
                    logger.error(f"上传 >>> 下载源文件失败 HTTP {resp.status}: {url}")
                    return None
                return await resp.read()
    except Exception as e:
        logger.error(f"上传 >>> 下载源文件异常: {e}")
        return None


async def upload_by_url(
    openid: str,
    scene: str,
    url: str,
    file_type: int = 1,
    file_name: Optional[str] = None,
) -> Optional[str]:
    """
    URL 上传：平台下载并转存，返回 file_info（不含 raw_url）。
    """
    endpoint = "users" if scene == "user" else "groups"
    api = f"{API_BASE}/v2/{endpoint}/{openid}/files"
    payload: dict = {"file_type": file_type, "url": url, "srv_send_msg": False}
    if file_name:
        payload["file_name"] = file_name
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(api, json=payload, headers=_headers(), timeout=10) as resp:
                data = await resp.json()
                if resp.status == 200 and data.get("file_info"):
                    logger.debug(f"上传 >>> URL 上传成功: {file_name or url}")
                    return data["file_info"]
                logger.error(f"上传 >>> URL 上传失败 HTTP {resp.status}: {data}")
                return None
    except Exception as e:
        logger.error(f"上传 >>> URL 上传异常: {e}")
        return None


async def _put_part(presigned_url: str, chunk: bytes) -> bool:
    """将单个分片 PUT 到预签名 URL。"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(presigned_url, data=chunk, timeout=30) as resp:
                return resp.status < 400
    except Exception as e:
        logger.error(f"上传 >>> 分片 PUT 失败: {e}")
        return False


async def _do_chunked_upload(
    openid: str,
    scene: str,
    data: bytes,
    file_type: int,
    file_name: str,
) -> Optional[dict]:
    """
    分片上传完整流程，返回 files 接口的完整响应 dict（含 file_info / raw_url / ttl）。
    """
    file_size = len(data)
    md5 = _md5(data)
    sha1 = _sha1(data)
    md5_10m = _md5(data[:MD5_10M_HEAD])

    endpoint = "users" if scene == "user" else "groups"
    prepare_api = f"{API_BASE}/v2/{endpoint}/{openid}/upload_prepare"
    prepare_payload = {
        "file_type": file_type,
        "file_size": str(file_size),
        "file_name": file_name,
        "md5": md5,
        "sha1": sha1,
        "md5_10m": md5_10m,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(prepare_api, json=prepare_payload, headers=_headers(), timeout=10) as resp:
                prep = await resp.json()
                if resp.status != 200 or "upload_id" not in prep:
                    logger.error(f"上传 >>> 预上传失败 HTTP {resp.status}: {prep}")
                    return None
                upload_id = prep["upload_id"]
                block_size = int(prep.get("block_size", DEFAULT_BLOCK_SIZE))
                parts = prep.get("parts", [])
    except Exception as e:
        logger.error(f"上传 >>> 预上传异常: {e}")
        return None

    # 逐片 PUT 到预签名 URL，并通知服务端该分片完成
    # 注意：QQ 返回的 parts[].index 是 1-based，切片需用 (index-1) 作偏移
    for part in parts:
        idx = part["index"]
        presigned = part["presigned_url"]
        start = (idx - 1) * block_size
        chunk = data[start: start + block_size]
        if not await _put_part(presigned, chunk):
            logger.error(f"上传 >>> 分片 {idx} 上传失败，终止")
            return None
        finish_api = f"{API_BASE}/v2/{endpoint}/{openid}/upload_part_finish"
        finish_payload = {
            "upload_id": upload_id,
            "part_index": idx,
            "block_size": str(len(chunk)),
            "md5": _md5(chunk),
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(finish_api, json=finish_payload, headers=_headers(), timeout=10) as resp:
                    if resp.status >= 400:
                        txt = await resp.text()
                        logger.error(f"上传 >>> 分片 {idx} 完成通知失败 HTTP {resp.status}: {txt}")
                        return None
        except Exception as e:
            logger.error(f"上传 >>> 分片 {idx} 完成通知异常: {e}")
            return None

    # 全部分片完成后合并，返回 file_info / raw_url / ttl
    files_api = f"{API_BASE}/v2/{endpoint}/{openid}/files"
    final_payload = {
        "file_type": file_type,
        "srv_send_msg": False,
        "file_name": file_name,
        "upload_id": upload_id,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(files_api, json=final_payload, headers=_headers(), timeout=10) as resp:
                result = await resp.json()
                if resp.status == 200 and result.get("file_info"):
                    logger.debug(f"上传 >>> 本地分片上传成功: {file_name}")
                    return result
                logger.error(f"上传 >>> 合并失败 HTTP {resp.status}: {result}")
                return None
    except Exception as e:
        logger.error(f"上传 >>> 合并异常: {e}")
        return None


async def upload_local(
    openid: str,
    scene: str,
    file_path: Union[str, Path],
    file_type: Optional[int] = None,
    file_name: Optional[str] = None,
) -> Optional[str]:
    """本地文件分片上传，返回 file_info（不含缓存）。"""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"上传 >>> 本地文件不存在: {path}")
        return None
    data = path.read_bytes()
    ftype = _sniff_file_type(data, file_name or path.name, file_type)
    if ftype == 1:
        if _is_supported_image(data):
            # png/jpg/gif/webp/bmp 受支持，原样上传（gif 保留动图），仅矫正扩展名
            fname = Path(file_name or path.name).with_suffix(_image_ext(data)).name
        else:
            data = _ensure_png(data)
            fname = Path(file_name or path.name).with_suffix(".png").name
    else:
        fname = _normalize_file_name(file_name or path.name, ftype)
    result = await _do_chunked_upload(openid, scene, data, ftype, fname)
    if result and result.get("raw_url"):
        _cache_media(str(file_path), result["raw_url"], int(result.get("ttl", 0) or 0), result.get("file_info"))
    return result["file_info"] if result else None


async def upload_media(
    openid: str,
    scene: str,
    source: Union[str, Path],
    file_type: Optional[int] = None,
    file_name: Optional[str] = None,
) -> Optional[str]:
    """
    统一富媒体上传入口，返回 file_info（用于直接发送 msg_type=7 富媒体消息）。

    Args:
        openid   : 单聊用户 OpenID 或 群 OpenID
        scene    : "user"（单聊）或 "group"（群聊），二者文件相互隔离
        source   : 图片/视频/文件来源
                   - http(s) 开头            → URL 上传
                   - 本地存在的路径(str/Path) → 分片上传
        file_type: 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
        file_name: 可选文件名

    Returns:
        file_info 字符串，失败返回 None
    """
    if isinstance(source, Path) or (
        isinstance(source, str) and not _is_url(source) and Path(source).exists()
    ):
        return await upload_local(openid, scene, source, file_type=file_type, file_name=file_name)
    if isinstance(source, str) and _is_url(source):
        return await upload_by_url(openid, scene, source, file_type=file_type, file_name=file_name)
    logger.warning(f"上传 >>> 无法识别的来源类型，尝试按 URL 处理: {source}")
    return await upload_by_url(openid, scene, str(source), file_type=file_type, file_name=file_name)


async def upload_image_link(
    openid: str,
    scene: str,
    source: Union[str, Path],
    file_type: Optional[int] = None,
    file_name: Optional[str] = None,
) -> Optional[str]:
    """
    上传并缓存「可访问链接」，返回可嵌入 Markdown 的远端 raw_url。

    流程：
      1. 按来源查数据库缓存，未过期则直接返回缓存链接
      2. 取得文件字节（本地直接读 / 网络先下载）
      3. 走分片上传，取响应中的 raw_url（COS 预签名 GET 链接，有效期 = ttl）
      4. 写入缓存表（带过期时间），返回 raw_url

    Args / Returns 同 upload_media，但返回值是可访问的图片链接字符串。
    """
    from app.modules import get_db

    key = str(source)
    db = get_db()
    cached = db.get_cached_media_by_source(key)
    if cached is not None:
        logger.debug(f"上传 >>> 命中缓存链接: {key}")
        return cached.url

    # 取得文件字节
    if isinstance(source, Path) or (
        isinstance(source, str) and not _is_url(source) and Path(source).exists()
    ):
        path = Path(source)
        data = path.read_bytes()
        fname = file_name or path.name
    elif isinstance(source, str) and _is_url(source):
        data = await _download(source)
        fname = file_name or _filename_from_url(source)
    else:
        data = await _download(str(source))
        fname = file_name or _filename_from_url(str(source))

    if not data:
        logger.error("上传 >>> 无法获取源文件字节，终止")
        return None

    ftype = _sniff_file_type(data, fname, file_type)
    if ftype == 1:
        if _is_supported_image(data):
            # png/jpg/gif/webp/bmp 受支持，原样上传（gif 保留动图），仅矫正扩展名
            fname = Path(fname).with_suffix(_image_ext(data)).name
        else:
            data = _ensure_png(data)
            fname = Path(fname).with_suffix(".png").name
    else:
        fname = _normalize_file_name(fname, ftype)
    result = await _do_chunked_upload(openid, scene, data, ftype, fname)
    if not result or not result.get("raw_url"):
        # 部分类型（如 file_type=4 文件）不会返回 raw_url，回退用 file_info 也无法嵌入 Markdown
        logger.error("上传 >>> 未获取到可嵌入的 raw_url（该类型可能不支持链接）")
        return None

    raw_url = result["raw_url"]
    ttl = int(result.get("ttl", 0) or 0)
    now = int(time.time())
    expire = now + ttl if ttl > 0 else now + FOREVER
    try:
        db.add_cached_media(
            source=key,
            url=raw_url,
            file_info=result.get("file_info"),
            ttl=ttl,
            create_time=str(now),
            expire_time=str(expire),
        )
    except Exception as e:
        logger.warning(f"上传 >>> 写入媒体缓存失败（不影响本次发送）: {e}")

    return raw_url
