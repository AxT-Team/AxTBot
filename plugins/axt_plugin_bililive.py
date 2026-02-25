import asyncio, tempfile

from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent, MediaUploadPayload
from src.Utils.MessageSender import upload_file
from src.Utils.Logger import logger

from uapis_extension import get_from_api, format_count, fetch_screenshot_from_service, delayed_remove, _upload

__metadata__ = {
    "name": "[官方插件]B站直播查询",
    "version": "2.0.2",
    "author": "AxT-Team",
    "description": "从接口请求得到B站直播间开播状态等信息，并生成精美卡片图片",
    "official": True,
}

def generate_card_html(data):
    """根据直播数据生成 HTML 卡片"""
    uid = data.get('uid', '')
    room_id = data.get('room_id', '')
    short_id = data.get('short_id', 0)
    display_room_id = short_id if short_id != 0 else room_id

    live_status = data.get('live_status', 0)
    status_map = {0: '未开播', 1: '直播中', 2: '轮播中'}
    status = status_map.get(live_status, '未知状态')

    attention = format_count(data.get('attention', 0))
    online = format_count(data.get('online', 0))

    parent_area = data.get('parent_area_name', '')
    area = data.get('area_name', '')
    area_display = f"{parent_area} > {area}" if parent_area and area else (parent_area or area or '未知分区')

    title = data.get('title', '无标题').strip()
    desc = data.get('description', '').strip().replace('\n', ' ')

    # 封面优先使用 user_cover，否则用 background
    cover = data.get('user_cover') or data.get('background') or ''
    # 主播头像（通过 uid 拼接，可能不存在，设置 onerror 占位）
    avatar_url = f"https://i0.hdslb.com/bfs/face/{uid}.jpg" if uid else ''

    live_time = data.get('live_time', '')
    if not live_time or live_status == 0:
        live_time = '未开播'

    tags_str = data.get('tags', '')
    tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []

    placeholder_cover = "https://via.placeholder.com/800x450?text=No+Cover"
    placeholder_avatar = "https://via.placeholder.com/100?text=UP"

    # 生成标签 HTML
    tags_html = ''
    for tag in tags_list:
        tags_html += f'<span class="tag">{tag}</span>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bilibili 直播间卡片</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f5f5f5;
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK', 'Helvetica Neue', sans-serif;
        }}
        .card {{
            width: 800px;
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.08), 0 6px 12px rgba(0,0,0,0.05);
            overflow: hidden;
            padding: 24px;
        }}
        .cover {{
            width: 100%;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .cover img {{ width: 100%; height: auto; display: block; }}
        .title {{
            font-size: 26px;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 12px;
            color: #1a1a1a;
            word-break: break-word;
        }}
        .tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
        .tag {{
            background-color: #fdeef2;
            color: #fb7299;
            font-size: 14px;
            font-weight: 500;
            padding: 4px 12px;
            border-radius: 20px;
        }}
        .up-info {{
            display: flex;
            align-items: center;
            margin-bottom: 24px;
        }}
        .avatar {{
            width: 56px;
            height: 56px;
            border-radius: 50%;
            overflow: hidden;
            margin-right: 16px;
            border: 2px solid #fb7299;
            flex-shrink: 0;
        }}
        .avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
        .up-details {{ flex: 1; }}
        .up-name {{ font-size: 18px; font-weight: 600; color: #1a1a1a; margin-bottom: 4px; }}
        .room-meta {{
            font-size: 14px;
            color: #888;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .room-meta i {{ font-size: 14px; color: #fb7299; margin-right: 2px; }}
        .stats {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            flex: 1;
            min-width: 80px;
            background: #f9f9f9;
            border-radius: 16px;
            padding: 12px 6px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 22px;
            font-weight: 700;
            color: #fb7299;
            margin-bottom: 4px;
        }}
        .stat-label {{
            font-size: 13px;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
        }}
        .stat-label i {{ font-size: 14px; color: #fb7299; }}
        .desc {{
            background: #f9f9f9;
            border-radius: 16px;
            padding: 16px;
            margin-bottom: 24px;
            font-size: 15px;
            line-height: 1.6;
            color: #444;
            word-break: break-word;
            max-height: 120px;
            overflow-y: auto;
        }}
        .footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 2px solid #eee;
            font-size: 14px;
            color: #888;
        }}
        .live-time i, .room-id i {{ margin-right: 4px; color: #fb7299; }}
        .desc::-webkit-scrollbar {{ width: 6px; }}
        .desc::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 10px; }}
        .desc::-webkit-scrollbar-thumb {{ background: #fb7299; border-radius: 10px; }}
        .status-badge {{
            display: inline-block;
            background-color: #fb7299;
            color: white;
            font-size: 14px;
            font-weight: 500;
            padding: 4px 12px;
            border-radius: 20px;
            margin-left: 12px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="cover">
            <img src="{cover}" alt="封面" onerror="this.src='{placeholder_cover}'">
        </div>
        <div class="title">
            {title}
            <span class="status-badge">{status}</span>
        </div>
        <div class="tags">
            {tags_html}
        </div>
        <div class="up-info">
            <div class="avatar">
                <img src="{avatar_url}" alt="主播头像" onerror="this.src='{placeholder_avatar}'">
            </div>
            <div class="up-details">
                <div class="up-name">UID: {uid}</div>
                <div class="room-meta">
                    <span><i class="fas fa-door-open"></i> 房间号: {display_room_id}</span>
                    <span><i class="fas fa-tag"></i> {area_display}</span>
                </div>
            </div>
        </div>
        <div class="stats">
            <div class="stat-item"><div class="stat-value">{online}</div><div class="stat-label"><i class="fas fa-eye"></i> 人气</div></div>
            <div class="stat-item"><div class="stat-value">{attention}</div><div class="stat-label"><i class="fas fa-heart"></i> 粉丝</div></div>
        </div>
        <div class="desc">{desc}</div>
        <div class="footer">
            <div class="live-time"><i class="fas fa-clock"></i> 开播时间: {live_time}</div>
            <div class="room-id"><i class="fas fa-hashtag"></i> 长号: {room_id}</div>
        </div>
    </div>
</body>
</html>
"""
    return html

@command(["blive", "/blive"])
async def bili_handler(event: GroupMessageEvent):
    msg = event.content.split(" ")[1] if len(event.content.split(" ")) > 1 else ""
    if not msg:
        await event.reply("请输入主播UID或房间号，例如：blive 672328094")
        return

    # 尝试用 mid 查询，失败则用 room_id 查询
    try:
        response = await get_from_api(f"/api/v1/social/bilibili/liveroom?mid={msg}")
    except Exception:
        try:
            response = await get_from_api(f"/api/v1/social/bilibili/liveroom?room_id={msg}")
        except Exception as e:
            await event.reply("房间信息获取失败，请确保您输入了正确的房间号/主播UID")
            logger.error(f"API请求失败: {e}")
            return

    if not response:
        await event.reply("API返回数据为空")
        return

    # 尝试生成图片卡片
    try:
        html = generate_card_html(response)   # 生成 HTML
        img_bytes = await fetch_screenshot_from_service(html)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        url = await _upload(tmp_path)
        asyncio.create_task(delayed_remove(tmp_path))

        if url:
            try:
                upload_resp = await upload_file(
                    MediaUploadPayload(file_type=1, url=url, event=event)
                )
                if upload_resp:
                    await event.reply(content="请确保您提供的图片无违规内容，否则将上报腾讯", media=upload_resp)
            except Exception as e:
                logger.error(f"图片发送失败，已上传至：{url}")
                await event.reply(f"图片发送失败，但已上传至：{url}")
        else:
            raise Exception("OSS上传失败")
    except Exception as e:
        logger.error(f"截图服务调用失败: {e}")
        # 回退为文本
        uid = response.get("uid", "")
        roomid = response.get("room_id", "")
        short_id = response.get("short_id", 0)
        display_room = short_id if short_id != 0 else roomid
        attention = response.get("attention", 0)
        online = response.get("online", 0)
        status = response.get("live_status", 0)
        status_map = {0: "未开播", 1: "开播中", 2: "轮播中"}
        status_str = status_map.get(status, "未知状态")
        area = f"{response.get('parent_area_name', '')} > {response.get('area_name', '')}"
        title = response.get("title", "")
        desc = response.get("description", "")
        live_time = response.get("live_time", "N/A") if status == 1 else "N/A"
        tags = response.get("tags", "")

        returns = f"主播UID: {uid}\n房间号: {display_room}\n开播状态: {status_str}\n直播标题: {title}\n直播分区: {area}\n直播时间: {live_time}\n粉丝数: {attention}\n人气: {online}\n标签: {tags}\n直播简介: {desc}"
        await event.reply(returns)