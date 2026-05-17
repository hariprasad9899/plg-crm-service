import requests
from fastapi import HTTPException
from app.core.config import Settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_request
from app.core.config import Settings
from app.core.exceptions.handler import AppException
from app.core.exceptions.error_catalog import INVALID_GOOGLE_TOKEN, GENERIC_EXCEPTION


class GoogleOAuthService:

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def exchange_code(self, code: str):
        settings = Settings()
        token_payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "postmessage",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = requests.post(
                settings.get_token_url, data=token_payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise AppException(GENERIC_EXCEPTION)

    def verify_google_id_token(self, token: str):
        settings = Settings()
        try:
            id_info = id_token.verify_oauth2_token(
                token, google_request.Request(), settings.google_client_id
            )

            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise AppException(INVALID_GOOGLE_TOKEN)
            return id_info
        except ValueError:
            raise AppException(INVALID_GOOGLE_TOKEN)
