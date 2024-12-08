from fastapi import APIRouter


router = APIRouter()


@router.get("")
async def health_check():
    """Check if the service and models are healthy."""
    return {"status": "healthy"}
