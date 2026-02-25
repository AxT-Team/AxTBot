import re
from urllib.parse import quote

from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent, MediaUploadPayload
from src.Utils.MessageSender import upload_file
from src.Utils.Logger import logger

from uapis_extension import apiconfig, post_for_api

__metadata__ = {
    "name": "[官方插件]摸摸头~",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "通过UnionOpenID或QQ号、图片获取摸头GIF",
    "official": True,
}


@command(["摸", "/摸"])
async def touch_handler(event: GroupMessageEvent):
    # 去除前后空格
    content = event.content.strip()
    
    # 显示帮助菜单
    if content in ['摸', '/摸', '/摸 ', '摸 ']:
        help_content = "=======摸一摸菜单=======" + "\n" + \
                   "/摸 [QQ号] - 通过QQ号生成摸一摸GIF" + "\n" + \
                   "/摸 [图片] - 通过图片生成摸一摸GIF" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /摸 3889003621" + "\n" + \
                   "或直接发送: /摸 [图片]" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，请重试。多张图片只取第一张作为参照" + "\n" + \
                   "=========================="
        await event.reply(content=help_content)
        return
    
    # 检查是否有附件（图片）
    has_attachment = event.attachments
    
    # 尝试匹配 QQ 号
    match = re.match(r"(?:/)?摸\s*(\d+)", content)
    
    try:
        if match:
            # 有 QQ 号 - 使用 GET 请求
            qq_number = match.group(1)
            logger.debug(f"摸头插件 >>> 使用QQ号: {qq_number}")
            
            payload = MediaUploadPayload(file_type=1, event=event)
            payload.url = f"{apiconfig.url}api/v1/image/motou?qq={qq_number}"
            
            logger.debug(f"摸头插件 >>> 请求URL: {payload.url}")
            result = await upload_file(payload)
            
            if result:
                await event.reply(content="请确保您提供的QQ号无违规内容，否则将上报腾讯", media=result)
            else:
                await event.reply(content="获取失败。\n请检查您的QQ号是否正确，或重新发起命令。\n若多次出现该问题，请提交至AxT社区")
                
        elif has_attachment:
            # 没有 QQ 号但有图片 - 使用 POST 请求
            image_url = event.attachments[0].get("url")
            logger.debug(f"摸头插件 >>> 使用图片URL: {image_url}")
            
            # URL编码图片地址，然后构建完整的API URL
            encoded_image_url = quote(image_url, safe='')
            api_url = f"?image_url={encoded_image_url}"
            
            logger.debug(f"摸头插件 >>> 请求URL: motou.shanshui.qzz.io/{api_url}")
            
            # 直接使用带编码参数的URL上传
            payload = MediaUploadPayload(file_type=1, event=event)
            payload.url = f"https://motou.shanshui.qzz.io/{api_url}"
            
            logger.debug(f"摸头插件 >>> 尝试上传图片")
            result = await upload_file(payload)
            
            if result:
                await event.reply(content="请确保您提供的图片无违规内容，否则将上报腾讯", media=result)
            else:
                await event.reply(content="生成摸头图片失败，请检查图片是否有效或重试")
        else:
            # 既没有 QQ 号也没有图片
            await event.reply(content="请提供QQ号或图片")
            return
            
    except Exception as e:
        logger.error(f"摸头插件 >>> 处理失败")
        logger.error(f"  ├─ 内容: {content}")
        logger.error(f"  ├─ 有附件: {has_attachment}")
        logger.error(f"  ├─ 错误类型: {type(e).__name__}")
        logger.error(f"  └─ 错误信息: {str(e)}")
        await event.reply(content=f"处理失败：{str(e)}")

