from .customers import router as customers_router
from .health import router as health_router

__all__ = [
    "customers_router",
    "health_router",
]