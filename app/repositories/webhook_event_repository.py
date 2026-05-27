from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import WebhookEvent

class WebhookEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_event_id(self, event_id: str) -> WebhookEvent | None:
        statement = select(WebhookEvent).where(WebhookEvent.event_id == event_id)

        return self.db.scalar(statement)

    def exists_by_event_id(self, event_id: str) -> bool:
        event = self.find_by_event_id(event_id)

        return event is not None

    def create(
        self,
        *,
        event_id: str,
        card_id: str,
        customer_email: str,
        event_timestamp: datetime,
    ) -> WebhookEvent:
        webhook_event = WebhookEvent(
            event_id=event_id,
            card_id=card_id,
            customer_email=customer_email,
            event_timestamp=event_timestamp,
        )

        self.db.add(webhook_event)
        self.db.flush()
        self.db.refresh(webhook_event)

        return webhook_event