import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test creating a user."""
    resp = await client.post(
        "/api/v1/users",
        json={"name": "John Doe", "email": "john@example.com"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, test_user):
    """Test getting a user by ID."""
    resp = await client.get(f"/api/v1/users/{test_user.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_create_group(client: AsyncClient):
    """Test creating a group."""
    resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Group"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_group_with_members(client: AsyncClient, test_user):
    """Test getting a group with members."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add member
    await client.post(
        f"/api/v1/groups/{group_id}/members",
        json={"user_id": str(test_user.id)}
    )
    
    # Get group
    resp = await client.get(f"/api/v1/groups/{group_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Group"
    assert len(data["members"]) == 1
    assert data["members"][0]["user_id"] == str(test_user.id)

