from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class SettlementCreate(BaseModel):
    payer_id: UUID
    payee_id: UUID
    amount: Decimal = Field(..., gt=0, decimal_places=2, max_digits=12)


class SettlementResponse(BaseModel):
    id: UUID
    group_id: UUID
    payer_id: UUID
    payee_id: UUID
    amount: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

