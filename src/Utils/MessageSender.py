import aiohttp
from datetime import datetime, timedelta

from src.Utils.EventClass import (
    MediaPayload,
    MessageSenderBasePayload,
    MessageSenderOverPayload,
    AutoReplyPayload,
    MediaUploadPayload,
)
from src.Utils.Logger import logger
from src.Utils.EventSenderApp import SentMessageStore
from src.Utils.EventSender import SentGroupMessage

open_url = "https://api.sgroup.qq.com"


async def send_group_message(group_openid, payload: MessageSenderBasePayload) -> None:
    logger.debug(f"发送群聊消息 -> {group_openid}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    # 检查是否有相同的消息正在发送或最近已发送（5秒内）
    recent_time = datetime.now() - timedelta(seconds=5)
    
    # 查询最近5秒内相同内容的消息
    recent_same_message = await SentGroupMessage.filter(
        group_id=group_openid,
        message=payload.content,
        timestamp__gte=recent_time
    ).first()
    
    if recent_same_message:
        logger.warning(f"消息去重检测 >>> 检测到重复消息")
        logger.warning(f"  ├─ 群组ID: {group_openid}")
        logger.warning(f"  ├─ 消息内容: {payload.content[:50]}...")
        logger.warning(f"  ├─ 上次发送时间: {recent_same_message.timestamp}")
        logger.warning(f"  ├─ 上次发送状态: {recent_same_message.status}")
        logger.warning(f"  └─ 建议: 跳过发送，避免被QQ平台去重")
        
        # 如果上次发送成功，直接返回
        if recent_same_message.status == "success":
            logger.info(f"消息去重 >>> 消息已在5秒内成功发送，跳过本次发送")
            return
        # 如果上次发送pending，也跳过
        elif recent_same_message.status == "pending":
            logger.info(f"消息去重 >>> 消息正在发送中，跳过本次发送")
            return

    record = await SentMessageStore.log_sent_group_message(
        group_id=group_openid, message=payload.content
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/v2/groups/{group_openid}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="group",
                    status="success",
                    message_id=response_json["id"],
                )
                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            
            errinfo = await response.json()
            
            # 详细的错误日志
            error_code = errinfo.get('code', '未知')
            error_msg = errinfo.get('message', '未知错误')
            err_code = errinfo.get('err_code', '未知')
            trace_id = errinfo.get('trace_id', '未知')
            
            logger.error(f"❌ 发送群消息失败")
            logger.error(f"  ├─ 群组ID: {group_openid}")
            logger.error(f"  ├─ 消息内容: {payload.content[:100]}...")
            logger.error(f"  ├─ HTTP状态码: {response.status}")
            logger.error(f"  ├─ 错误代码: {error_code}")
            logger.error(f"  ├─ 错误信息: {error_msg}")
            logger.error(f"  ├─ 内部错误码: {err_code}")
            logger.error(f"  └─ 追踪ID: {trace_id}")
            
            # 根据错误代码提供建议
            if error_code == 40054005:
                logger.error(f"  💡 建议: 消息被去重")
                logger.error(f"     - 原因：5秒内发送了相同的消息")
                logger.error(f"     - 解决：等待5秒后重试，或修改消息内容")
                logger.error(f"     - 注意：本地去重检查可能未生效，请检查数据库连接")
            elif error_code == 304023:
                logger.error(f"  💡 建议: 消息发送频率过高")
                logger.error(f"     - 解决：降低消息发送频率")
            elif error_code == 304024:
                logger.error(f"  💡 建议: 消息内容违规")
                logger.error(f"     - 解决：检查消息内容是否包含敏感词")
            
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="group",
                status="failed",
                error_info=str(errinfo),
            )


async def send_channel_message(channel_id, guild_id, payload: MessageSenderBasePayload):
    """发送频道消息"""
    logger.debug(f"发送频道消息 -> {channel_id}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_channel_message(
        channel_id=channel_id,
        guild_id=guild_id,
        message=payload.content,
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/channels/{channel_id}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="channel",
                    status="success",
                    message_id=response_json["id"],
                )
                logger.debug(f"发信 >>> 返回结果 -> {response_json}")
                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="channel",
                status="failed",
                error_info=errinfo,
            )


async def send_channel_dms(guild_id, payload: MessageSenderBasePayload):
    logger.debug(f"发送频道私聊消息 -> {guild_id}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_channel_private_message(
        guild_id=guild_id,
        message=payload.content,
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/dms/{guild_id}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                logger.debug(f"发信 >>> 返回结果 -> {response_json}")
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="dms",
                    status="success",
                    message_id=response_json["id"],
                )

                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="dms",
                status="failed",
                error_info=errinfo,
            )


