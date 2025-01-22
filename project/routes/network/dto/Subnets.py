from pydantic import BaseModel, Field


class Subnets(BaseModel):
    network_ip_address: str
    mask_prefix: int = Field(..., ge=1, le=32)
    hosts_per_subnet: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "network_ip_address": "192.168.1.0",
                    "mask_prefix": 24,
                    "hosts_per_subnet": 30
                }
            ]
        }
    }
