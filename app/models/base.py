"""Déclaration de la « base » SQLAlchemy pour tous les modèles.

Chaque classe‐modèle de l’application hérite de `Base` afin de partager
la même métadonnée et de permettre à SQLAlchemy de créer le schéma.
"""

from sqlalchemy.ext.declarative import declarative_base

#: Instance unique de base déclarative (metadata partagée).
Base = declarative_base()
