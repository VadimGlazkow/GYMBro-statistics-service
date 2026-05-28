from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()


async def get_current_user(credentials: HTTPBearer = Depends(security)) -> int:
    """Заглушка. Возвращает user_id = 1 для всех запросов"""
    return 2