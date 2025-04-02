import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from src.api.endpoints.auth import auth_router
from src.api.endpoints.orders import order_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(order_router, prefix="/orders")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)