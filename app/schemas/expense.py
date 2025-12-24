from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from app.models.expense import SplitType


class ExpenseSplitCreate(BaseModel):
    user_id: UUID
    amount: Optional[Decimal] = None
    percent: Optional[Decimal] = Field(None, ge=0, le=100)


class ExpenseCreate(BaseModel):
    paid_by_user_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)
    description: str = Field(..., min_length=1, max_length=500)
    split_type: SplitType
    splits: List[ExpenseSplitCreate] = Field(default_factory=list)
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v


class ExpenseSplitResponse(BaseModel):
    user_id: UUID
    amount: Decimal
    percent: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class ExpenseResponse(BaseModel):
    id: UUID
    group_id: UUID
    paid_by_user_id: UUID
    amount: Decimal
    description: str
    split_type: SplitType
    created_at: datetime
    splits: List[ExpenseSplitResponse] = []
    
    class Config:
        from_attributes = True

