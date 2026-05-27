from typing import Any
from sqlalchemy.orm import Session
from app.models import PipefyRequest

class PipefyRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        operation: str,
        payload_json: dict[str, Any],
    ) -> PipefyRequest:
        pipefy_request = PipefyRequest(
            operation=operation,
            payload_json=payload_json,
        )

        self.db.add(pipefy_request)
        self.db.flush()
        self.db.refresh(pipefy_request)

        return pipefy_request