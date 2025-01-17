# import os
#
# import jwt
# import datetime
# from abc import ABC, abstractmethod
#
#
# class TokenConfig:
#     SECRET_KEY = os.getenv("JWT_SECRET_KEY")
#     ALGORITHM = os.getenv("JWT_ALGORITHM")
#     DEFAULT_TTL = int(os.getenv("JWT_DEFAULT_TTL"))
#
#
# class TokenCreator(ABC):
#     @abstractmethod
#     async def create_token(self, admin_id: int, username: str, ttl: int = TokenConfig.DEFAULT_TTL) -> str:
#         pass
#
#
# class TokenVerifier(ABC):
#     @abstractmethod
#     async def verify_token(self, token: str) -> dict:
#         pass
#
#
# class JWTTokenCreator(TokenCreator):
#     async def create_token(self, admin_id: int, username: str, ttl: int = TokenConfig.DEFAULT_TTL) -> str:
#         payload = {
#             "admin_id": admin_id,
#             "username": username,
#             "exp": int(datetime.datetime.now().timestamp()) + (ttl * 60)
#         }
#         token = jwt.encode(payload, TokenConfig.SECRET_KEY, algorithm=TokenConfig.ALGORITHM)
#         return token
#
#
# class JWTTokenVerifier(TokenVerifier):
#     async def verify_token(self, token: str) -> dict:
#         try:
#             decoded_data = jwt.decode(token, TokenConfig.SECRET_KEY, algorithms=[TokenConfig.ALGORITHM])
#             expiration_time = decoded_data["exp"]
#             decoded_data.pop("exp", None)
#             return {
#                 "token_status": True,
#                 "token_data": {
#                     **decoded_data,
#                 },
#                 "expiration_time": expiration_time
#             }
#         except jwt.ExpiredSignatureError:
#             return {"token_status": False, "detail": "Token expired"}
#         except jwt.InvalidTokenError:
#             return {"token_status": False, "detail": "Invalid token"}
#
#
# class TokenService:
#     def __init__(self, token_creator: TokenCreator = JWTTokenCreator(), token_verifier: TokenVerifier = JWTTokenVerifier()):
#         self._token_creator = token_creator
#         self._token_verifier = token_verifier
#
#     async def generate_token(self, admin_id: int, username: str, ttl: int = TokenConfig.DEFAULT_TTL):
#         return await self._token_creator.create_token(admin_id, username, ttl)
#
#     async def check_token(self, token: str):
#         return await self._token_verifier.verify_token(token)
