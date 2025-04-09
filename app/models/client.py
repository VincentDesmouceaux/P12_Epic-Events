from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(150), nullable=True)
    date_created = Column(DateTime, default=datetime.utcnow)
    date_last_contact = Column(DateTime, nullable=True)
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User", backref="clients")
