from typing import Union

from fastapi import HTTPException
from pymysql import err
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from database import async_session
from database.mariadb.models import Articles, ArticlesTranslations, ArticlesPageTranslations


async def get_article_dict(article_query: Articles):
    def map_translations(translations, *fields):
        return {field: {item.language: getattr(item, field) for item in translations} for field in fields}

    if article_query:
        article_dict = {
            "article_id": article_query.article_id,
            **map_translations(article_query.translation, "title", "content"),
            "page": map_translations(article_query.page, "title", "description"),
        }
        article_dict["page"]["url"] = article_query.url
        return article_dict



async def get_articles(limit: int = 10, page: int = 1):
    offset = (page - 1) * limit
    try:
        async with async_session() as session_db:
            articles_query = await session_db.execute(select(Articles).options(
                    selectinload(Articles.translation),
                    selectinload(Articles.page)
                ).limit(limit).offset(offset)
            )
            articles = articles_query.scalars().all()
            articles_dict = [await get_article_dict(article) for article in articles]

            total_query = await session_db.execute(select(func.count("*")).select_from(Articles))
            total = total_query.scalar()

            if 1 < page > total:
                raise HTTPException(status_code=404, detail="Page not found")

            return {
                "articles": articles_dict,
                "count": total,
                "page": {
                    "current": page,
                    "total": (total + limit - 1) // limit,
                }
            }
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def get_article(article_id_or_url: Union[int, str]):
    try:
        async with async_session() as session_db:
            if article_id_or_url.isdigit():
                article_id = int(article_id_or_url)
                article_query = await session_db.execute(select(Articles).options(
                    selectinload(Articles.translation),
                    selectinload(Articles.page)
                ).filter_by(article_id=article_id))
            else:
                article_url = article_id_or_url
                article_query = await session_db.execute(select(Articles).options(
                    selectinload(Articles.translation),
                    selectinload(Articles.page)
                ).filter_by(url=article_url))

            article = article_query.scalar_one_or_none()
            if article is None:
                raise HTTPException(status_code=404, detail="Article not found")

            return await get_article_dict(article)
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def create_article(article_data: dict):
    title_dict = article_data["title"]
    content_dict = article_data["content"]
    page_dict = article_data["page"]

    article_url = page_dict["url"]
    await check_article_url(article_url)

    try:
        async with async_session() as session_db:
            article_obj = Articles(url=article_url)
            session_db.add(article_obj)
            await session_db.flush()

            for lang in title_dict.keys():
                article_title = title_dict[lang]
                article_content = content_dict[lang]

                page_title = page_dict["title"][lang]
                page_description = page_dict["description"][lang]

                translation_obj = ArticlesTranslations(article_id=article_obj.article_id,
                                                       language=lang,
                                                       title=article_title,
                                                       content=article_content
                                                       )

                page_translation_obj = ArticlesPageTranslations(article_id=article_obj.article_id,
                                                                language=lang,
                                                                title=page_title,
                                                                description=page_description
                                                                )

                session_db.add_all([translation_obj, page_translation_obj])

            await session_db.commit()

            return article_data
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def update_article(article_id: int, article_data: dict):
    try:
        async with async_session() as session_db:
            article_query = await session_db.execute(
                select(Articles).options(
                    selectinload(Articles.translation),
                    selectinload(Articles.page),
                ).filter_by(article_id=article_id)
            )
            article = article_query.scalar_one_or_none()

            if not article:
                raise HTTPException(status_code=404, detail="Article not found")

            for translation in article.translation:
                if "title" in article_data:
                    if translation.language in article_data["title"]:
                        translation.title = article_data["title"][translation.language]

                if "content" in article_data:
                    if translation.language in article_data["content"]:
                        translation.content = article_data["content"][translation.language]

            if "page" in article_data:
                for page in article.page:
                    if "title" in article_data["page"]:
                        if page.language in article_data["page"]["title"]:
                            page.title = article_data["page"]["title"][page.language]

                    if "description" in article_data["page"]:
                        if page.language in article_data["page"]["description"]:
                            page.description = article_data["page"]["description"][page.language]

                    if "url" in article_data["page"]:
                        article.url = article_data["page"]["url"]

            await session_db.commit()
            return await get_article_dict(article)
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def delete_article(article_id: int):
    try:
        async with async_session() as session_db:
            article_query = await session_db.execute(
                select(Articles).options(
                    selectinload(Articles.translation),
                    selectinload(Articles.page)
                ).filter_by(article_id=article_id)
            )
            article = article_query.scalar_one_or_none()

            if article is None:
                raise HTTPException(status_code=404, detail="Article not found")

            for item in article.translation:
                await session_db.delete(item)

            for item in article.page:
                await session_db.delete(item)

            await session_db.delete(article)
            await session_db.commit()
            return await get_articles()
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def check_article_url(url: str):
    try:
        async with async_session() as session_db:
            article_query = await session_db.execute(select(Articles).filter_by(url=url))
            if article_query.scalar_one_or_none() is not None:
                raise HTTPException(status_code=409, detail="Article url is already taken")
    except (err.MySQLError, SQLAlchemyError) as error:
        print(error)
        await session_db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
