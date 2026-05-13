from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    database_url: str
    google_oauth_url: str
    jwt_secret_key: str
    aws_access_key_id: str
    aws_secret_access_key: str

    @property
    def get_token_url(self) -> str:
        return f"{self.google_oauth_url}/token"

    class Config:
        env_file = ".env"
