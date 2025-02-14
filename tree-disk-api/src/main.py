from contextlib import asynccontextmanager
from cv2 import log
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from .config.settings import DEBUG, log_settings
from .api.router import router

logger = logging.getLogger(__name__)

logging_level = logging.DEBUG if DEBUG else logging.INFO
logging.basicConfig(level=logging_level)
logging.getLogger("uvicorn").setLevel(logging_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting the application.")

    # print all settings in debug
    log_settings()

    yield


app = FastAPI(
    title="Tree Disk API",
    description="API for analyzing tree disk.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include all routes
app.include_router(router)

# Enable CORS for the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
