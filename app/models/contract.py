from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base
from app.models.client import Client
from app.models.user import User


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Lien vers le client concerné
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", backref="contracts")

    # Le commercial gérant ce contrat (souvent le même que dans Client)
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User", backref="contracts")

    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)

    date_created = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)

    # Ex: on pourrait avoir un "date_signed" ou "signed_by" si besoin.
