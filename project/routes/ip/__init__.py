from fastapi import APIRouter

from project import router_v1
from project.utils.NetworkService import IPConverter
from fastapi.responses import JSONResponse


ip_router = APIRouter(prefix="/ip", tags=["IP"])


@ip_router.get("/bin/{ip_address}/")
async def ip_to_binary_endpoint(ip_address: str):
    ip_converter = IPConverter()
    ip_bin = await ip_converter.ip_to_binary(ip_address)

    return JSONResponse(status_code=200, content={
        "ip_address_binary": ip_bin,
    })


@ip_router.get("/dec/{ip_address_bin}/")
async def binary_ip_to_dec_endpoint(ip_address_bin: str):
    ip_converter = IPConverter()
    ip_address = await ip_converter.binary_to_ip(ip_address_bin)

    return JSONResponse(status_code=200, content={
        "ip_address": ip_address,
    })


router_v1.include_router(ip_router)
