# tests/unit/test_noti_service.py

import pytest
from app.services.noti_service import NotificationManager


# Should store websocket in active_connections after subscribe
@pytest.mark.asyncio
async def test_subscribe_adds_connection(mocker):
    manager = NotificationManager()
    websocket = mocker.MagicMock()
    websocket.send_text = mocker.AsyncMock()
    await manager.subscribe("user@example.com", websocket)
    assert "user@example.com" in manager.active_connections
    assert manager.active_connections["user@example.com"] == websocket


# Should remove websocket from active_connections
def test_unsubscribe_removes_connection(mocker):
    manager = NotificationManager()
    manager.active_connections["user@example.com"] = mocker.MagicMock()
    manager.unsubscribe("user@example.com")
    assert "user@example.com" not in manager.active_connections


# Should not raise error if email is not in active_connections
def test_unsubscribe_nonexistent_key(mocker):
    manager = NotificationManager()
    manager.unsubscribe("nonexistent@example.com")
    assert True


# Should broadcast message to all websockets
@pytest.mark.asyncio
async def test_broadcast_sends_to_all(mocker):
    manager = NotificationManager()
    ws1 = mocker.MagicMock()
    ws1.send_text = mocker.AsyncMock()
    ws2 = mocker.MagicMock()
    ws2.send_text = mocker.AsyncMock()
    manager.active_connections = {
        "user1@example.com": ws1,
        "user2@example.com": ws2,
    }
    await manager.broadcast("Hello")
    ws1.send_text.assert_awaited_once_with("Hello")
    ws2.send_text.assert_awaited_once_with("Hello")


# Should remove connection if send_text raises exception
@pytest.mark.asyncio
async def test_broadcast_handles_send_failure(mocker):
    manager = NotificationManager()
    good_ws = mocker.MagicMock()
    good_ws.send_text = mocker.AsyncMock()
    bad_ws = mocker.MagicMock()
    bad_ws.send_text = mocker.AsyncMock(side_effect=Exception("fail"))
    manager.active_connections = {
        "good@example.com": good_ws,
        "bad@example.com": bad_ws,
    }
    await manager.broadcast("Notify")
    assert "good@example.com" in manager.active_connections
    assert "bad@example.com" not in manager.active_connections
    good_ws.send_text.assert_awaited_once_with("Notify")
    bad_ws.send_text.assert_awaited_once_with("Notify")
