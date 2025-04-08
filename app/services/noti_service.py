import logging
from fastapi import WebSocket

logger=logging.getLogger(__name__)

# implement realtime notification based on WebSocket
class NotificationManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def subscribe(self, email: str, websocket: WebSocket):
        self.active_connections[email] = websocket
        logger.info(f"{email} subscribed")
        logger.info("current notification list:%s", self.active_connections.keys())

    def unsubscribe(self, email: str):
        self.active_connections.pop(email, None)
        logger.info(f"{email} unsubscribed")
        logger.info("current notification list:%s", self.active_connections.keys())

    async def broadcast(self, message: str):
        for email, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_text(message)
            except Exception:
                logger.exception("Failed to send message to %s, disconnecting", email)
                self.unsubscribe(email)

        logger.info("Finished sending notification. email list:%s", self.active_connections.keys())

noti_manager = NotificationManager()
