"""Modèle « Event ».

Un événement (prestations Epic Events) est toujours adossé à un contrat.
Il peut être pris en charge par un collaborateur *support*.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class Event(Base):
    """Table *events* – informations logistiques des événements."""

    __tablename__: str = "events"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    # --- clés étrangères -------------------------------------------
    contract_id: int = Column(
        Integer, ForeignKey("contracts.id"), nullable=False)
    support_id: int | None = Column(
        Integer, ForeignKey("users.id"), nullable=True)

    # --- datation ---------------------------------------------------
    date_start: datetime = Column(DateTime, default=datetime.utcnow)
    date_end: datetime | None = Column(DateTime, nullable=True)

    # --- détails pratiques -----------------------------------------
    location: str | None = Column(String(255), nullable=True)
    attendees: int | None = Column(Integer, nullable=True)
    notes: str | None = Column(Text, nullable=True)

    # --- relations --------------------------------------------------
    contract = relationship("Contract", backref="event")
    support = relationship("User", backref="events")
