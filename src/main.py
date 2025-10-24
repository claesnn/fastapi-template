from fastapi import FastAPI
from pydantic import BaseModel
from logger import logger

from features.todos.routes import router as todos_router
from features.users.routes import router as users_router
from middleware import StructlogRequestMiddleware

app = FastAPI()

app.add_middleware(StructlogRequestMiddleware)


class StatusResponse(BaseModel):
    status: str


@app.get("/", response_model=StatusResponse)
async def status():
    await logger.ainfo("Status endpoint called")
    return {"status": "ok"}


app.include_router(todos_router)
app.include_router(users_router)
