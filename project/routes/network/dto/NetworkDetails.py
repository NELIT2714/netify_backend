from pydantic import BaseModel, Field


class NetworkDetails(BaseModel):
    ip_address: str
    mask_prefix: int = Field(..., ge=1, le=32)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ip_address": "192.168.1.1",
                    "mask_prefix": 24
                }
            ]
        }
    }
