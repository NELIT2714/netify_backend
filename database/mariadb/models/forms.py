from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base


class Forms(Base):
    __tablename__ = "contact_forms"

    form_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False, index=True)
    email = Column(String(70), nullable=False, index=True)
    message = Column(Text, nullable=False)

    data = relationship("FormsMetadata", back_populates="form", uselist=False)


class FormsMetadata(Base):
    __tablename__ = "contact_forms_metadata"

    form_id = Column(Integer, ForeignKey("contact_forms.form_id"), primary_key=True, index=True)
    ip_address = Column(String(15), nullable=True, default=None)
    language = Column(String(5), nullable=True, default=None)
    location = Column(String(150), nullable=True, default=None)
    submitted_at = Column(DateTime, nullable=False)

    form = relationship("Forms", back_populates="data")
