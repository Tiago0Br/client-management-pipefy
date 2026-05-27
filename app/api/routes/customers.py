from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domain.exceptions import CustomerAlreadyExistsError
from app.schemas import CustomerCreateRequest, CustomerCreateResponse
from app.services import CustomerService

router = APIRouter(
    prefix="/clientes",
    tags=["Customers"],
)

@router.post(
    path="",
    response_model=CustomerCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    payload: CustomerCreateRequest,
    db: Session = Depends(get_db),
) -> CustomerCreateResponse:
    customer_service = CustomerService(db)

    try:
        customer = customer_service.create_customer(payload)
    except CustomerAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return customer