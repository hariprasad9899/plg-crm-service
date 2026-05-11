from abc import ABC, abstractmethod


class AuthPort(ABC):

    @abstractmethod
    def create_user(self, full_name: str, email: str, password: str):
        pass
