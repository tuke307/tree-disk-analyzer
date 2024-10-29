from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get(
    "/sample",
    responses={
        429: {"description": "Too Many Requests"},
    },
)
async def sample(q: str) -> None:
    """
    Sample endpoint.<br>
    Example usage: http://127.0.0.1:8000/sample
    """
    query = q
    print(f"Query: {query}")

    return None
