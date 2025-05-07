# -*- coding: utf-8 -*-
"""
Création du schéma SQL.

Le module expose une seule fonction :

    init_db()  – supprime l’éventuel schéma existant puis recrée
                 l’ensemble des tables déclarées dans les modèles.
"""

from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base


def init_db() -> None:
    """
    (Re)crée toutes les tables définies dans *app.models*.

    * Supprime le schéma existant (``DROP TABLE …``) ;
    * Exécute les instructions ``CREATE TABLE`` générées par SQLAlchemy.
    """
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    engine = conn.engine

    print("Suppression des tables existantes…")
    Base.metadata.drop_all(bind=engine)

    print("Création du schéma (tables)…")
    Base.metadata.create_all(bind=engine)

    print("Tables créées avec succès.")
