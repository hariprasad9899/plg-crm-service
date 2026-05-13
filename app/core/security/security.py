from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def hash_value(value: str) -> str:
    return password_hash.hash(value)


def verify_hash(plain_value: str, hash_value: str) -> bool:
    return password_hash.verify(plain_value, hash_value)
