from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Articles(Base):
    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, unique=True, index=True)

    translation = relationship("ArticlesTranslations", back_populates="article", uselist=True)
    page = relationship("ArticlesPageTranslations", back_populates="article", uselist=True)


class ArticlesTranslations(Base):
    __tablename__ = "articles_translations"

    translation_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.article_id"), index=True)
    language = Column(String(5), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)

    article = relationship("Articles", back_populates="translation")


class ArticlesPageTranslations(Base):
    __tablename__ = "articles_page_translations"

    translation_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.article_id"), index=True)
    language = Column(String(5), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    article = relationship("Articles", back_populates="page")
