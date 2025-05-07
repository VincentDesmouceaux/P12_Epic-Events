"""Modèle « Client ».

Représente une entité cliente gérée par un commercial.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Client(Base):
    """Table *clients* – renseignements sur les clients."""

    __tablename__: str = "clients"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    full_name: str = Column(String(150), nullable=False)
    email: str = Column(String(150), nullable=False)
    phone: str | None = Column(String(50), nullable=True)
    company_name: str | None = Column(String(150), nullable=True)
    date_created: datetime = Column(DateTime, default=datetime.utcnow)
    date_last_contact: datetime | None = Column(DateTime, nullable=True)

    # --- relations --------------------------------------------------
    commercial_id: int = Column(
        Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User", backref="clients")
