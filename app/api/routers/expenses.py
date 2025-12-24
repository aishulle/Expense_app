from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.services.expense_service import ExpenseService
from app.schemas.expense import ExpenseCreate, ExpenseResponse

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


async def invalidate_balance_cache(redis_client: redis.Redis, group_id: UUID):
    """Invalidate balance cache keys for a group."""
    await redis_client.delete(f"balances:{group_id}:raw")
    await redis_client.delete(f"balances:{group_id}:simplified")


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    group_id: UUID,
    expense_data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Create a new expense in a group."""
    expense_service = ExpenseService(db)
    expense = await expense_service.create_expense(group_id, expense_data)
    
    # Invalidate balance cache
    await invalidate_balance_cache(redis_client, group_id)
    
    return expense

