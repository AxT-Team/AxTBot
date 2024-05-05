import functools,botpy
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
            except botpy.errors.ServerError as e: 
                await client.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    content='消息被去重，请重新唤起该指令',
                    msg_id=message.id
                )
        async def post_group_file(client, url):
            try:
                upload = await client.api.post_group_file(
                    group_openid=message.group_openid,
                    file_type=1,
                    url=url
                )
                await client.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7,
                    msg_id=message.id,
                    media=upload
                )
            except botpy.errors.ServerError as e: 
                await client.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    content='消息被去重，请重新唤起该指令',
                    msg_id=message.id
                )
        return await func(client, message, post_group_message, post_group_file, *args, **kwargs)
    return wrapper
