from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", backref="contracts")
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User", backref="contracts")
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    is_signed = Column(Boolean, default=False)
