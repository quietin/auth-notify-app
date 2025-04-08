# app/jwt_auth.py
import os
import jwt
import logging
from fastapi_login import LoginManager
from starlette.websockets import WebSocket

from sqlmodel import select, Session
from app.database import engine
from app.models.user import User

logger = logging.getLogger(__name__)

# Load secret key from environment
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

# Initialize token manager
manager = LoginManager(SECRET_KEY, token_url="/login", use_cookie=True)
manager.cookie_name = "access_token"


@manager.user_loader()
def load_user(email: str) -> User | None:
    logger.info("load user with email: %s", email)
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        return user


# fastapi-login doesn't provide a method to extract info from WebSocket request
def extract_email_from_ws_cookie(websocket: WebSocket) -> str:
    token = websocket.cookies.get(manager.cookie_name)
    if not token:
        raise ValueError("Missing token")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload.get("sub")
    if not email:
        raise ValueError("Missing 'sub' in token")
    return email
