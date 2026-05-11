from sqlalchemy.orm import Session
from app.domain.ports.auth_ports import AuthPort
from app.infrastructure.database.models.auth_models import User, UserStatusEnum


class AuthRepo(AuthPort):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, full_name: str, email: str, password: str):
        user = User(
            full_name=full_name,
            primary_email=email,
            status=UserStatusEnum.ACTIVE,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
