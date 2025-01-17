from fastapi import Path, APIRouter
from fastapi.responses import JSONResponse

from project import router_v1
from project.utils.NetworkService import IPConverter

mask_router = APIRouter(prefix="/mask", tags=["Mask"])


@mask_router.get("/prefix/{prefix}/")
async def mask_to_cidr_endpoint(prefix: int = Path(..., ge=1, le=32)):
    ip_converter = IPConverter()
    ip_mask = await ip_converter.prefix_to_mask_ip(prefix)

    return JSONResponse(status_code=200, content={
        "ip_mask": ip_mask,
    })


@mask_router.get("/ip/{mask_ip}/")
async def mask_to_cidr_endpoint(mask_ip: str):
    ip_converter = IPConverter()
    prefix = await ip_converter.mask_ip_to_prefix(mask_ip)

    return JSONResponse(status_code=200, content={
        "prefix": prefix,
    })


router_v1.include_router(mask_router)
