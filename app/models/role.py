# app/models/role.py
from sqlalchemy import Column, Integer, String
from app.models import Base


class Role(Base):
    """
    Modèle représentant un rôle (ou département) dans l'entreprise.
    Exemple de rôles : "commercial", "support", "gestion".
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
