import datetime

from fastapi import HTTPException
from pymysql import err
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from database import async_session
from database.mariadb.models import Forms, FormsMetadata


async def get_form_dict(form_query: Forms):
    if form_query:
        return {
            "form_id": form_query.form_id,
            "fullname": form_query.fullname,
            "email": form_query.email,
            "message": form_query.message,
            "metadata": {
                "ip_address": form_query.data.ip_address,
                "language": form_query.data.language,
                "location": form_query.data.location,
                "submitted_at": str(form_query.data.submitted_at),
            }
        }


async def get_forms(limit: int = 10, page: int = 1):
    offset = (page - 1) * limit
    try:
        async with async_session() as session_db:
            forms_query = await session_db.execute(select(Forms).options(
                selectinload(Forms.data)
            ).limit(limit).offset(offset))
            forms = forms_query.scalars().all()

            total_query = await session_db.execute(select(func.count("*")).select_from(Forms))
            total = total_query.scalar()

            forms_dict = [await get_form_dict(form) for form in forms]

            return {
                "forms": forms_dict,
                "page": {
                    "current": page,
                    "total": (total + limit - 1) // limit,
                }
            }
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def get_form(form_id: int):
    try:
        async with async_session() as session_db:
            form_query = await session_db.execute(select(Forms).options(
                selectinload(Forms.data)
            ).filter_by(form_id=form_id))
            form = form_query.scalar_one_or_none()

            if form is None:
                raise HTTPException(status_code=404, detail="Form not found")

            return await get_form_dict(form)
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def create_form(form_data: dict):
    try:
        async with async_session() as session_db:
            form_obj = Forms(
                fullname=form_data["fullname"],
                email=form_data["email"],
                message=form_data["message"]
            )
            session_db.add(form_obj)
            await session_db.flush()

            form_metadata_obj = FormsMetadata(
                form_id=form_obj.form_id,
                ip_address=form_data["metadata"]["ip_address"],
                language=form_data["metadata"]["language"],
                location=form_data["metadata"]["location"],
                submitted_at=datetime.datetime.now()
            )
            session_db.add(form_metadata_obj)
            await session_db.commit()

            return form_data
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


# async def update_form(form_id: int, form_data: dict):
#     return form_data


async def delete_form(form_id: int):
    try:
        async with async_session() as session_db:
            form_query = await session_db.execute(select(Forms).options(selectinload(Forms.data)).filter_by(form_id=form_id))
            form = form_query.scalar_one_or_none()

            if form is None:
                raise HTTPException(status_code=404, detail="Form not found")

            await session_db.delete(form)
            await session_db.delete(form.data)
            await session_db.commit()

            return await get_forms()
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
