import pytest
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Group, GroupMember, Expense, ExpenseSplit, SplitType


@pytest.mark.asyncio
async def test_equal_split_with_rounding(client: AsyncClient, test_users, db_session: AsyncSession):
    """Test equal split with 3 members and rounding."""
    # Create group with 3 users
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    for user in test_users:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
    
    # Create expense with equal split (amount that doesn't divide evenly)
    expense_data = {
        "paid_by_user_id": str(test_users[0].id),
        "amount": "100.00",
        "description": "Test expense",
        "split_type": "EQUAL",
        "splits": []  # Empty splits means split among all members
    }
    
    resp = await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense_data)
    assert resp.status_code == 201
    expense = resp.json()
    
    # Check that splits were created
    assert len(expense["splits"]) == 3
    
    # Check amounts (100 / 3 = 33.33, remainder distributed)
    split_amounts = [Decimal(str(s["amount"])) for s in expense["splits"]]
    total = sum(split_amounts)
    assert total == Decimal("100.00")
    
    # All amounts should be around 33.33 or 33.34
    assert all(amount in [Decimal("33.33"), Decimal("33.34")] for amount in split_amounts)


@pytest.mark.asyncio
async def test_exact_split_validation_failure(client: AsyncClient, test_users, db_session: AsyncSession):
    """Test that exact split fails when sum doesn't match total."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    for user in test_users[:2]:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
    
    # Create expense with exact split that doesn't sum correctly
    expense_data = {
        "paid_by_user_id": str(test_users[0].id),
        "amount": "100.00",
        "description": "Test expense",
        "split_type": "EXACT",
        "splits": [
            {"user_id": str(test_users[0].id), "amount": "50.00"},
            {"user_id": str(test_users[1].id), "amount": "40.00"}  # Sum = 90, should be 100
        ]
    }
    
    resp = await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense_data)
    assert resp.status_code == 400
    assert "must equal total amount" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_exact_split_success(client: AsyncClient, test_users, db_session: AsyncSession):
    """Test exact split with correct sum."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    for user in test_users[:2]:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
    
    # Create expense with exact split
    expense_data = {
        "paid_by_user_id": str(test_users[0].id),
        "amount": "100.00",
        "description": "Test expense",
        "split_type": "EXACT",
        "splits": [
            {"user_id": str(test_users[0].id), "amount": "60.00"},
            {"user_id": str(test_users[1].id), "amount": "40.00"}
        ]
    }
    
    resp = await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense_data)
    assert resp.status_code == 201
    expense = resp.json()
    
    assert len(expense["splits"]) == 2
    assert Decimal(expense["splits"][0]["amount"]) == Decimal("60.00")
    assert Decimal(expense["splits"][1]["amount"]) == Decimal("40.00")


@pytest.mark.asyncio
async def test_percent_split_validation_failure(client: AsyncClient, test_users, db_session: AsyncSession):
    """Test that percent split fails when sum != 100."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    for user in test_users[:2]:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
    
    # Create expense with percent split that doesn't sum to 100
    expense_data = {
        "paid_by_user_id": str(test_users[0].id),
        "amount": "100.00",
        "description": "Test expense",
        "split_type": "PERCENT",
        "splits": [
            {"user_id": str(test_users[0].id), "percent": "60.00"},
            {"user_id": str(test_users[1].id), "percent": "30.00"}  # Sum = 90, should be 100
        ]
    }
    
    resp = await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense_data)
    assert resp.status_code == 400
    assert "must equal 100" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_percent_split_with_rounding(client: AsyncClient, test_users, db_session: AsyncSession):
    """Test percent split with rounding."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    for user in test_users[:3]:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
    
    # Create expense with percent split (33.33% each)
    expense_data = {
        "paid_by_user_id": str(test_users[0].id),
        "amount": "100.00",
        "description": "Test expense",
        "split_type": "PERCENT",
        "splits": [
            {"user_id": str(test_users[0].id), "percent": "33.33"},
            {"user_id": str(test_users[1].id), "percent": "33.33"},
            {"user_id": str(test_users[2].id), "percent": "33.34"}  # Sum = 100
        ]
    }
    
    resp = await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense_data)
    assert resp.status_code == 201
    expense = resp.json()
    
    assert len(expense["splits"]) == 3
    
    # Check that amounts sum to total
    split_amounts = [Decimal(str(s["amount"])) for s in expense["splits"]]
    total = sum(split_amounts)
    assert total == Decimal("100.00")
    
    # Check that percents are stored
    assert all(s.get("percent") is not None for s in expense["splits"])

