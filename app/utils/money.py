from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple


def round_decimal(value: Decimal, decimal_places: int = 2) -> Decimal:
    """Round decimal to specified decimal places."""
    quantize_str = "0." + "0" * decimal_places
    return value.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)


def distribute_remainder(
    total_amount: Decimal,
    amounts: List[Decimal],
    decimal_places: int = 2
) -> List[Decimal]:
    """
    Distribute remainder fairly after rounding.
    Adds the remainder (if any) to the first few amounts.
    """
    rounded_amounts = [round_decimal(amt, decimal_places) for amt in amounts]
    rounded_sum = sum(rounded_amounts)
    remainder = total_amount - rounded_sum
    
    if remainder == 0:
        return rounded_amounts
    
    # Distribute remainder in smallest increments
    quantize_str = "0." + "0" * decimal_places
    increment = Decimal("0." + "0" * (decimal_places - 1) + "1")
    
    index = 0
    while remainder != 0 and index < len(rounded_amounts):
        rounded_amounts[index] += increment
        rounded_amounts[index] = round_decimal(rounded_amounts[index], decimal_places)
        remainder -= increment
        index += 1
    
    return rounded_amounts


def split_equal(
    total_amount: Decimal,
    num_people: int,
    decimal_places: int = 2
) -> List[Decimal]:
    """Split amount equally among people with fair remainder distribution."""
    if num_people == 0:
        return []
    
    per_person = total_amount / Decimal(num_people)
    amounts = [per_person] * num_people
    
    return distribute_remainder(total_amount, amounts, decimal_places)

