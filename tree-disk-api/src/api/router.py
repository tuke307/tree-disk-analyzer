from fastapi import APIRouter
from api.endpoints import segmentation, pith, rings, health

# Create routers
router = APIRouter()

# Include all endpoint routers
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(
    segmentation.router, prefix="/segmentation", tags=["segmentation"]
)
router.include_router(pith.router, prefix="/pith", tags=["pith"])
router.include_router(rings.router, prefix="/rings", tags=["rings"])
