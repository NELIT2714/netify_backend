import math
from fastapi import HTTPException

from project.utils.NetworkService import IPConverter


class SubnetService:

    @staticmethod
    async def get_subnets(network_ip_address: str, mask_prefix: int, hosts_per_subnet: int):
        hosts = 2 ** (32 - mask_prefix)
        if hosts_per_subnet > hosts:
            return HTTPException(status_code=400, detail="hosts_per_subnet exceeds available addresses in the network")
        
        adjusted_hosts = 2 ** math.ceil(math.log2(hosts_per_subnet + 2)) - 2
        new_mask_prefix = 32 - math.ceil(math.log2(adjusted_hosts + 2))

        ip_converter = IPConverter()
        network_ip_binary = await ip_converter.ip_to_binary(network_ip_address)

        num_subnets = 2 ** (new_mask_prefix - mask_prefix)
        subnet_size = 2 ** (32 - new_mask_prefix)

        subnet_mask = await ip_converter.prefix_to_mask_ip(new_mask_prefix)

        subnets = []
        for i in range(num_subnets):
            subnet_start_binary = bin(int(network_ip_binary, 2) + (i * subnet_size))[2:].zfill(32)
            subnet_start_ip = await ip_converter.binary_to_ip(subnet_start_binary)

            subnet_end_binary = bin(int(subnet_start_binary, 2) + subnet_size - 1)[2:].zfill(32)
            subnet_end_ip = await ip_converter.binary_to_ip(subnet_end_binary)

            subnets.append({
                "start_ip": subnet_start_ip,
                "end_ip": subnet_end_ip,
            })
        
        return {
            "subnet_mask": subnet_mask,
            "mask_prefix": new_mask_prefix,
            "usable_hosts": adjusted_hosts,
            "subnets": subnets
        }

