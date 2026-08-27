"""Application configuration, loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables (or a `.env` file)."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    database_url: str = "sqlite:///./app.db"

    session_secret_key: str = "insecure-dev-secret-change-me"

    oauth_issuer: str = ""
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_redirect_uri: str = "http://localhost:8000/auth/callback"
    oauth_scopes: str = "openid profile email"


settings = Settings()
