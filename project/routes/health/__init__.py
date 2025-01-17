import psutil

from project import router_v1


@router_v1.get("/health/", tags=["General"])
async def health_endpoint():
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)

    health_info = {
        "api": {
            "cpu": {
                "used": f"{cpu_percent:.1f}%"
            },
            "memory": {
                "total": f"{memory.total / 1024 / 1024 / 1024:.2f} GB",
                "available": f"{memory.available / 1024 / 1024 / 1024:.2f} GB",
                "used": f"{memory.used / 1024 / 1024 / 1024:.2f} GB",
                "percent": f"{memory.percent}%"
            }
        }
    }
    return health_info
