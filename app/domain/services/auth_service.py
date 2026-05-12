from app.core.exceptions.response import success_response


class AuthService:
    def __init__(self, repo):
        self.repo = repo

    def create_user(self, full_name: str, email: str, password: str):
        user = self.repo.create_user(
            full_name=full_name, email=email, password=password
        )
        res_data = {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.primary_email,
            "status": user.status,
        }
        return success_response(data=res_data)
