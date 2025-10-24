from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from features.auth.bearer import get_current_user
from logger import logger

from features.todos.routes import router as todos_router
from features.users.routes import router as users_router
from middleware import StructlogRequestMiddleware
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Literal

app = FastAPI(dependencies=[Depends(get_current_user)])

app.add_middleware(StructlogRequestMiddleware)


class StatusResponse(BaseModel):
    status: Literal["ok"]


@app.get("/", response_model=StatusResponse)
async def read_status():
    await logger.ainfo("Status endpoint called")
    return {"status": "ok"}


@app.get("/health", response_model=StatusResponse)
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        return {"status": "ok"}
    except Exception as e:
        await logger.aerror("Health check failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection failed")


app.include_router(todos_router)
app.include_router(users_router)
