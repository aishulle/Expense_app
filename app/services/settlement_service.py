from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.repositories.settlement_repository import SettlementRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.settlement import SettlementCreate
from app.utils.money import round_decimal


class SettlementService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settlement_repo = SettlementRepository(session)
        self.group_repo = GroupRepository(session)
    
    async def create_settlement(
        self, group_id: UUID, settlement_data: SettlementCreate
    ) -> dict:
        """Create a settlement and invalidate balance cache."""
        # Validate group exists
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Validate payer and payee are different
        if settlement_data.payer_id == settlement_data.payee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payer and payee must be different"
            )
        
        # Validate payer is a group member
        if not await self.group_repo.is_member(group_id, settlement_data.payer_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payer must be a member of the group"
            )
        
        # Validate payee is a group member
        if not await self.group_repo.is_member(group_id, settlement_data.payee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payee must be a member of the group"
            )
        
        # Validate amount > 0
        if settlement_data.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Settlement amount must be greater than 0"
            )
        
        # Round amount to 2 decimal places
        rounded_amount = round_decimal(Decimal(str(settlement_data.amount)))
        
        # Create settlement
        settlement_dict = {
            "group_id": group_id,
            "payer_id": settlement_data.payer_id,
            "payee_id": settlement_data.payee_id,
            "amount": rounded_amount,
        }
        
        settlement = await self.settlement_repo.create(settlement_dict)
        return settlement

