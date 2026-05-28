from fastapi import FastAPI
from app.api.routes import customers_router, health_router, webhooks_router

app = FastAPI(title="Client Management Pipefy")

@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Client Management Pipefy API",
        "docs": "/docs",
        "health": "/health",
    }

app.include_router(health_router)
app.include_router(customers_router)
app.include_router(webhooks_router)