from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    pipefy_pipe_id: str
    pipefy_phase_id: str
    pipefy_field_customer_name: str
    pipefy_field_customer_email: str
    pipefy_field_request_type: str
    pipefy_field_patrimony_value: str
    pipefy_field_status: str
    pipefy_field_priority: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()