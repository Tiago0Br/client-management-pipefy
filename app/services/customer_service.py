from sqlalchemy.exc import IntegrityError
from app.domain.exceptions import CustomerAlreadyExistsError
from sqlalchemy.orm import Session
from app.domain.enums import CustomerStatus, PipefyOperation
from app.integrations import PipefyClient
from app.models import Customer
from app.repositories import CustomerRepository, PipefyRequestRepository
from app.schemas import CustomerCreateRequest

class CustomerService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repository = CustomerRepository(db)
        self.pipefy_request_repository = PipefyRequestRepository(db)
        self.pipefy_client = PipefyClient()

    def create_customer(self, data: CustomerCreateRequest) -> Customer:
        normalized_email = str(data.email).lower()
        existing_customer = self.customer_repository.find_by_email(normalized_email)

        if existing_customer is not None:
            raise CustomerAlreadyExistsError(normalized_email)

        try:
            customer = self.customer_repository.create(
                name=data.name,
                email=normalized_email,
                request_type=data.request_type,
                patrimony_value=data.patrimony_value,
                status=CustomerStatus.WAITING_ANALYSIS.value,
            )

            create_card_payload = self.pipefy_client.build_create_card_payload(
                customer_name=customer.name,
                customer_email=customer.email,
                request_type=customer.request_type,
                patrimony_value=customer.patrimony_value,
            )

            self.pipefy_request_repository.create(
                operation=PipefyOperation.CREATE_CARD.value,
                payload_json=create_card_payload,
            )

            self.db.commit()
            self.db.refresh(customer)

            return customer
        
        except IntegrityError as error:
            self.db.rollback()
            raise CustomerAlreadyExistsError(normalized_email) from error

        except Exception:
            self.db.rollback()
            raise