from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        name: str,
        email: str,
        request_type: str,
        patrimony_value: Decimal,
        status: str,
    ) -> Customer:
        customer = Customer(
            name=name,
            email=email,
            request_type=request_type,
            patrimony_value=patrimony_value,
            status=status,
        )

        self.db.add(customer)
        self.db.flush()
        self.db.refresh(customer)

        return customer

    def find_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(Customer.email == email)

        return self.db.scalar(statement)

    def update_after_webhook(
        self,
        *,
        customer: Customer,
        status: str,
        priority: str,
        pipefy_card_id: str,
    ) -> Customer:
        customer.status = status
        customer.priority = priority
        customer.pipefy_card_id = pipefy_card_id

        self.db.flush()
        self.db.refresh(customer)

        return customer