import requests as http_requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from app.core.exceptions.handler import AppException
from app.core.exceptions.error_catalog import INVALID_GOOGLE_TOKEN, GENERIC_EXCEPTION


class GoogleOAuthService:

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def exchange_code(self, code: str):
        token_payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "postmessage",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = http_requests.post(
                settings.get_token_url, data=token_payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except http_requests.HTTPError as e:
            print("HTTP ERROR", e.response.json())
            raise AppException(GENERIC_EXCEPTION)
        except http_requests.RequestException as e:
            print("REQUEST ERROR", e)
            raise AppException(GENERIC_EXCEPTION)

    def verify_google_id_token(self, token: str):
        try:
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.google_client_id,
            )
            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise AppException(INVALID_GOOGLE_TOKEN)
            return id_info
        except ValueError:
            raise AppException(INVALID_GOOGLE_TOKEN)
