from pydantic import BaseModel
from decimal import Decimal


class RawBalanceResponse(BaseModel):
    debtor_id: str
    creditor_id: str
    amount: Decimal


class SimplifiedBalanceResponse(BaseModel):
    payer_id: str
    payee_id: str
    amount: Decimal

