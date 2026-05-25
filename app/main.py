from fastapi import FastAPI

app = FastAPI(title="Client Management Pipefy")

@app.get("/")
def read_root():
    return {
        "message": "Client Management Pipefy API",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "API is running",
    }