from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domain.enums import CustomerStatus, PipefyOperation
from app.models import Customer, PipefyRequest

def test_create_customer_with_valid_payload(
    client: TestClient,
    db_session: Session,
    valid_customer_payload: dict[str, object],
) -> None:
    response = client.post("/clientes", json=valid_customer_payload)

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] is not None
    assert response_data["name"] == "João Silva"
    assert response_data["email"] == "joao.silva@example.com"
    assert response_data["request_type"] == "Atualização cadastral"
    assert response_data["status"] == CustomerStatus.WAITING_ANALYSIS.value
    assert response_data["priority"] is None
    assert response_data["pipefy_card_id"] is None

    customer = db_session.scalar(
        select(Customer).where(Customer.email == "joao.silva@example.com")
    )

    assert customer is not None
    assert customer.name == "João Silva"
    assert customer.status == CustomerStatus.WAITING_ANALYSIS.value

    pipefy_request = db_session.scalar(select(PipefyRequest))

    assert pipefy_request is not None
    assert pipefy_request.operation == PipefyOperation.CREATE_CARD.value
    assert "createCard" in pipefy_request.payload_json["query"]

    payload_input = pipefy_request.payload_json["variables"]["input"]

    assert payload_input["title"] == "João Silva"
    assert payload_input["submitterEmail"] == "joao.silva@example.com"