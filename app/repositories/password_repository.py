from abc import ABC, abstractmethod
import hashlib
import bcrypt


class IPasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(
        self, password: str, db_password: str
    ) -> bool:
        pass


class PasswordHasher(IPasswordHasher):
    def hash_password(self, password: str) -> str:
        sha = hashlib.sha256(password.encode()).digest()
        return bcrypt.hashpw(sha, bcrypt.gensalt()).decode()

    def verify_password(
        self, password: str, db_password: str
    ) -> bool:
        sha = hashlib.sha256(password.encode()).digest()
        return bcrypt.checkpw(sha, db_password.encode())
