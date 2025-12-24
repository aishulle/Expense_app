from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.expense import Expense, ExpenseSplit
from app.models.settlement import Settlement
from app.repositories.group_repository import GroupRepository
from app.utils.balance_simplification import calculate_net_balances, simplify_balances
from app.utils.money import round_decimal
import json


class BalanceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.group_repo = GroupRepository(session)
    
    async def get_raw_balances(self, group_id: UUID) -> list[dict]:
        """Get raw balances (ledger-style) for a group."""
        # Validate group exists
        group = await self.group_repo.get_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group {group_id} not found"
            )
        
        # Get all expenses with splits
        expenses_result = await self.session.execute(
            select(Expense, ExpenseSplit)
            .join(ExpenseSplit, Expense.id == ExpenseSplit.expense_id)
            .where(Expense.group_id == group_id)
        )
        
        # Build raw balances from expenses
        raw_balances: dict[tuple[UUID, UUID], Decimal] = {}
        
        for expense, split in expenses_result.all():
            # Who paid (creditor) vs who owes (debtor)
            # If user is in split but didn't pay, they owe the payer
            if split.user_id != expense.paid_by_user_id:
                key = (split.user_id, expense.paid_by_user_id)
                raw_balances[key] = raw_balances.get(key, Decimal("0")) + Decimal(str(split.amount))
            # If user paid more than their share, they are owed by others
            # This is already handled by the splits above
        
        # Apply settlements (reduce balances)
        settlements_result = await self.session.execute(
            select(Settlement).where(Settlement.group_id == group_id)
        )
        settlements = settlements_result.scalars().all()
        
        for settlement in settlements:
            # Settlement: payer pays payee, so payer owes less, payee is owed less
            key = (settlement.payer_id, settlement.payee_id)
            raw_balances[key] = raw_balances.get(key, Decimal("0")) - Decimal(str(settlement.amount))
            
            # Remove zero or negative balances (settlement can reverse debt)
            if raw_balances[key] <= 0:
                raw_balances.pop(key, None)
        
        # Convert to list format
        result = []
        for (debtor_id, creditor_id), amount in raw_balances.items():
            if amount > 0:
                result.append({
                    "debtor_id": str(debtor_id),
                    "creditor_id": str(creditor_id),
                    "amount": float(round_decimal(amount, 2))
                })
        
        return result
    
    async def get_simplified_balances(self, group_id: UUID) -> list[dict]:
        """Get simplified balances for a group."""
        raw_balances = await self.get_raw_balances(group_id)
        simplified = simplify_balances(calculate_net_balances(raw_balances))
        
        # Convert amounts back to Decimal format for response
        result = []
        for transfer in simplified:
            result.append({
                "payer_id": transfer["payer_id"],
                "payee_id": transfer["payee_id"],
                "amount": Decimal(str(transfer["amount"]))
            })
        
        return result

