# app/main.py
from dotenv import load_dotenv

load_dotenv()

import logging
import jwt
from app.auth import manager, SECRET_KEY
from datetime import timedelta

from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from starlette.responses import HTMLResponse, RedirectResponse

from app.database import init_db, get_session
from sqlmodel import Session
from app.logger import init_logging
from app.models import UserCreate
from contextlib import asynccontextmanager
from app.user_handler import create_user, authenticate_user
from app.websocket_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_logging()
    yield

    # TODO
    # close corresponding res


logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/hello")
async def root():
    logger.info("say hello");
    return {"message": "Hello World"}


# Root route: redirect based on login status
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    token = request.cookies.get("access_token")
    if token:
        try:
            # Try to load user from token
            await manager(request)
            return RedirectResponse("/welcome")
        except Exception:
            pass
    return RedirectResponse("/login")


@app.get("/register_trigger")
async def register():
    await ws_manager.broadcast(f"New user registered: test555@gmail.com")

    return {"message": "trigger successfully"}


@app.post("/register")
async def register(user_in: UserCreate, user=Depends(create_user)):
    logger.info("Register request: %s", user_in.email)

    import asyncio
    # asyncio.create_task(wsManager.broadcast(f"📩 New user registered: {user.email}"))

    await ws_manager.broadcast(f"📩 New user registered: {user.email}")

    return {"message": "User registered successfully", "email": user.email}


#TODO: remove
@app.get("/me")
async def me(request: Request):
    import jwt
    from app.auth import SECRET_KEY
    print("✅ manager._user_callback =", manager._user_callback)
    try:
        token = request.cookies.get("access_token")
        print("🔍 Raw token from cookie:", token)

        # 手动解码看看 payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("🔍 JWT payload:", payload)

        user = await manager(request)  # 会尝试再次解码并调用 user_loader
        return {"email": user.email}

    except Exception as e:
        return {
            "error_type": type(e).__name__,
            "error_msg": str(e)
        }


@app.post("/login")
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
    response.set_cookie("access_token", access_token, secure=True, httponly=True, samesite="lax")
    return response


@app.post("/logout")
async def logout(request: Request):
    try:
        user = await manager(request)  # ✅ 自动从 cookie 中解析出 user
        print("logout user email: %s", user.email)
        ws_manager.disconnect(user.email)
    except HTTPException:
        pass  # 用户未登录，无需断开

    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response


@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    print("received ws coming")
    await websocket.accept()
    try:
        # user = await manager._get_user(websocket)
        # email = user.email
        # print("received ws conn:%s", email)

        token = websocket.cookies.get(manager.cookie_name)  # 通常是 "access_token"
        if not token:
            raise ValueError("Missing token")

        # fastapi-login doesn't provide method to extract info from WS request
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if not email:
            raise ValueError("Missing 'sub' in token")

        print("✅ WS connect from:", email)

        await ws_manager.connect(email, websocket)

        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(email)
    except Exception as e:
        print("❌ WebSocket auth failed:", e)
        await websocket.close()


# Login page
@app.get("/login", response_class=HTMLResponse)
def get_login_page():
    with open("app/static/login.html") as f:
        return HTMLResponse(f.read())


# Register page
@app.get("/register", response_class=HTMLResponse)
def get_register_page():
    with open("app/static/register.html") as f:
        return HTMLResponse(f.read())


# Welcome page
@app.get("/welcome", response_class=HTMLResponse)
async def get_welcome_page(request: Request):
    from fastapi_login.exceptions import InvalidCredentialsException as LoginAuthException
    print("🧪 type =", type(LoginAuthException))
    try:
        user = await manager(request)
        if user is None:
            logger.info("user is none")
            return RedirectResponse("/login", status_code=303)
        logger.info("user is existed")
    except HTTPException:
        return RedirectResponse("/login", status_code=303)

    with open("app/static/welcome.html") as f:
        return HTMLResponse(f.read())
