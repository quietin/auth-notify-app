import logging
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import UserCreate, User
from app.utils import get_password_hash, verify_password


logger = logging.getLogger(__name__)


def create_user(user_in: UserCreate, session: Session = Depends(get_session)) -> User:
    """Register a new user with hashed password."""
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    logger.info("New user registered: %s", user.email)
    return user


def authenticate_user(email: str, password: str, session: Session) -> User:
    """Authenticate user and check password."""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        logger.info("Login failed for email: %s", email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info("fetch user:%s ", user.model_dump());
    return user