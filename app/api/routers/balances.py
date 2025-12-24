from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import json

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.services.balance_service import BalanceService
from app.schemas.balance import RawBalanceResponse, SimplifiedBalanceResponse
from decimal import Decimal

router = APIRouter(prefix="/groups/{group_id}/balances", tags=["balances"])


@router.get("/raw", response_model=list[RawBalanceResponse])
async def get_raw_balances(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get raw balances (ledger-style) for a group."""
    cache_key = f"balances:{group_id}:raw"
    
    # Try to get from cache
    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        return [
            RawBalanceResponse(
                debtor_id=item["debtor_id"],
                creditor_id=item["creditor_id"],
                amount=Decimal(str(item["amount"]))
            )
            for item in data
        ]
    
    # Calculate balances
    balance_service = BalanceService(db)
    balances = await balance_service.get_raw_balances(group_id)
    
    # Convert to response format
    result = [
        RawBalanceResponse(
            debtor_id=b["debtor_id"],
            creditor_id=b["creditor_id"],
            amount=Decimal(str(b["amount"]))
        )
        for b in balances
    ]
    
    # Cache for 1 hour (serialize for cache)
    cache_data = [
        {
            "debtor_id": r.debtor_id,
            "creditor_id": r.creditor_id,
            "amount": float(r.amount)
        }
        for r in result
    ]
    await redis_client.setex(cache_key, 3600, json.dumps(cache_data))
    
    return result


@router.get("/simplified", response_model=list[SimplifiedBalanceResponse])
async def get_simplified_balances(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get simplified balances for a group."""
    cache_key = f"balances:{group_id}:simplified"
    
    # Try to get from cache
    cached = await redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        return [SimplifiedBalanceResponse(**item) for item in data]
    
    # Calculate balances
    balance_service = BalanceService(db)
    balances = await balance_service.get_simplified_balances(group_id)
    
    # Convert to response format
    result = [
        {
            "payer_id": str(b["payer_id"]),
            "payee_id": str(b["payee_id"]),
            "amount": float(b["amount"])
        }
        for b in balances
    ]
    
    # Cache for 1 hour
    await redis_client.setex(cache_key, 3600, json.dumps(result))
    
    return [SimplifiedBalanceResponse(**item) for item in result]

