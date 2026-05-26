from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.domain.enums import CustomerPriority, CustomerStatus

class PipefyCardUpdatedWebhookRequest(BaseModel):
    event_id: str = Field(min_length=1, max_length=255)
    card_id: str = Field(min_length=1, max_length=255)
    customer_email: EmailStr = Field(alias="cliente_email")
    timestamp: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

class PipefyCardUpdatedWebhookResponse(BaseModel):
    message: str
    already_processed: bool
    customer_email: EmailStr
    status: CustomerStatus | None = None
    priority: CustomerPriority | None = None