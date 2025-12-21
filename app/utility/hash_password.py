import hashlib

import bcrypt


def hash_password(password: str) -> str:
    sha = hashlib.sha256(password.encode()).digest()
    return bcrypt.hashpw(sha, bcrypt.gensalt()).decode()


def verify_password(user_password: str, db_password: str) -> bool:
    sha = hashlib.sha256(user_password.encode()).digest()
    return bcrypt.checkpw(sha, db_password.encode())
