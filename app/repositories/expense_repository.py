from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group


class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, expense_data: dict, splits: list[dict]) -> Expense:
        """Create a new expense with splits."""
        expense = Expense(**expense_data)
        self.session.add(expense)
        await self.session.flush()
        
        # Create splits
        for split_data in splits:
            split = ExpenseSplit(expense_id=expense.id, **split_data)
            self.session.add(split)
        
        await self.session.flush()
        
        # Refresh expense with splits loaded
        result = await self.session.execute(
            select(Expense)
            .where(Expense.id == expense.id)
            .options(selectinload(Expense.splits))
        )
        expense = result.scalar_one()
        return expense
    
    async def get_by_id(self, expense_id: UUID) -> Expense | None:
        """Get expense by ID with splits."""
        result = await self.session.execute(
            select(Expense)
            .where(Expense.id == expense_id)
            .options(selectinload(Expense.splits))
        )
        return result.scalar_one_or_none()
    
    async def get_by_group(self, group_id: UUID):
        """Get all expenses for a group."""
        result = await self.session.execute(
            select(Expense)
            .where(Expense.group_id == group_id)
            .options(selectinload(Expense.splits))
            .order_by(Expense.created_at.desc())
        )
        return result.scalars().all()

