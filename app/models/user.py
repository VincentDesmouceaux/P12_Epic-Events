from sqlalchemy import Column, Integer, String
from app.models import Base


class User(Base):
    """
    Table des collaborateurs de l'entreprise (gestion, commercial, support).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    # Exemples de rôles : "gestion", "commercial", "support"

    # Exemples de champs optionnels (nom, email, etc.)
    # email = Column(String(150), unique=True)

    # Pas de relation "native" ici,
    # mais on peut définir relationships si on veut accéder
    # aux clients/contrats liés (pour un commercial),
    # aux événements liés (pour un support).
    # Cf. client.py, contract.py, event.py
