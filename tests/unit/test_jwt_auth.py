import pytest
import jwt
from fastapi import WebSocket
from app.services.jwt_auth import extract_email_from_ws_cookie, load_user
from app.models.user import User


def test_extract_email_exceptions(mocker):
    websocket = mocker.Mock()

    # Case 1: Missing token
    websocket.cookies = {}
    with pytest.raises(ValueError, match="Missing token"):
        extract_email_from_ws_cookie(websocket)

    # Case 2: Invalid token
    websocket.cookies = {"access_token": "invalid"}
    mocker.patch("app.services.jwt_auth.jwt.decode", side_effect=jwt.DecodeError("bad token"))
    with pytest.raises(jwt.DecodeError):
        extract_email_from_ws_cookie(websocket)

    # Case 3: Missing 'sub'
    mocker.patch("app.services.jwt_auth.jwt.decode", return_value={})
    with pytest.raises(ValueError, match="Missing 'sub' in token"):
        extract_email_from_ws_cookie(websocket)


# Should return user if found in DB
def test_load_user_found(mocker):
    mock_user = User(email="user@example.com", hashed_password="xxx")
    mock_query = mocker.MagicMock()
    mock_query.first.return_value = mock_user

    mock_session = mocker.MagicMock()
    mock_session.exec.return_value = mock_query
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    mocker.patch("app.services.jwt_auth.Session", return_value=mock_session)

    user = load_user("user@example.com")

    assert user.email == "user@example.com"



# Should return None if user not found
def test_load_user_not_found(mocker):
    mock_query = mocker.MagicMock()
    mock_query.first.return_value = None

    mock_session = mocker.MagicMock()
    mock_session.exec.return_value = mock_query
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    mocker.patch("app.services.jwt_auth.Session", return_value=mock_session)

    user = load_user("nonexist@example.com")

    assert user is None
