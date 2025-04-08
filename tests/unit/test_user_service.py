
# tests/unit/test_user_service.py

import pytest
from fastapi import HTTPException
from app.services.user_service import create_user, authenticate_user
from app.models.user import UserCreate, User
from app.utils.security import get_password_hash


# Test create_user for successful user creation.
def test_create_user_success(mocker):
    # Create a fake session object.
    session = mocker.Mock()

    # Simulate no duplicate user exists.
    fake_query = mocker.Mock()
    fake_query.first.return_value = None
    session.exec.return_value = fake_query

    # Stub methods for adding and committing.
    session.add.return_value = None
    session.commit.return_value = None

    # Simulate session.refresh to assign an id to the user.
    def refresh_side_effect(user):
        user.id = 1
    session.refresh.side_effect = refresh_side_effect

    # Construct a UserCreate instance.
    user_in = UserCreate(email="test@example.com", password="secret")

    # Call create_user function.
    result = create_user(user_in, session)

    # Verify the result is an instance of User.
    assert isinstance(result, User)

    # Verify the email is correctly assigned.
    assert result.email == "test@example.com"

    # Verify the hashed password format (bcrypt hash usually starts with "$2").
    assert result.hashed_password.startswith("$2")


# Test create_user when the email already exists.
def test_create_user_email_exists(mocker):
    # Create a fake session object.
    session = mocker.Mock()

    # Simulate that a user with the email already exists.
    existing_user = User(email="test@example.com", hashed_password="xxx")
    fake_query = mocker.Mock()
    fake_query.first.return_value = existing_user
    session.exec.return_value = fake_query

    # Construct a UserCreate instance.
    user_in = UserCreate(email="test@example.com", password="secret")

    # Verify that an HTTPException is raised when email exists.
    with pytest.raises(HTTPException) as exc:
        create_user(user_in, session)

    # Assert the exception status code is 400.
    assert exc.value.status_code == 400

    # Assert the exception message contains the expected detail.
    assert "Email already registered" in exc.value.detail


# Test authenticate_user for successful authentication.
def test_authenticate_user_success(mocker):
    # Create a fake session object.
    session = mocker.Mock()
    hashed = get_password_hash("secret")

    # Create a user instance with valid credentials.
    user = User(email="test@example.com", hashed_password=hashed)
    user.id = 1
    fake_query = mocker.Mock()
    fake_query.first.return_value = user
    session.exec.return_value = fake_query

    # Call authenticate_user with correct email and password.
    result = authenticate_user("test@example.com", "secret", session)

    # Verify the returned result is the expected User instance.
    assert result.email == "test@example.com"
    assert isinstance(result, User)


# Test authenticate_user with non-existent email.
def test_authenticate_user_invalid_email(mocker):
    # Create a fake session object.
    session = mocker.Mock()

    # Simulate that no user is found for the email.
    fake_query = mocker.Mock()
    fake_query.first.return_value = None
    session.exec.return_value = fake_query

    # Verify that an HTTPException is raised when email is not found.
    with pytest.raises(HTTPException) as exc:
        authenticate_user("nonexist@example.com", "secret", session)

    # Assert the exception status code is 401.
    assert exc.value.status_code == 401

    # Assert the exception message contains the expected detail.
    assert "Invalid credentials" in exc.value.detail


# Test authenticate_user with incorrect password.
def test_authenticate_user_invalid_password(mocker):
    # Create a fake session object.
    session = mocker.Mock()

    hashed = get_password_hash("test_other@example.com")

    # Create a user instance with an incorrect password hash.
    user = User(email="test@example.com", hashed_password=hashed)
    fake_query = mocker.Mock()
    fake_query.first.return_value = user
    session.exec.return_value = fake_query

    # Verify that an HTTPException is raised when the password is incorrect.
    with pytest.raises(HTTPException) as exc:
        authenticate_user("test@example.com", "wrong", session)

    # Assert the exception status code is 401.
    assert exc.value.status_code == 401

    # Assert the exception message contains the expected detail.
    assert "Invalid credentials" in exc.value.detail
