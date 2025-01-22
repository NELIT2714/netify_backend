from fastapi import HTTPException


class IPConverter:
    @staticmethod
    async def ip_to_binary(ip_address: str) -> str:
        octets = ip_address.split(".")
        if not len(octets) == 4:
            raise HTTPException(status_code=400, detail="Invalid IP address")

        try:
            for octet in octets:
                octet_int = int(octet)
                if not (0 <= octet_int <= 255):
                    raise HTTPException(status_code=400, detail="Invalid IP address")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IP address")

        return "".join(f"{int(octet):08b}" for octet in ip_address.split("."))

    @staticmethod
    async def binary_to_ip(binary: str) -> str:
        if not len(binary) == 32:
            raise HTTPException(status_code=400, detail="Invalid binary format")
        return ".".join(str(int(binary[i:i + 8], 2)) for i in range(0, 32, 8))

    # Replace to SubnetService
    @staticmethod
    async def prefix_to_mask_ip(prefix: int) -> str:
        if 1 < prefix > 32:
            raise HTTPException(status_code=400, detail="Invalid subnet mask length")

        mask_binary = "1" * prefix + "0" * (32 - prefix)
        return ".".join(str(int(mask_binary[i:i + 8], 2)) for i in range(0, 32, 8))

    # Replace to SubnetService
    @staticmethod
    async def mask_ip_to_prefix(mask_ip: str) -> int:
        try:
            mask_octets = mask_ip.split(".")
            if len(mask_octets) != 4:
                raise HTTPException(status_code=400, detail="Invalid IP address format")

            mask_binary = "".join(f'{int(octet):08b}' for octet in mask_octets)
            cidr = mask_binary.count("1")

            if not (1 <= cidr <= 32) or "01" in mask_binary:
                raise HTTPException(status_code=400, detail="Invalid subnet mask")

            return cidr
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid subnet mask value")


class NetworkService:
    def __init__(self, ip: str, subnet_mask: str):
        self.ip = ip
        self.subnet_mask = subnet_mask
        self.ip_converter = IPConverter()

    async def get_ip_status(self):
        if self.ip == "127.0.0.1":
            return "Localhost"

        first_octet, second_octet, *_ = map(int, self.ip.split("."))
        if (first_octet == 10) or (first_octet == 172 and 16 <= second_octet <= 31) or (first_octet == 192 and second_octet == 168):
            return "Private"

        return "Public"

    async def get_ip_class(self):
        try:
            first_octet = int(self.ip.split(".")[0])
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid IP address")

        ip_classes = {
            range(1, 128): "A",
            range(128, 192): "B",
            range(192, 224): "C",
            range(224, 240): "D (Multicast)",
            range(240, 256): "E (Experimental)",
        }

        for ip_range, ip_class in ip_classes.items():
            if first_octet in ip_range:
                return ip_class

        raise HTTPException(status_code=400, detail="Invalid IP address")

    async def get_network_address(self):
        ip_binary = await self.ip_converter.ip_to_binary(self.ip)
        mask_binary = await self.ip_converter.ip_to_binary(self.subnet_mask)

        network_binary = "".join("1" if ip_bit == "1" and mask_bit == "1" else "0" for ip_bit, mask_bit in zip(ip_binary, mask_binary))
        return await self.ip_converter.binary_to_ip(network_binary)

    async def get_broadcast_address(self):
        ip_converter = IPConverter()
        ip_binary = await ip_converter.ip_to_binary(self.ip)
        mask_binary = await ip_converter.ip_to_binary(self.subnet_mask)

        broadcast_binary = "".join("1" if mask_bit == "0" else ip_bit for ip_bit, mask_bit in zip(ip_binary, mask_binary))
        return await ip_converter.binary_to_ip(broadcast_binary)

    async def get_hosts(self):
        mask_binary = await self.ip_converter.ip_to_binary(self.subnet_mask)
        num_of_zeros = mask_binary.count("0")
        return (2 ** num_of_zeros) - 2
