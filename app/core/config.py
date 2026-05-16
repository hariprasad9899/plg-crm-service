from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    database_url: str
    google_oauth_url: str
    jwt_secret_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    environment: str

    @property
    def get_token_url(self) -> str:
        return f"{self.google_oauth_url}/token"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    class Config:
        env_file = ".env"
