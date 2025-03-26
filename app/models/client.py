from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base
from app.models.user import User


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)

    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=True)
    company_name = Column(String(150), nullable=True)

    date_created = Column(DateTime, default=datetime.utcnow)  # premier contact
    # dernière mise à jour
    date_last_contact = Column(DateTime, nullable=True)

    # Le commercial responsable de ce client
    # -> On suppose qu'il s'agit d'un user avec role="commercial"
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relation pour accéder à l'objet "User" du commercial
    commercial = relationship("User", backref="clients")

    # Vous pouvez aussi stocker le nom du commercial, mais c'est
    # redondant avec le user. On s'appuie plutôt sur la relation.
