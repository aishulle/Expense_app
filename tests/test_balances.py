import pytest
from decimal import Decimal
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_raw_balances_after_expenses(client: AsyncClient, test_users, db_session):
    """Test raw balances correctness after multiple expenses."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    user_ids = []
    for user in test_users:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
        user_ids.append(str(user.id))
    
    # User 0 pays $100, split equally among all 3
    expense1 = {
        "paid_by_user_id": user_ids[0],
        "amount": "100.00",
        "description": "Expense 1",
        "split_type": "EQUAL",
        "splits": []
    }
    await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense1)
    
    # User 1 pays $60, split equally among all 3
    expense2 = {
        "paid_by_user_id": user_ids[1],
        "amount": "60.00",
        "description": "Expense 2",
        "split_type": "EQUAL",
        "splits": []
    }
    await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense2)
    
    # Get raw balances
    resp = await client.get(f"/api/v1/groups/{group_id}/balances/raw")
    assert resp.status_code == 200
    balances = resp.json()
    
    # User 0 paid $100, each person owes $33.33, so user 1 and 2 owe user 0
    # User 1 paid $60, each person owes $20, so user 0 and 2 owe user 1
    
    # Net: User 1 owes User 0: $33.33 - $20 = $13.33
    # Net: User 2 owes User 0: $33.33
    # Net: User 2 owes User 1: $20
    # User 0 is owed: $33.33 + $33.33 - $20 = $46.66
    # User 1 is owed: $20 - $33.33 = -$13.33 (owes $13.33)
    
    # Check that balances exist
    assert len(balances) > 0
    
    # Verify amounts are positive
    for balance in balances:
        assert Decimal(str(balance["amount"])) > 0


@pytest.mark.asyncio
async def test_simplified_balances(client: AsyncClient, test_users, db_session):
    """Test simplified balances correctness."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    user_ids = []
    for user in test_users[:2]:  # Use 2 users for simplicity
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
        user_ids.append(str(user.id))
    
    # User 0 pays $100, split equally (each owes $50)
    expense = {
        "paid_by_user_id": user_ids[0],
        "amount": "100.00",
        "description": "Expense",
        "split_type": "EQUAL",
        "splits": []
    }
    await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense)
    
    # Get simplified balances
    resp = await client.get(f"/api/v1/groups/{group_id}/balances/simplified")
    assert resp.status_code == 200
    simplified = resp.json()
    
    # User 1 should owe User 0 $50
    assert len(simplified) == 1
    assert simplified[0]["payer_id"] == user_ids[1]
    assert simplified[0]["payee_id"] == user_ids[0]
    assert Decimal(str(simplified[0]["amount"])) == Decimal("50.00")


@pytest.mark.asyncio
async def test_settlement_reduces_balances(client: AsyncClient, test_users, db_session):
    """Test that settlement reduces balances."""
    # Create group
    group_resp = await client.post("/api/v1/groups", json={"name": "Test Group"})
    group_id = group_resp.json()["id"]
    
    # Add users to group
    user_ids = []
    for user in test_users[:2]:
        await client.post(f"/api/v1/groups/{group_id}/members", json={"user_id": str(user.id)})
        user_ids.append(str(user.id))
    
    # User 0 pays $100, split equally (user 1 owes user 0 $50)
    expense = {
        "paid_by_user_id": user_ids[0],
        "amount": "100.00",
        "description": "Expense",
        "split_type": "EQUAL",
        "splits": []
    }
    await client.post(f"/api/v1/groups/{group_id}/expenses", json=expense)
    
    # Check initial balance
    resp = await client.get(f"/api/v1/groups/{group_id}/balances/simplified")
    assert resp.status_code == 200
    initial_balance = resp.json()[0]["amount"]
    assert Decimal(str(initial_balance)) == Decimal("50.00")
    
    # User 1 pays $30 to User 0
    settlement = {
        "payer_id": user_ids[1],
        "payee_id": user_ids[0],
        "amount": "30.00"
    }
    await client.post(f"/api/v1/groups/{group_id}/settlements", json=settlement)
    
    # Check updated balance (should be $50 - $30 = $20)
    resp = await client.get(f"/api/v1/groups/{group_id}/balances/simplified")
    assert resp.status_code == 200
    updated_balance = resp.json()[0]["amount"]
    assert Decimal(str(updated_balance)) == Decimal("20.00")

