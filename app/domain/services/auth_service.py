class AuthService:
    def __init__(self, repo):
        self.repo = repo

    def create_user(self, full_name: str, email: str, password: str):
        user = self.repo.create_user(
            full_name=full_name, email=email, password=password
        )
        return {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.primary_email,
            "status": user.status,
        }
