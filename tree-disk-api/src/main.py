from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.preparation import create_dirs, download_u2net_model, download_yolo_model
from api.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI app started.")

    create_dirs()
    download_u2net_model()
    download_yolo_model()

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
