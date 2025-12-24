from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.services.settlement_service import SettlementService
from app.schemas.settlement import SettlementCreate, SettlementResponse

router = APIRouter(prefix="/groups/{group_id}/settlements", tags=["settlements"])


async def invalidate_balance_cache(redis_client: redis.Redis, group_id: UUID):
    """Invalidate balance cache keys for a group."""
    await redis_client.delete(f"balances:{group_id}:raw")
    await redis_client.delete(f"balances:{group_id}:simplified")


@router.post("", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    group_id: UUID,
    settlement_data: SettlementCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Create a new settlement in a group."""
    settlement_service = SettlementService(db)
    settlement = await settlement_service.create_settlement(group_id, settlement_data)
    
    # Invalidate balance cache
    await invalidate_balance_cache(redis_client, group_id)
    
    return settlement

