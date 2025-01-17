import bcrypt
from fastapi import HTTPException
from pydantic import validate_email
from pydantic_core import PydanticCustomError
from pymysql import err
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import selectinload
from database import async_session
from database.mariadb.models import Admins, AdminsPermissions
from project.utils import TokenService


async def get_admin_dict(admin_query):
    return {
        "admin_id": admin_query.admin_id,
        "username": admin_query.username,
        "email": admin_query.email,
        "permissions": [item.permission for item in admin_query.permissions]
    }


async def get_admin(admin_id: int):
    try:
        async with async_session() as session_db:
            admin_query = await session_db.execute(select(Admins).options(
                selectinload(Admins.permissions)
            ).filter_by(admin_id=admin_id))
            admin = admin_query.scalar()

            if admin is None:
                raise HTTPException(status_code=404, detail="Admin not found")

            return await get_admin_dict(admin)
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def create_admin(admin_data: dict):
    try:
        async with async_session() as session_db:
            admin_query = await session_db.execute(select(Admins).filter_by(username=admin_data["username"]))
            admin = admin_query.scalar()

            if admin is not None:
                raise HTTPException(status_code=409, detail="Username already taken")

            admin_obj = Admins(
                username=admin_data["username"],
                email=admin_data["email"],
                password_hash=bcrypt.hashpw(admin_data["password"].encode(), bcrypt.gensalt())
            )
            session_db.add(admin_obj)
            await session_db.flush()

            for permission in admin_data["permissions"]:
                permission_obj = AdminsPermissions(
                    admin_id=admin_obj.admin_id,
                    permission=permission
                )
                session_db.add(permission_obj)

            await session_db.commit()
            return admin_data
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def login(admin_data: dict):
    try:
        async with async_session() as session_db:
            try:
                _, email = validate_email(admin_data["username_or_email"])
                admin_query = await session_db.execute(select(Admins).filter_by(email=email))
            except PydanticCustomError:
                username = admin_data["username_or_email"]
                admin_query = await session_db.execute(select(Admins).filter_by(username=username))

            admin = admin_query.scalar()
            if admin is None:
                raise HTTPException(status_code=404, detail="User not found")

            if not bcrypt.checkpw(admin_data["password"].encode(), admin.password_hash):
                raise HTTPException(status_code=401, detail="Incorrect password")

            token_service = TokenService()
            token = await token_service.generate_token(admin_id=admin.admin_id, username=admin.username)

            return token
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
