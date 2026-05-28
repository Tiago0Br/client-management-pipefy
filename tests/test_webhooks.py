from app.core.settings import settings
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.domain.enums import CustomerPriority, CustomerStatus, PipefyOperation
from app.models import Customer, PipefyRequest, WebhookEvent

def test_webhook_processes_high_priority_customer(
    client: TestClient,
    db_session: Session,
    create_customer_in_database: Customer,
    pipefy_webhook_payload: dict[str, str],
) -> None:
    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=pipefy_webhook_payload,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["message"] == "Webhook event processed successfully."
    assert response_data["already_processed"] is False
    assert response_data["customer_email"] == "joao.silva@example.com"
    assert response_data["status"] == CustomerStatus.PROCESSED.value
    assert response_data["priority"] == CustomerPriority.HIGH.value

    customer = db_session.scalar(
        select(Customer).where(Customer.email == "joao.silva@example.com")
    )

    assert customer is not None
    assert customer.status == CustomerStatus.PROCESSED.value
    assert customer.priority == CustomerPriority.HIGH.value
    assert customer.pipefy_card_id == "card_456"

    webhook_event = db_session.scalar(
        select(WebhookEvent).where(WebhookEvent.event_id == "evt_123")
    )

    assert webhook_event is not None
    assert webhook_event.card_id == "card_456"
    assert webhook_event.customer_email == "joao.silva@example.com"

    pipefy_requests = db_session.scalars(
        select(PipefyRequest).where(
            PipefyRequest.operation == PipefyOperation.UPDATE_CARD_FIELD.value
        )
    ).all()

    assert len(pipefy_requests) == 2

    payloads = [request.payload_json for request in pipefy_requests]

    assert any(
        payload["variables"]["input"]["field_id"] == settings.pipefy_field_status
        and payload["variables"]["input"]["new_value"] == CustomerStatus.PROCESSED.value
        for payload in payloads
    )

    assert any(
        payload["variables"]["input"]["field_id"] == settings.pipefy_field_priority
        and payload["variables"]["input"]["new_value"] == CustomerPriority.HIGH.value
        for payload in payloads
    )

def test_webhook_processes_normal_priority_customer(
    client: TestClient,
    db_session: Session,
    normal_patrimony_customer_payload: dict[str, object],
) -> None:
    create_customer_response = client.post(
        "/clientes",
        json=normal_patrimony_customer_payload,
    )

    assert create_customer_response.status_code == 201

    webhook_payload = {
        "event_id": "evt_normal_priority",
        "card_id": "card_normal_priority",
        "cliente_email": "carlos.souza@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=webhook_payload,
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["already_processed"] is False
    assert response_data["status"] == CustomerStatus.PROCESSED.value
    assert response_data["priority"] == CustomerPriority.NORMAL.value

    customer = db_session.scalar(
        select(Customer).where(Customer.email == "carlos.souza@example.com")
    )

    assert customer is not None
    assert customer.status == CustomerStatus.PROCESSED.value
    assert customer.priority == CustomerPriority.NORMAL.value
    assert customer.pipefy_card_id == "card_normal_priority"

def test_webhook_duplicate_event_id_is_not_processed_twice(
    client: TestClient,
    db_session: Session,
    create_customer_in_database: Customer,
    pipefy_webhook_payload: dict[str, str],
) -> None:
    first_response = client.post(
        "/webhooks/pipefy/card-updated",
        json=pipefy_webhook_payload,
    )

    second_response = client.post(
        "/webhooks/pipefy/card-updated",
        json=pipefy_webhook_payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_response_data = first_response.json()
    second_response_data = second_response.json()

    assert first_response_data["already_processed"] is False
    assert second_response_data["already_processed"] is True
    assert second_response_data["message"] == "Webhook event already processed."

    webhook_events_count = db_session.scalar(
        select(func.count()).select_from(WebhookEvent)
    )

    update_card_field_requests_count = db_session.scalar(
        select(func.count())
        .select_from(PipefyRequest)
        .where(PipefyRequest.operation == PipefyOperation.UPDATE_CARD_FIELD.value)
    )

    assert webhook_events_count == 1
    assert update_card_field_requests_count == 2

def test_webhook_for_nonexistent_customer_returns_404(
    client: TestClient,
) -> None:
    webhook_payload = {
        "event_id": "evt_customer_not_found",
        "card_id": "card_customer_not_found",
        "cliente_email": "unknown.customer@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }

    response = client.post(
        "/webhooks/pipefy/card-updated",
        json=webhook_payload,
    )

    assert response.status_code == 404
    assert "unknown.customer@example.com" in response.json()["detail"]