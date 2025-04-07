import logging
from fastapi import WebSocket

logger=logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, email: str, websocket: WebSocket):
        self.active_connections[email] = websocket
        logger.info(f"{email} connected")
        logger.info("current notification list:%s", self.active_connections.keys())

    def disconnect(self, email: str):
        self.active_connections.pop(email, None)
        logger.info(f"{email} disconnected")
        logger.info("current notification list:%s", self.active_connections.keys())

    async def broadcast(self, message: str):
        for email, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception:
                logger.exception("Failed to send message to %s, disconnecting", email)
                self.disconnect(email)

ws_manager = ConnectionManager()
