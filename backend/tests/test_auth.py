import pytest
from httpx import AsyncClient

from backend.app.models.user_model import User


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "ValidPass123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "ValidPass123",
            "full_name": "Duplicate User",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "password": "short",
            "full_name": "Weak User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPass123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPass123",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token(async_client: AsyncClient):
    response = await async_client.get("/api/v1/trips")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_invalid_token(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/trips",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_returns_new_token(async_client: AsyncClient, test_user: User):
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
        },
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    old_refresh = tokens["refresh_token"]

    refresh_response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert new_tokens["refresh_token"] != old_refresh
    assert "access_token" in new_tokens


@pytest.mark.asyncio
async def test_old_refresh_token_rejected_after_rotation(async_client: AsyncClient, test_user: User):
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123",
        },
    )
    tokens = login_response.json()
    old_refresh = tokens["refresh_token"]

    first_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert first_refresh.status_code == 200

    second_refresh = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert second_refresh.status_code == 401