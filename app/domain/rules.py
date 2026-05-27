from decimal import Decimal
from app.domain.enums import CustomerPriority

HIGH_PRIORITY_MINIMUM_PATRIMONY = Decimal("200000")

def calculate_customer_priority(patrimony_value: Decimal) -> CustomerPriority:
    if patrimony_value >= HIGH_PRIORITY_MINIMUM_PATRIMONY:
        return CustomerPriority.HIGH

    return CustomerPriority.NORMAL