from fastapi.responses import JSONResponse
from project.routes.network import network_router
from project.routes.network.dto import Subnets
from project.utils.SubnetsService import SubnetService


@network_router.post("/subnets/")
async def network_subnets_endpoint(subnets_data: Subnets):
    subnet_service = SubnetService()
    subnets = await subnet_service.get_subnets(network_ip_address=subnets_data.network_ip_address, 
                                               mask_prefix=subnets_data.mask_prefix, hosts_per_subnet=subnets_data.hosts_per_subnet)

    return JSONResponse(status_code=200, content=subnets)
