from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.enums import CustomerStatus, PipefyOperation
from app.domain.exceptions import CustomerNotFoundError
from app.domain.rules import calculate_customer_priority
from app.integrations import PipefyClient
from app.repositories import (
    CustomerRepository,
    PipefyRequestRepository,
    WebhookEventRepository,
)
from app.schemas import (
    PipefyCardUpdatedWebhookRequest,
    PipefyCardUpdatedWebhookResponse,
)


class WebhookService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repository = CustomerRepository(db)
        self.webhook_event_repository = WebhookEventRepository(db)
        self.pipefy_request_repository = PipefyRequestRepository(db)
        self.pipefy_client = PipefyClient()

    def process_card_updated(
        self,
        data: PipefyCardUpdatedWebhookRequest,
    ) -> PipefyCardUpdatedWebhookResponse:
        normalized_email = str(data.customer_email).lower()

        already_processed = self.webhook_event_repository.exists_by_event_id(
            data.event_id,
        )

        if already_processed:
            return PipefyCardUpdatedWebhookResponse(
                message="Webhook event already processed.",
                already_processed=True,
                customer_email=normalized_email,
            )

        customer = self.customer_repository.find_by_email(normalized_email)

        if customer is None:
            raise CustomerNotFoundError(normalized_email)

        priority = calculate_customer_priority(customer.patrimony_value)

        try:
            payloads = self.pipefy_client.build_update_status_and_priority_payloads(
                card_id=data.card_id,
                status=CustomerStatus.PROCESSED,
                priority=priority,
            )

            for payload in payloads:
                self.pipefy_request_repository.create(
                    operation=PipefyOperation.UPDATE_CARD_FIELD.value,
                    payload_json=payload,
                )

            updated_customer = self.customer_repository.update_after_webhook(
                customer=customer,
                status=CustomerStatus.PROCESSED.value,
                priority=priority.value,
                pipefy_card_id=data.card_id,
            )

            self.webhook_event_repository.create(
                event_id=data.event_id,
                card_id=data.card_id,
                customer_email=normalized_email,
                event_timestamp=data.timestamp,
            )

            self.db.commit()
            self.db.refresh(updated_customer)

            return PipefyCardUpdatedWebhookResponse(
                message="Webhook event processed successfully.",
                already_processed=False,
                customer_email=updated_customer.email,
                status=CustomerStatus(updated_customer.status),
                priority=priority,
            )

        except IntegrityError:
            self.db.rollback()

            return PipefyCardUpdatedWebhookResponse(
                message="Webhook event already processed.",
                already_processed=True,
                customer_email=normalized_email,
            )

        except Exception:
            self.db.rollback()
            raise