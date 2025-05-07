"""Modèle « Contract ».

Un contrat relie un client à un commercial et précise le montant
engagé, le reste à payer, la date de création et l’état de signature.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import Base


class Contract(Base):
    """Table *contracts* – détail des contrats signés (ou non)."""

    __tablename__: str = "contracts"

    id: int = Column(Integer, primary_key=True, autoincrement=True)

    # --- clés étrangères -------------------------------------------
    client_id: int = Column(Integer, ForeignKey("clients.id"), nullable=False)
    commercial_id: int = Column(
        Integer, ForeignKey("users.id"), nullable=False)

    # --- montants ---------------------------------------------------
    total_amount: float = Column(Float, nullable=False)
    remaining_amount: float = Column(Float, nullable=False)

    # --- métadonnées -----------------------------------------------
    date_created: datetime = Column(DateTime, default=datetime.utcnow)
    is_signed: bool = Column(Boolean, default=False)

    # --- relations --------------------------------------------------
    client = relationship("Client", backref="contracts")
    commercial = relationship("User", backref="contracts")
