from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.domain.enums import CustomerPriority, CustomerStatus

class CustomerCreateRequest(BaseModel):
    name: str = Field(
        alias="cliente_nome",
        min_length=1,
        max_length=255,
    )
    email: EmailStr = Field(alias="cliente_email")
    request_type: str = Field(
        alias="tipo_solicitacao",
        min_length=1,
        max_length=255,
    )
    patrimony_value: Decimal = Field(
        alias="valor_patrimonio",
        ge=0,
    )

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

class CustomerCreateResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    request_type: str
    patrimony_value: Decimal
    status: CustomerStatus
    priority: CustomerPriority | None = None
    pipefy_card_id: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    request_type: str
    patrimony_value: Decimal
    status: CustomerStatus
    priority: CustomerPriority | None = None
    pipefy_card_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)