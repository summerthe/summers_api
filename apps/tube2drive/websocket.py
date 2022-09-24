import websockets
from django.conf import settings


async def broadcast_upload_request_update(user_uuid: str, text_body: str):
    """Broadcast upload request update to user.

    Parameters
    ----------
    user_uuid : str
    text_body : str
    """
    url = f"{settings.WS_CURRENT_DOMAIN}/tube2drive/upload-requests/{user_uuid}/"
    headers = {"origin": settings.WS_CURRENT_DOMAIN}
    async with websockets.connect(url, extra_headers=headers) as websocket:
        await websocket.send(text_body)
