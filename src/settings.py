from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./moeda_estudantil.db"
    session_secret: str = "dev-only-change-this-secret"
    session_hours: int = 8
    cookie_secure: bool = False
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    admin_token: str = ""
    password_iterations: int = 600_000

    upload_dir: str = "uploads"
    max_upload_bytes: int = 2 * 1024 * 1024

    mail_host: str = ""
    mail_port: int = 2525
    mail_user: str = ""
    mail_password: str = ""
    mail_from: str = "Moeda Estudantil <noreply@moeda.local>"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
