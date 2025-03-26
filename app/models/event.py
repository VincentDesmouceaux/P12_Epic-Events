from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base
from app.models.contract import Contract
from app.models.user import User


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Lien vers le contrat concerné
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("Contract", backref="event")
    # Un contrat donne lieu à un seul événement (?), ou un event
    # par contrat. Cf. cahier des charges.

    # Collaborateur support attribué
    support_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    support = relationship("User", backref="events")
    # Il s'agit d'un user (role="support") chargé de l'événement

    date_start = Column(DateTime, default=datetime.utcnow)
    date_end = Column(DateTime, nullable=True)

    location = Column(String(255), nullable=True)
    attendees = Column(Integer, nullable=True)  # nombre de participants
    notes = Column(Text, nullable=True)
