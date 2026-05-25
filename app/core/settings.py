from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str

    pipefy_pipe_id: str
    pipefy_phase_id: str

    pipefy_field_cliente_nome: str
    pipefy_field_cliente_email: str
    pipefy_field_tipo_solicitacao: str
    pipefy_field_valor_patrimonio: str
    pipefy_field_status: str
    pipefy_field_prioridade: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()