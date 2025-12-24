from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.expense import Expense, ExpenseSplit, SplitType
from app.models.group import GroupMember
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.group_repository import GroupRepository
from app.schemas.expense import ExpenseCreate
from app.utils.money import split_equal, round_decimal, distribute_remainder


class ExpenseService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense_repo = ExpenseRepository(session)
        self.group_repo = GroupRepository(session)
    
    async def create_expense(self, group_id: UUID, expense_data: ExpenseCreate) -> Expense:
        """Create an expense with appropriate split logic."""
        # Validate group exists
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Validate paid_by_user_id is a group member
        if not await self.group_repo.is_member(group_id, expense_data.paid_by_user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payer must be a member of the group"
            )
        
        # Process splits based on split type
        splits_data = await self._calculate_splits(
            group_id, expense_data.amount, expense_data.split_type, expense_data.splits
        )
        
        # Create expense
        expense_dict = {
            "group_id": group_id,
            "paid_by_user_id": expense_data.paid_by_user_id,
            "amount": expense_data.amount,
            "description": expense_data.description,
            "split_type": expense_data.split_type,
        }
        
        expense = await self.expense_repo.create(expense_dict, splits_data)
        return expense
    
    async def _calculate_splits(
        self,
        group_id: UUID,
        total_amount: Decimal,
        split_type: SplitType,
        provided_splits: list
    ) -> list[dict]:
        """Calculate expense splits based on split type."""
        # Get all group members
        members_result = await self.session.execute(
            select(GroupMember.user_id).where(GroupMember.group_id == group_id)
        )
        member_ids = [row[0] for row in members_result.all()]
        
        if not member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Group has no members"
            )
        
        splits_data = []
        
        if split_type == SplitType.EQUAL:
            # Use provided participants or all members
            participant_ids = [s.user_id for s in provided_splits] if provided_splits else member_ids
            
            # Validate all participants are group members
            for user_id in participant_ids:
                if user_id not in member_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User {user_id} is not a member of this group"
                    )
            
            # Split equally
            split_amounts = split_equal(total_amount, len(participant_ids))
            
            for i, user_id in enumerate(participant_ids):
                splits_data.append({
                    "user_id": user_id,
                    "amount": split_amounts[i],
                    "percent": None
                })
        
        elif split_type == SplitType.EXACT:
            if not provided_splits:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="EXACT split type requires splits with amounts"
                )
            
            # Validate amounts sum to total
            total_split_amount = sum(
                Decimal(str(s.amount)) for s in provided_splits if s.amount is not None
            )
            
            if abs(total_split_amount - total_amount) > Decimal("0.01"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sum of split amounts ({total_split_amount}) must equal total amount ({total_amount})"
                )
            
            # Validate all participants are group members
            for split in provided_splits:
                if split.user_id not in member_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User {split.user_id} is not a member of this group"
                    )
                if split.amount is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="EXACT split type requires amount for each split"
                    )
                
                splits_data.append({
                    "user_id": split.user_id,
                    "amount": round_decimal(Decimal(str(split.amount))),
                    "percent": None
                })
        
        elif split_type == SplitType.PERCENT:
            if not provided_splits:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PERCENT split type requires splits with percentages"
                )
            
            # Validate percentages sum to 100
            total_percent = sum(
                Decimal(str(s.percent)) for s in provided_splits if s.percent is not None
            )
            
            if abs(total_percent - Decimal("100")) > Decimal("0.01"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sum of percentages ({total_percent}) must equal 100"
                )
            
            # Validate all participants are group members
            for split in provided_splits:
                if split.user_id not in member_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"User {split.user_id} is not a member of this group"
                    )
                if split.percent is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="PERCENT split type requires percent for each split"
                    )
            
            # Calculate amounts from percentages
            percent_amounts = []
            for split in provided_splits:
                percent_decimal = Decimal(str(split.percent))
                amount = (total_amount * percent_decimal) / Decimal("100")
                percent_amounts.append((split.user_id, amount))
            
            # Distribute remainder fairly
            amounts_list = [amt for _, amt in percent_amounts]
            distributed_amounts = distribute_remainder(total_amount, amounts_list)
            
            for i, (user_id, _) in enumerate(percent_amounts):
                splits_data.append({
                    "user_id": user_id,
                    "amount": distributed_amounts[i],
                    "percent": round_decimal(Decimal(str(provided_splits[i].percent)), 2)
                })
        
        return splits_data

