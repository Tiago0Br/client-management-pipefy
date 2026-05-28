from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domain.exceptions import CustomerNotFoundError
from app.schemas import (
    PipefyCardUpdatedWebhookRequest,
    PipefyCardUpdatedWebhookResponse,
)
from app.services import WebhookService

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]

@router.post(
    "/pipefy/card-updated",
    response_model=PipefyCardUpdatedWebhookResponse,
    status_code=status.HTTP_200_OK,
)
def process_pipefy_card_updated_webhook(
    payload: PipefyCardUpdatedWebhookRequest,
    db: DatabaseSession,
) -> PipefyCardUpdatedWebhookResponse:
    webhook_service = WebhookService(db)

    try:
        return webhook_service.process_card_updated(payload)
    except CustomerNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error