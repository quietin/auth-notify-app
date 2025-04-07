# app/auth.py

import os
import logging
from fastapi_login import LoginManager

from sqlmodel import select, Session
from app.database import engine
from app.models import User

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
        logger.info("load user result: %s", user.model_dump())
        return user
