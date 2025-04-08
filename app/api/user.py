from datetime import timedelta

import logging
from fastapi import Depends, Form, HTTPException, APIRouter
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from app.services.jwt_auth import manager
from app.database import get_session
from app.models.user import UserCreate
from app.services.noti_service import noti_manager
from app.services.user_service import create_user, authenticate_user
from app.services.jwt_auth import extract_email_from_ws_cookie
from app.config import STATIC_DIR

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/hello")
async def hello():
    logger.info("say hello")
    return {"message": "Hello World"}


# Root route: redirect based on login status
@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            # Try to load user from token
            await manager(request)
            return RedirectResponse("/welcome")
        except Exception:
            logger.exception("access path / failed ")

    return RedirectResponse("/login")


@router.post("/register")
async def register(user_in: UserCreate, user=Depends(create_user)):
    logger.info("Register request: %s", user_in.email)

    await noti_manager.broadcast(f"New user registered: {user.email}")

    return {"message": "User registered successfully", "email": user.email}


@router.post("/login")
def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
):
    user = authenticate_user(email, password, session)
    access_token = manager.create_access_token(
        data={"sub": user.email},
        expires=timedelta(hours=24)
    )

    response = JSONResponse({"message": "Login successful"})
    # set httponly=True to avoid security problems
    response.set_cookie("access_token", access_token, secure=True, httponly=True, samesite="lax")
    return response


@router.post("/logout")
async def logout(request: Request):
    try:
        # Automatically extract the user from the cookie
        user = await manager(request)
        logger.info("logout user email: %s", user.email)
        noti_manager.unsubscribe(user.email)
    except HTTPException:
        logger.exception("Logout failed")

    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@router.websocket("/ws/notifications")
async def notifications_ws_handler(websocket: WebSocket):
    email = None

    await websocket.accept()
    logger.info("a new ws conn is coming")
    try:
        # generally is "access_token"
        email = extract_email_from_ws_cookie(websocket)
        logger.info("ws connect from email:%s", email)
        await noti_manager.subscribe(email, websocket)

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if email:
            noti_manager.unsubscribe(email)
    except Exception as e:
        logger.exception("WebSocket error: %s", e)
    finally:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()


# Login page
@router.get("/login", response_class=HTMLResponse)
def get_login_page():
    return FileResponse(STATIC_DIR / "login.html")


# Register page
@router.get("/register", response_class=HTMLResponse)
def get_register_page():
    return FileResponse(STATIC_DIR / "register.html")


# Welcome page
@router.get("/welcome", response_class=HTMLResponse)
async def get_welcome_page(request: Request):
    try:
        user = await manager(request)
        if user is None:
            logger.info("user is none")
            return RedirectResponse("/login", status_code=303)
        logger.info("user is existed")
    except HTTPException:
        return RedirectResponse("/login", status_code=303)

    return FileResponse(STATIC_DIR / "welcome.html")
