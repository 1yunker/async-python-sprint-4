from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from .base import Base


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    original_url = Column(String, index=True)
    short_url = Column(String, unique=True, index=True)
    short_id = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    # is_private = Column(Boolean, default=False)

    tbl_clicks = relationship('Click')


class Click(Base):
    __tablename__ = 'clicks'

    id = Column(Integer, primary_key=True)
    url_id = Column(ForeignKey('urls.id'))
    user_agent = Column(String or None)
    created_at = Column(DateTime, server_default=func.now())
