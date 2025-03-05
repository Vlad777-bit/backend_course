import secrets
from typing import Dict

# Словарь вида {token: user_id}
# В продакшене лучше хранить в Redis, чтобы был общий доступ
in_memory_tokens: Dict[str, int] = {}

def create_token_for_user(user_id: int) -> str:
    """
    Генерируем случайный токен и сохраняем в словарь in_memory_tokens.
    Возвращаем сам токен.
    """
    token = secrets.token_hex(16)
    in_memory_tokens[token] = user_id
    return token

def get_user_id_by_token(token: str) -> int:
    """
    Возвращает user_id, если токен есть в словаре, иначе 0 или -1.
    """
    return in_memory_tokens.get(token, 0)

def delete_token(token: str):
    """
    Удаляем токен (logout).
    """
    in_memory_tokens.pop(token, None)
