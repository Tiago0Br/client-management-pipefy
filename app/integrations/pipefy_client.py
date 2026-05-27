from decimal import Decimal
from typing import Any
from app.core.settings import Settings, settings
from app.domain.enums import CustomerPriority, CustomerStatus
from app.integrations.pipefy_mutations import (
    CREATE_CARD_MUTATION,
    UPDATE_CARD_FIELD_MUTATION,
)

class PipefyClient:
    def __init__(self, app_settings: Settings = settings):
        self.settings = app_settings

    def build_create_card_payload(
        self,
        *,
        customer_name: str,
        customer_email: str,
        request_type: str,
        patrimony_value: Decimal,
    ) -> dict[str, Any]:
        return {
            "query": CREATE_CARD_MUTATION,
            "variables": {
                "input": {
                    "pipe_id": self.settings.pipefy_pipe_id,
                    "phase_id": self.settings.pipefy_phase_id,
                    "title": customer_name,
                    "submitterEmail": customer_email,
                    "fields_attributes": [
                        self._build_field_attribute(
                            field_id=self.settings.pipefy_field_customer_name,
                            field_value=customer_name,
                        ),
                        self._build_field_attribute(
                            field_id=self.settings.pipefy_field_customer_email,
                            field_value=customer_email,
                        ),
                        self._build_field_attribute(
                            field_id=self.settings.pipefy_field_request_type,
                            field_value=request_type,
                        ),
                        self._build_field_attribute(
                            field_id=self.settings.pipefy_field_patrimony_value,
                            field_value=self._format_decimal(patrimony_value),
                        ),
                        self._build_field_attribute(
                            field_id=self.settings.pipefy_field_status,
                            field_value=CustomerStatus.WAITING_ANALYSIS.value,
                        ),
                    ],
                },
            },
        }

    def build_update_card_field_payload(
        self,
        *,
        card_id: str,
        field_id: str,
        new_value: str,
    ) -> dict[str, Any]:
        return {
            "query": UPDATE_CARD_FIELD_MUTATION,
            "variables": {
                "input": {
                    "card_id": card_id,
                    "field_id": field_id,
                    "new_value": new_value,
                },
            },
        }

    def build_update_status_payload(
        self,
        *,
        card_id: str,
        status: CustomerStatus,
    ) -> dict[str, Any]:
        return self.build_update_card_field_payload(
            card_id=card_id,
            field_id=self.settings.pipefy_field_status,
            new_value=status.value,
        )

    def build_update_priority_payload(
        self,
        *,
        card_id: str,
        priority: CustomerPriority,
    ) -> dict[str, Any]:
        return self.build_update_card_field_payload(
            card_id=card_id,
            field_id=self.settings.pipefy_field_priority,
            new_value=priority.value,
        )

    def build_update_status_and_priority_payloads(
        self,
        *,
        card_id: str,
        status: CustomerStatus,
        priority: CustomerPriority,
    ) -> list[dict[str, Any]]:
        return [
            self.build_update_status_payload(
                card_id=card_id,
                status=status,
            ),
            self.build_update_priority_payload(
                card_id=card_id,
                priority=priority,
            ),
        ]

    @staticmethod
    def _build_field_attribute(
        *,
        field_id: str,
        field_value: str,
    ) -> dict[str, str]:
        return {
            "field_id": field_id,
            "field_value": field_value,
        }

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        return format(value, "f")