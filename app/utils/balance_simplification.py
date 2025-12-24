from decimal import Decimal
from typing import Dict, List, Tuple
from uuid import UUID


def calculate_net_balances(
    raw_balances: List[Dict[str, any]]
) -> Dict[UUID, Decimal]:
    """
    Calculate net balance for each user from raw balances.
    Positive = user is owed money, Negative = user owes money.
    """
    net_balances: Dict[UUID, Decimal] = {}
    
    for balance in raw_balances:
        debtor_id = UUID(balance["debtor_id"])
        creditor_id = UUID(balance["creditor_id"])
        amount = Decimal(str(balance["amount"]))
        
        # Debtor owes (negative balance)
        net_balances[debtor_id] = net_balances.get(debtor_id, Decimal("0")) - amount
        # Creditor is owed (positive balance)
        net_balances[creditor_id] = net_balances.get(creditor_id, Decimal("0")) + amount
    
    return net_balances


def simplify_balances(net_balances: Dict[UUID, Decimal]) -> List[Dict[str, any]]:
    """
    Simplify balances using greedy matching algorithm.
    Returns list of transfers: payer_id -> payee_id -> amount.
    Only positive amounts, no zero transfers.
    """
    # Separate debtors (negative) and creditors (positive)
    debtors = [
        (user_id, abs(amount))
        for user_id, amount in net_balances.items()
        if amount < 0
    ]
    creditors = [
        (user_id, amount)
        for user_id, amount in net_balances.items()
        if amount > 0
    ]
    
    # Sort: largest debts first
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    transfers = []
    debtor_idx = 0
    creditor_idx = 0
    
    while debtor_idx < len(debtors) and creditor_idx < len(creditors):
        debtor_id, debt_remaining = debtors[debtor_idx]
        creditor_id, credit_remaining = creditors[creditor_idx]
        
        # Amount to transfer is the minimum of what debtor owes and creditor is owed
        transfer_amount = min(debt_remaining, credit_remaining)
        
        if transfer_amount > 0:
            transfers.append({
                "payer_id": str(debtor_id),
                "payee_id": str(creditor_id),
                "amount": float(transfer_amount)
            })
            
            # Update remaining amounts
            debt_remaining -= transfer_amount
            credit_remaining -= transfer_amount
            
            debtors[debtor_idx] = (debtor_id, debt_remaining)
            creditors[creditor_idx] = (creditor_id, credit_remaining)
        
        # Move to next debtor if fully paid
        if debt_remaining == 0:
            debtor_idx += 1
        
        # Move to next creditor if fully paid
        if credit_remaining == 0:
            creditor_idx += 1
    
    return transfers

