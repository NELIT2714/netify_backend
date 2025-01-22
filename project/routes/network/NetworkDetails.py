from fastapi import HTTPException
from fastapi.responses import JSONResponse

from project.routes.network import network_router
from project.routes.network.dto import NetworkDetails

from project.utils import NetworkService
from project.utils.NetworkService import IPConverter


@network_router.post("/details/")
async def network_details_endpoint(network_data: NetworkDetails):
    ip_converter = IPConverter()
    subnet_mask = await ip_converter.prefix_to_mask_ip(network_data.mask_prefix)

    network_service = NetworkService(ip=network_data.ip_address, subnet_mask=subnet_mask)

    network_ip = await network_service.get_network_address()
    network_hosts = await network_service.get_hosts()
    network_broadcast = await network_service.get_broadcast_address()

    ip_class = await network_service.get_ip_class()
    ip_status = await network_service.get_ip_status()

    return JSONResponse(status_code=200, content={
        "ip": {
            "address": network_data.ip_address,
            "ip_class": ip_class,
            "ip_status": ip_status,
        },
        "network": {
            "ip": network_ip,
            "hosts": network_hosts,
            "broadcast": network_broadcast,
            "subnet_mask": subnet_mask,
        },
    })