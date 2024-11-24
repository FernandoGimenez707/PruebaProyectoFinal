import jwt
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Optional, Dict
from db_utils import db_operation
from utils.error_handler import handle_exceptions

class AuthManager:
    SECRET_KEY = secrets.token_hex(32)
    TOKEN_EXPIRY = timedelta(hours=8)

    @handle_exceptions("Authentication")
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        hashed_password = self._hash_password(password)
        with db_operation() as cursor:
            cursor.execute(
                "SELECT id, username, role FROM usuarios WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            user = cursor.fetchone()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'token': self._generate_token(user)
                }
        return None

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()

    def _generate_token(self, user) -> str:
        return jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + self.TOKEN_EXPIRY
        }, self.SECRET_KEY, algorithm='HS256')
