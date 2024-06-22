from botpy.message import GroupMessage, Message, DirectMessage

class HandleAtMessage:
    def __init__(self, client):
        self.client = client
        self.sendMessage = None
        self.sendFile = None

    def sendmessage(self, message, content):
        if isinstance(message, GroupMessage):
            self.client.api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                content=content,
                msg_id=message.id
            )
        if isinstance(message, Message):
            self.client.api.post_message(

            )
        if isinstance(message, DirectMessage):
            self.client.api.post_dms(

            )

    async def send_message(self, message):
        if isinstance(message, GroupMessage):
            self.sendMessage = self.client.api.post_group_message
            self.sendFile = self.client.api.post_group_file
        if isinstance(message, Message):
            self.sendMessage = self.client.api.post_message
        if isinstance(message, DirectMessage):
            self.sendMessage = self.client.api.post_dms