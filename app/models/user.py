"""Modèle « User ».

Représente un collaborateur de l’entreprise, rattaché à un rôle
(:class:`app.models.role.Role`).
"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    """Table *users* – informations d’identification et de profil."""

    __tablename__: str = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    employee_number: str = Column(String(50), unique=True, nullable=False)
    first_name: str = Column(String(150), nullable=False)
    last_name: str = Column(String(150), nullable=False)
    email: str = Column(String(150), unique=True, nullable=False)
    password_hash: str = Column(String(255), nullable=False)

    # --- relations --------------------------------------------------
    role_id: int = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", backref="users", lazy="joined")
