from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("Contract", backref="event")
    support_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    support = relationship("User", backref="events")
    date_start = Column(DateTime, default=datetime.utcnow)
    date_end = Column(DateTime, nullable=True)
    location = Column(String(255), nullable=True)
    attendees = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
