import json

from channels.generic.websocket import AsyncWebsocketConsumer


class UploadRequestUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Accepts connection on uuid of user and create room."""
        self.user_uuid = self.scope["url_route"]["kwargs"]["user_uuid"]
        self.room_group_name = "upload_requests_%s" % self.user_uuid

        # Join room for one user's for all tabs
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Leaves room.

        Parameters
        ----------
        close_code : _type_
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    async def receive(self, text_data: str):
        """Recieves the message and send to the handler.

        Parameters
        ----------
        text_data : str
        """
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {**data, "type": "upload_request_update"},
        )

    async def upload_request_update(self, event: dict[str, str]):
        """Handler to broadcast message for update on upload request.

        Parameters
        ----------
        event : dict[str,str]
        """
        await self.send(json.dumps(event))
