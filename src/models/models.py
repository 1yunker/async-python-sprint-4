from sqlalchemy import Boolean, Column, Integer, String

from .base import Base


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    original_url = Column(String, index=True)
    short_url = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
    # key = Column(String, unique=True, index=True)
    # secret_key = Column(String, unique=True, index=True)
