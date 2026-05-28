from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.domain.enums import CustomerStatus
from app.main import app
from app.models import Customer

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_customer_payload() -> dict[str, object]:
    return {
        "cliente_nome": "João Silva",
        "cliente_email": "joao.silva@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000,
    }


@pytest.fixture
def high_patrimony_customer_payload() -> dict[str, object]:
    return {
        "cliente_nome": "Maria Oliveira",
        "cliente_email": "maria.oliveira@example.com",
        "tipo_solicitacao": "Atualização cadastral",
        "valor_patrimonio": 250000,
    }


@pytest.fixture
def normal_patrimony_customer_payload() -> dict[str, object]:
    return {
        "cliente_nome": "Carlos Souza",
        "cliente_email": "carlos.souza@example.com",
        "tipo_solicitacao": "Nova solicitação",
        "valor_patrimonio": 150000,
    }


@pytest.fixture
def pipefy_webhook_payload() -> dict[str, str]:
    return {
        "event_id": "evt_123",
        "card_id": "card_456",
        "cliente_email": "joao.silva@example.com",
        "timestamp": "2026-05-18T12:00:00Z",
    }


@pytest.fixture
def create_customer_in_database(db_session: Session) -> Customer:
    customer = Customer(
        name="João Silva",
        email="joao.silva@example.com",
        request_type="Atualização cadastral",
        patrimony_value=Decimal("250000"),
        status=CustomerStatus.WAITING_ANALYSIS.value,
    )

    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)

    return customer