import pytest

@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    # Register
    resp = await client.post("/register", json={
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"

    # Login
    resp = await client.post("/login", data={
        "email": "alice@example.com",
        "password": "secret123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.cookies

    # Logout
    client.cookies.update(resp.cookies)
    resp = await client.post("/logout", follow_redirects=True)
    assert resp.status_code in (200, 303)


@pytest.mark.asyncio
async def test_login_and_register_errors(client):
    # Duplicate registration
    data = {"email": "dupe@example.com", "password": "abc123"}
    resp1 = await client.post("/register", json=data)
    assert resp1.status_code == 200

    resp2 = await client.post("/register", json=data)
    assert resp2.status_code == 400
    assert "Email already registered" in resp2.text

    # Register a valid user
    await client.post("/register", json={"email": "user@example.com", "password": "correct"})

    # Wrong password
    resp = await client.post("/login", data={
        "email": "user@example.com",
        "password": "wrong"
    })
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.text

    # Non-existent user
    resp = await client.post("/login", data={
        "email": "nosuch@example.com",
        "password": "whatever"
    })
    assert resp.status_code == 401
    assert "Invalid credentials" in resp.text
