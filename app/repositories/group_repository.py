from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.group import Group, GroupMember
from app.models.user import User
from app.schemas.group import GroupCreate, GroupMemberCreate


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, group_data: GroupCreate) -> Group:
        """Create a new group."""
        group = Group(**group_data.model_dump())
        self.session.add(group)
        await self.session.flush()
        await self.session.refresh(group)
        return group
    
    async def get_by_id(self, group_id: UUID, load_members: bool = False) -> Group | None:
        """Get group by ID."""
        query = select(Group).where(Group.id == group_id)
        if load_members:
            query = query.options(selectinload(Group.members).selectinload(GroupMember.user))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def add_member(self, group_id: UUID, member_data: GroupMemberCreate) -> GroupMember:
        """Add a member to a group."""
        # Check if user exists
        user = await self.session.get(User, member_data.user_id)
        if not user:
            raise ValueError(f"User {member_data.user_id} not found")
        
        # Check if already a member
        existing = await self.session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == member_data.user_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"User {member_data.user_id} is already a member of this group")
        
        member = GroupMember(group_id=group_id, user_id=member_data.user_id)
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member
    
    async def get_members(self, group_id: UUID):
        """Get all members of a group."""
        result = await self.session.execute(
            select(GroupMember)
            .where(GroupMember.group_id == group_id)
            .options(selectinload(GroupMember.user))
        )
        return result.scalars().all()
    
    async def is_member(self, group_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of the group."""
        result = await self.session.execute(
            select(GroupMember).where(
                GroupMember.group_id == group_id,
                GroupMember.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None

