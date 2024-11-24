import re
from decimal import Decimal
from typing import Optional, Dict, Any

class DataValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        pattern = r'^\+?[\d\s-]{8,}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_decimal(value: str) -> Optional[Decimal]:
        try:
            decimal = Decimal(value)
            return decimal if decimal >= 0 else None
        except:
            return None
            
    @staticmethod
    def validate_integer(value: str) -> Optional[int]:
        try:
            number = int(value)
            return number if number >= 0 else None
        except:
            return None

    @classmethod
    def validate_product(cls, data: Dict[str, Any]) -> list:
        errors = []
        if not data.get('nombre'):
            errors.append("El nombre es requerido")
        if not cls.validate_decimal(data.get('precio', '')):
            errors.append("El precio debe ser un número válido")
        if not cls.validate_integer(data.get('stock', '')):
            errors.append("El stock debe ser un número entero válido")
        return errors