async def send_private_message(user_id, payload: MessageSenderBasePayload):
    logger.debug(f"发送QQ私聊消息 -> {user_id}: {payload.content}")
    from src.Utils.GetAccessToken import ACCESS_TOKEN

    record = await SentMessageStore.log_sent_user_message(
        message=payload.content, user_id=user_id
    )

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{open_url}/v2/users/{user_id}/messages",
            json=payload.to_dict(),
            headers={
                "Authorization": f"QQBot {ACCESS_TOKEN}",
                "Content-Type": "application/json",
            },
        ) as response:
            if response.status == 200:
                response_json: MessageSenderOverPayload = await response.json()
                logger.debug(f"发信 >>> 返回结果 -> {response_json}")
                await SentMessageStore.update_message_status(
                    record_id=record.id,
                    message_type="user",
                    status="success",
                    message_id=response_json["id"],
                )
                return
            elif response.status == 204:
                logger.debug(f"发信 >>> 操作成功，本请求无包体")
                return
            elif response.status in [201, 202]:
                logger.debug(f"发信 >>> 异步操作成功，但本请求存在问题")
                response_json = await response.json()
                logger.debug(f"发信 >>> 异步操作结果 -> {response_json}")
                return
            elif response.status == 401:
                logger.debug(f"发信 >>> 错误：未授权，请检查access_token")
            elif response.status == 404:
                logger.debug(f"发信 >>> 错误：未找到，请检查群组ID")
            elif response.status == 405:
                logger.debug(f"发信 >>> 错误：方法错误，请检查请求方法")
            elif response.status == 429:
                logger.debug(f"发信 >>> 错误：请求被限制，请检查请求频率")
            elif response.status in [500, 504]:
                logger.debug(f"发信 >>> 错误：开放平台处理失败")
            errinfo = await response.json()
            logger.error(f"发信 >>> 错误：{errinfo}")
            await SentMessageStore.update_message_status(
                record_id=record.id,
                message_type="user",
                status="failed",
                error_info=errinfo,
            )


async def send_auto_reply(payload: AutoReplyPayload) -> None:
    """发送自动填充的消息"""
    base_payload = MessageSenderBasePayload()
    if payload.markdown:
        base_payload.markdown = payload.markdown
        base_payload.msg_type = 2
    base_payload.msg_id = payload.msg_id
    if payload.ark:
        base_payload.ark = payload.ark
        base_payload.msg_type = 3
    if payload.media:
        base_payload.media = payload.media
        base_payload.msg_type = 7
    if payload.image:
        base_payload.image = payload.image
    if payload.group_id:
        if payload.markdown or payload.ark:
            base_payload.content = " "
        elif payload.event_id:
            base_payload.event_id = payload.event_id
            base_payload.content = payload.content
        else:
            base_payload.content = "\n" + str(payload.content)
        await send_group_message(payload.group_id, base_payload)
    elif payload.channel_id and payload.is_direct_message == False:
        base_payload.content = payload.content
        await send_channel_message(payload.channel_id, payload.guild_id, base_payload)
    elif payload.guild_id:
        base_payload.content = payload.content
        await send_channel_dms(payload.guild_id, base_payload)
    elif payload.user_id:
        base_payload.content = payload.content
        await send_private_message(payload.user_id, base_payload)
    logger.debug(base_payload.to_dict())


async def upload_file(payload: MediaUploadPayload):
    """上传文件至QQ服务器，返回文件信息

    :param payload: MediaUploadPayload 上传文件的负载
    :return dict: 文件信息 or None
    :return url: 传入原url 用于处理频道图片

    ---

    详见：
    - 群聊/私聊：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/rich-media.html
    - 频道/频私：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/post_messages.html

    Powered by AxTn Network 2023-2025
    """
    logger.debug(f"上传文件 {payload.url} 至QQ服务器")
    if payload.event.event_type == "群消息":
        url = open_url + f"/v2/groups/{payload.event.group_id}/files"
    elif payload.event.event_type == "私信":
        url = open_url + f"/v2/users/{payload.event.user_id}/files"
    elif payload.event.event_type in ["频道艾特", "私域频道", "频道私信"]:
        url = payload.url  # 频道图片上传使用原url
        return MediaPayload({"url": payload.url})

    else:
        logger.error(f"上传文件失败: 不支持的消息类型 {payload.event.event_type}")
        return None
    async with aiohttp.ClientSession() as session:
        from src.Utils.GetAccessToken import ACCESS_TOKEN
        async with session.post(
            url,
            json=payload.to_dict(),
            headers={"Authorization": f"QQBot {ACCESS_TOKEN}"},
        ) as response:
            logger.debug(str(payload.to_dict()) + "，请求URL为：" + url)
            if response.status == 200:
                file_info = await response.json()
                return MediaPayload(file_info)
            else:
                message = await response.json()
                # 详细的错误日志
                logger.error(f"❌ 上传文件失败")
                logger.error(f"  ├─ 消息类型: {payload.event.event_type}")
                logger.error(f"  ├─ 文件类型: {payload.file_type} (1=图片, 2=视频, 3=语音, 4=文件)")
                logger.error(f"  ├─ 文件URL: {payload.url}")
                logger.error(f"  ├─ 请求URL: {url}")
                logger.error(f"  ├─ HTTP状态码: {response.status}")
                
                # 解析错误信息
                error_code = message.get('code', '未知')
                error_msg = message.get('message', '未知错误')
                err_code = message.get('err_code', '未知')
                trace_id = message.get('trace_id', '未知')
                
                logger.error(f"  ├─ 错误代码: {error_code}")
                logger.error(f"  ├─ 错误信息: {error_msg}")
                logger.error(f"  ├─ 内部错误码: {err_code}")
                logger.error(f"  └─ 追踪ID: {trace_id}")
                
                # 根据错误代码提供建议
                if error_code == 850026:
                    logger.error(f"  💡 建议: 富媒体文件下载失败，可能原因：")
                    logger.error(f"     - 文件URL无法访问或已失效")
                    logger.error(f"     - 文件服务器拒绝QQ服务器访问")
                    logger.error(f"     - 文件格式不支持或文件损坏")
                    logger.error(f"     - 网络连接问题")
                elif error_code == 304003:
                    logger.error(f"  💡 建议: URL非法，请检查文件URL格式")
                elif error_code == 304004:
                    logger.error(f"  💡 建议: 文件大小超过限制")
                elif error_code == 304005:
                    logger.error(f"  💡 建议: 文件格式不支持")
                raise