import os

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# from .middlewares import APIKeyMiddleware


# @asynccontextmanager
# async def lifespan(app_class: FastAPI):
#     from .database.mariadb import models
#
#     await create_tables()
#     yield


app = FastAPI(
    title="Netify API",
    debug=True if os.getenv("API_MODE") == "DEV" else False,
    docs_url="/",
    redoc_url="/redoc" if os.getenv("MODE") == "DEV" else None,
    # lifespan=lifespan
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

router_v1 = APIRouter(prefix="/v1")

from .routes import health, network, mask, ip

router.include_router(router_v1)
app.include_router(router)

# app.add_middleware(APIKeyMiddleware)
