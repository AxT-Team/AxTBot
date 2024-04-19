import functools
def post_group_message_decorator(func):
    @functools.wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        async def post_group_message(client, message, content):
            try: 
                await client.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    content=content,
                    msg_id=message.id
                )
            except Exception as e: 
                await client.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    content='消息发送失败，请重试或联系管理员',
                    msg_id=message.id
                )
        return await func(client, message, post_group_message, *args, **kwargs)
    return wrapper
