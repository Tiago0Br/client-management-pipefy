from enum import StrEnum


class CustomerStatus(StrEnum):
    WAITING_ANALYSIS = "Aguardando Análise"
    PROCESSED = "Processado"

class CustomerPriority(StrEnum):
    HIGH = "prioridade_alta"
    NORMAL = "prioridade_normal"

class PipefyOperation(StrEnum):
    CREATE_CARD = "createCard"
    UPDATE_CARD_FIELD = "updateCardField"