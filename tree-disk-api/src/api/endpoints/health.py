from fastapi import APIRouter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def health_check():
    """Check if the service and models are healthy."""
    logger.debug("Health check endpoint called.")

    return {"status": "healthy"}
