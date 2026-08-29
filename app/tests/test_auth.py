def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Ayomide"
    assert data["email"] == "ayo@example.com"
    assert "password" not in data
    assert "password_hash" not in data
    
from app.database import SessionLocal
from app.models import User


def test_password_is_hashed(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    db = SessionLocal()

    user = (
        db.query(User)
        .filter(User.email == "ayo@example.com")
        .first()
    )

    assert user.password_hash != "hello123"
    assert user.password_hash.startswith("$argon2")

    db.close()
    
def test_duplicate_email(client):
    payload = {
        "name": "Ayomide",
        "email": "ayo@example.com",
        "password": "hello123",
    }

    first = client.post(
        "/auth/register",
        json=payload,
    )

    assert first.status_code == 201

    second = client.post(
        "/auth/register",
        json={
            "name": "AnotherUser",
            "email": "ayo@example.com",
            "password": "different123",
        },
    )

    assert second.status_code == 409
    
def test_duplicate_name(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "another@example.com",
            "password": "hello123",
        },
    )

    assert response.status_code == 409
    
def test_login(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "ayo@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    
def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "hello123",
        },
    )

    assert response.status_code == 401
    
def test_get_me_without_token(client):
    response = client.get("/users/me")

    assert response.status_code == 401
    
def test_get_me(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    access_token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Ayomide"
    assert data["email"] == "ayo@example.com"
    
def test_invalid_jwt(client):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer this-is-not-a-real-token"
        },
    )

    assert response.status_code == 401
    
def test_refresh_token(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    
def test_refresh_token_rotation(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    old_refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert response.status_code == 200

    new_refresh_token = response.json()["refresh_token"]

    assert new_refresh_token != old_refresh_token
    
def test_logout(client):
    client.post(
        "/auth/register",
        json={
            "name": "Ayomide",
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ayo@example.com",
            "password": "hello123",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200