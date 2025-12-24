from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.settlement import Settlement


class SettlementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, settlement_data: dict) -> Settlement:
        """Create a new settlement."""
        settlement = Settlement(**settlement_data)
        self.session.add(settlement)
        await self.session.flush()
        await self.session.refresh(settlement)
        return settlement
    
    async def get_by_id(self, settlement_id: UUID) -> Settlement | None:
        """Get settlement by ID."""
        return await self.session.get(Settlement, settlement_id)
    
    async def get_by_group(self, group_id: UUID):
        """Get all settlements for a group."""
        result = await self.session.execute(
            select(Settlement)
            .where(Settlement.group_id == group_id)
            .order_by(Settlement.created_at.desc())
        )
        return result.scalars().all()

