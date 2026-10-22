from fastapi import APIRouter
from .health import router as health_router
from .dashboard import router as dashboard_router
from .users import router as users_router
from .assets import router as assets_router
from .nominees import router as nominees_router
from .executors import router as executors_router
from .plans import router as plans_router
from .releases import router as releases_router
from .graph import router as graph_router
from .seed import router as seed_router

api_router = APIRouter(prefix="/api")

api_router.include_router(health_router, prefix="/health", tags=["System & Health"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(assets_router, prefix="/assets", tags=["Digital Assets"])
api_router.include_router(nominees_router, prefix="/nominees", tags=["Nominees"])
api_router.include_router(executors_router, prefix="/executors", tags=["Trusted Executors"])
api_router.include_router(plans_router, prefix="/plans", tags=["Legacy Plans"])
api_router.include_router(releases_router, prefix="/releases", tags=["Scheduled Releases"])
api_router.include_router(graph_router, prefix="/graph", tags=["Graph Traversals & Topology"])
api_router.include_router(seed_router, prefix="/seed", tags=["Data Seeding & Maintenance"])

__all__ = ["api_router"]
