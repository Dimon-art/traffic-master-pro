"""Конфигурация приложения из переменных окружения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения TrafficMaster Pro."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    postgres_user: str = "trainer"
    postgres_password: str = "change_me"
    postgres_db: str = "traffic_master"
    postgres_host: str = "db"
    postgres_port: int = 5432
    redis_url: str = "redis://redis:6379/0"
    openai_model: str = "gpt-4o-mini"
    sheets_leads_id: str = ""
    sheets_history_id: str = ""
    sheets_cp_archive_id: str = ""
    sheets_calls_id: str = ""
    gdrive_backup_folder_id: str = ""
    knowledge_base_path: str = "/app/knowledge_base"

    @property
    def database_url(self) -> str:
        """Собирает URL подключения к PostgreSQL для SQLAlchemy.

        Returns:
            Строка подключения в формате ``postgresql+psycopg2``.
        """
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
