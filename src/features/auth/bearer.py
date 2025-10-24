from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException

security = HTTPBearer()


def authenticate_token(token: str) -> bool:
    # Placeholder for token authentication logic
    return token == "Nina"


async def get_current_user(credentials=Depends(security)):
    token = credentials.credentials
    if not authenticate_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": 1, "username": "testuser"}
