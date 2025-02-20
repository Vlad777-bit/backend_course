from pydantic import BaseModel, EmailStr, field_validator
from datetime import date, datetime
import re

class Contact(BaseModel):
    last_name: str
    first_name: str
    date_of_birth: date
    phone: str
    email: EmailStr

    @field_validator("last_name", "first_name")
    def validate_names(cls, v):
        if not v or not v[0].isupper():
            raise ValueError("Имя и фамилия должны начинаться с заглавной буквы.")

        if not re.fullmatch(r"[А-ЯЁ][а-яё]+", v):
            raise ValueError("Имя и фамилия должны содержать только кириллицу.")
        return v

    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.fullmatch(r"\+?\d{10,15}", v):
            raise ValueError("Номер телефона должен содержать от 10 до 15 цифр, с необязательным знаком + в начале.")
        return v


class ExtendedContact(Contact):
    reason: str
    detected_at: datetime

    @field_validator("reason")
    def validate_reason(cls, value):
        allowed = ["нет доступа к сети", "не работает телефон", "не приходят письма"]
        if value not in allowed:
            raise ValueError(
                "Причина обращения должна быть одной из: " + ", ".join(allowed)
            )
        return value



class ExtendedContactMultiple(Contact):
    reasons: list[str]
    detected_at: datetime

    @field_validator("reasons")
    def validate_reasons(cls, values):
        allowed = ["нет доступа к сети", "не работает телефон", "не приходят письма"]
        for v in values:
            if v not in allowed:
                raise ValueError(
                    "Каждая причина обращения должна быть одной из: " + ", ".join(allowed)
                )
        return values
