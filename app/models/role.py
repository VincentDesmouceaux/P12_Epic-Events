"""Modèle « Role ».

Un rôle représente le département ou les droits d’un collaborateur
(ex. : *commercial*, *support*, *gestion*).
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String

from app.models.base import Base


class Role(Base):
    """Table *roles* – stocke les différents types de rôle disponibles."""

    __tablename__: str = "roles"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(50), unique=True, nullable=False)
    description: str | None = Column(String(255), nullable=True)
