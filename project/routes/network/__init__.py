from fastapi import APIRouter
from fastapi.responses import JSONResponse

from project import router_v1
from project.routes.network.dto import NetworkDetails
from project.utils import NetworkService
from project.utils.NetworkService import IPConverter

network_router = APIRouter(prefix="/network", tags=["Network"])

from .NetworkDetails import network_details_endpoint
from .Subnets import network_subnets_endpoint

router_v1.include_router(network_router)
