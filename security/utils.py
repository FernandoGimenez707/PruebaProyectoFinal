import re
from typing import Any
import secrets
from functools import wraps

class SecurityUtils:
    @staticmethod
    def sanitize_input(value: Any) -> str:
        if not isinstance(value, str):
            return value
        return re.sub(r'[<>"/\'%;()&+]', '', value)

    @staticmethod
    def generate_secure_filename(filename: str) -> str:
        name, ext = filename.rsplit('.', 1)
        return f"{re.sub(r'[^a-zA-Z0-9]', '_', name)}_{secrets.token_hex(8)}.{ext}"

    @staticmethod
    def validate_password(password: str) -> bool:
        return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password))

def requires_auth(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'session') or not self.session.validate_session():
            raise PermissionError("Unauthorized access")
        return f(self, *args, **kwargs)
    return wrapper
