import time, tempfile, asyncio

from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent, MediaUploadPayload
from src.Utils.MessageSender import upload_file
from src.Utils.Logger import logger

from uapis_extension import get_from_api, format_count, fetch_screenshot_from_service, delayed_remove, _upload

__metadata__ = {
    "name": "[官方插件]B站视频查询",
    "version": "1.2.1",
    "author": "AxT-Team",
    "description": "从接口请求解析B站视频信息，并生成精美卡片图片",
    "official": True,
}


# 生成卡片 HTML
def generate_card_html(data):
    """根据视频数据生成 HTML 卡片"""
    bvid = data.get('bvid', '')
    title = data.get('title', '无标题')
    desc = data.get('desc', '').strip().replace('\n', ' ')
    pub_ts = data.get('pubdate', 0)
    pub_date = time.strftime('%Y-%m-%d', time.localtime(pub_ts)) if pub_ts else '未知'
    duration = data.get('duration', 0)
    minutes = duration // 60
    seconds = duration % 60
    duration_str = f"{minutes}:{seconds:02d}" if duration else "未知"

    tname = data.get('tname', '未知分区')
    copyright_type = data.get('copyright', 1)
    copyright_str = '原创' if copyright_type == 1 else '转载'

    pic_url = data.get('pic', '')
    owner = data.get('owner', {})
    owner_name = owner.get('name', '未知UP')
    owner_face = owner.get('face', '')
    owner_mid = owner.get('mid', '')

    stat = data.get('stat', {})
    view = format_count(stat.get('view', 0))
    danmaku = format_count(stat.get('danmaku', 0))
    like = format_count(stat.get('like', 0))
    coin = format_count(stat.get('coin', 0))
    favorite = format_count(stat.get('favorite', 0))

    placeholder_cover = "https://via.placeholder.com/800x450?text=No+Cover"
    placeholder_avatar = "https://via.placeholder.com/100?text=UP"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bilibili 视频卡片</title>
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
        .tags {{ display: flex; gap: 8px; margin-bottom: 20px; }}
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
        .publish-date {{
            font-size: 14px;
            color: #888;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .publish-date i {{ font-size: 14px; color: #fb7299; }}
        .stats {{
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .stat-item {{
            flex: 1;
            min-width: 70px;
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
        .duration i, .bvid i {{ margin-right: 4px; color: #fb7299; }}
        .bvid {{ font-family: monospace; }}
        .desc::-webkit-scrollbar {{ width: 6px; }}
        .desc::-webkit-scrollbar-track {{ background: #f1f1f1; border-radius: 10px; }}
        .desc::-webkit-scrollbar-thumb {{ background: #fb7299; border-radius: 10px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="cover">
            <img src="{pic_url}" alt="封面" onerror="this.src='{placeholder_cover}'">
        </div>
        <div class="title">{title}</div>
        <div class="tags">
            <span class="tag">{tname}</span>
            <span class="tag">{copyright_str}</span>
        </div>
        <div class="up-info">
            <div class="avatar">
                <img src="{owner_face}" alt="UP主头像" onerror="this.src='{placeholder_avatar}'">
            </div>
            <div class="up-details">
                <div class="up-name">{owner_name}</div>
                <div class="publish-date">
                    <i class="fas fa-calendar-alt"></i> 发布 · {pub_date}
                </div>
            </div>
        </div>
        <div class="stats">
            <div class="stat-item"><div class="stat-value">{view}</div><div class="stat-label"><i class="fas fa-play"></i> 播放</div></div>
            <div class="stat-item"><div class="stat-value">{danmaku}</div><div class="stat-label"><i class="fas fa-comment-dots"></i> 弹幕</div></div>
            <div class="stat-item"><div class="stat-value">{like}</div><div class="stat-label"><i class="fas fa-heart"></i> 点赞</div></div>
            <div class="stat-item"><div class="stat-value">{coin}</div><div class="stat-label"><i class="fas fa-coins"></i> 投币</div></div>
            <div class="stat-item"><div class="stat-value">{favorite}</div><div class="stat-label"><i class="fas fa-star"></i> 收藏</div></div>
        </div>
        <div class="desc">{desc}</div>
        <div class="footer">
            <div class="duration"><i class="fas fa-clock"></i> 总时长 {duration_str}</div>
            <div class="bvid"><i class="fas fa-hashtag"></i> {bvid}</div>
        </div>
    </div>
</body>
</html>
"""
    return html

@command(["bili", "/bili"])
async def bili_handler(event: GroupMessageEvent):
    # 解析参数
    parts = event.content.split()
    if len(parts) < 2:
        await event.reply("请提供AV号或BV号，例如：bili BV17x411w79F")
        return
    identifier = parts[1].strip()

    # 确定参数类型
    if identifier.lower().startswith("bv"):
        param = {"bvid": identifier}
    else:
        aid = identifier.replace("av", "").replace("AV", "")
        if aid.isdigit():
            param = {"aid": aid}
        else:
            await event.reply("输入的AV/BV号格式不正确")
            return

    # 获取视频信息
    try:
        query = "&".join(f"{k}={v}" for k, v in param.items())
        response = await get_from_api(f"/api/v1/social/bilibili/videoinfo?{query}")
    except Exception as e:
        await event.reply("视频信息获取失败，请确保您输入了正确的AV/BV号！")
        raise e

    if not response:
        await event.reply("API返回数据为空，无法解析视频信息")
        logger.error("解析结果：" + str(response))
        return

    # 尝试生成图片卡片（在线程中运行同步 Playwright 代码）
    try:
        html = generate_card_html(response)   # 生成 HTML
        img_bytes = await fetch_screenshot_from_service(html)

        # 保存临时文件并发送
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        # 发送图片（CQ 码格式，请根据你的机器人平台调整）
        url = await _upload(tmp_path)
        asyncio.create_task(delayed_remove(tmp_path))
        if url:
            try:
                response = await upload_file(
                    MediaUploadPayload(file_type=1, url=url, event=event)
                )
                if response:
                    await event.reply(
                        content="请确保您提供的图片无违规内容，否则将上报腾讯",
                        media=response,
                    )
            except Exception as e:
                # 发送失败则回退为文本并提供链接
                logger.error(f"图片发送失败，已上传至：{url}")
                await event.reply(
                    content=f"图片发送失败\n{e}",
                )
    except Exception as e:
        import traceback
        traceback.print_exc()   # 或者 logger.error(traceback.format_exc())
        logger.error(f"截图服务调用失败: {e}")
        # 回退到文本回复
        bvid = response.get("bvid", "")
        avid = response.get("aid", "")
        part = response.get("videos", 1)
        part_name = response.get("tname", "未知")
        copyright = "原创" if response.get("copyright") == 1 else "转载" if response.get("copyright") == 2 else "未知"
        duration_sec = response.get("duration", 0)
        duration = f"{duration_sec//60}分{duration_sec%60}秒"

        returns = f"""视频标题：{response.get('title','无标题')}
视频AV号：av{avid}  BV号：{bvid}
分P数：{part}  分区：{part_name}
{copyright} | 时长：{duration}"""
        await event.reply(returns)