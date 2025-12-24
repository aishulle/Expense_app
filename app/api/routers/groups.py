from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.group_repository import GroupRepository
from app.schemas.group import GroupCreate, GroupResponse, GroupMemberCreate

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new group."""
    group_repo = GroupRepository(db)
    group = await group_repo.create(group_data)
    # Reload group with members loaded to avoid lazy-loading issues in async context
    group = await group_repo.get_by_id(group.id, load_members=True)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created group"
        )
    return group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get group by ID with members."""
    group_repo = GroupRepository(db)
    group = await group_repo.get_by_id(group_id, load_members=True)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    return group


@router.post("/{group_id}/members", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def add_group_member(
    group_id: UUID,
    member_data: GroupMemberCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a member to a group."""
    group_repo = GroupRepository(db)
    
    # Check if group exists
    group = await group_repo.get_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )
    
    try:
        await group_repo.add_member(group_id, member_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Return updated group with members
    group = await group_repo.get_by_id(group_id, load_members=True)
    return group

