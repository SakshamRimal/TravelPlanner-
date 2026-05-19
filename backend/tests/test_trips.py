import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from backend.app.models.user_model import User
from backend.app.models.trip_model import Trip


@pytest.mark.asyncio
async def test_user_a_creates_trip(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.post(
        "/api/v1/trips",
        json={
            "origin": "KTM",
            "destination": "Pokhara",
            "budget": 50000,
            "travelers": 2,
            "start_date": (datetime.now().date() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=10)).isoformat(),
            "status": "planned",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["destination"] == "Pokhara"


@pytest.mark.asyncio
async def test_user_a_reads_own_trip(async_client: AsyncClient, auth_headers: dict, sample_trip: Trip):
    response = await async_client.get(
        f"/api/v1/trips/{sample_trip.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Pokhara"


@pytest.mark.asyncio
async def test_user_b_cannot_read_user_a_trip(async_client: AsyncClient, sample_trip: Trip, other_user_headers: dict):
    response = await async_client.get(
        f"/api/v1/trips/{sample_trip.id}",
        headers=other_user_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_b_cannot_update_user_a_trip(async_client: AsyncClient, sample_trip: Trip, other_user_headers: dict):
    response = await async_client.patch(
        f"/api/v1/trips/{sample_trip.id}",
        json={"destination": "Lukla"},
        headers=other_user_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_user_b_cannot_delete_user_a_trip(async_client: AsyncClient, sample_trip: Trip, other_user_headers: dict):
    response = await async_client.delete(
        f"/api/v1/trips/{sample_trip.id}",
        headers=other_user_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthenticated_user_cannot_list_trips(async_client: AsyncClient):
    response = await async_client.get("/api/v1/trips")
    assert response.status_code == 401