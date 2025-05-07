# app/config/database.py
# -*- coding: utf-8 -*-
"""
Gestion de la configuration et de la connexion à la base de données.

Ce module lit les variables d’environnement définies dans le fichier
```.env``` pour construire l’URL SQLAlchemy de connexion, puis propose :

* **DatabaseConfig** – objet léger qui stocke la configuration.
* **DatabaseConnection** – fabrique d’engine et de sessions SQLAlchemy.

Aucune trace de débogage n’est laissée afin de garder le module propre pour
la production.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Charge immédiatement les variables d'environnement depuis `.env`
load_dotenv()


class DatabaseConfig:
    """
    Lecture et stockage de la configuration liée à la base de données.

    Les variables attendues dans le fichier ```.env``` :

    * **DB_ENGINE**   – ex. ``mysql+pymysql`` ou ``sqlite``  
    * **DB_USER**     – nom d’utilisateur SQL  
    * **DB_PASSWORD** – mot de passe SQL  
    * **DB_HOST**     – hôte du serveur  
    * **DB_PORT**     – port du serveur  
    * **DB_NAME**     – nom de la base  
    * **SENTRY_DSN**  – (optionnel) DSN Sentry, lu ici pour information

    Un attribut supplémentaire ``sqlalchemy_database_url`` est construit
    automatiquement pour être passé à *SQLAlchemy*.
    """

    def __init__(self) -> None:
        # Paramètres principaux
        self.db_engine: str | None = os.getenv("DB_ENGINE")
        self.db_user: str | None = os.getenv("DB_USER")
        self.db_password: str | None = os.getenv("DB_PASSWORD")
        self.db_host: str | None = os.getenv("DB_HOST")
        self.db_port: str | None = os.getenv("DB_PORT")
        self.db_name: str | None = os.getenv("DB_NAME")

        # Information éventuelle pour Sentry (non utilisée ici)
        self.sentry_dsn: str | None = os.getenv("SENTRY_DSN")

        # Construction de l’URL que requiert SQLAlchemy
        self.sqlalchemy_database_url: str = (
            f"{self.db_engine}://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


class DatabaseConnection:
    """
    Fabrique d’*engine* et de sessions SQLAlchemy.

    Exemple d’utilisation
    ---------------------
    >>> cfg = DatabaseConfig()
    >>> db = DatabaseConnection(cfg)
    >>> with db.create_session() as session:
    ...     # utiliser la session
    """

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config

        # Création de l’engine SQLAlchemy
        self.engine = create_engine(
            self.config.sqlalchemy_database_url,
            echo=False,                 # pas de SQL en sortie standard
        )

        # Fabrique de sessions (« sessionmaker »)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    # ------------------------------------------------------------------
    # API public
    # ------------------------------------------------------------------
    def create_session(self):
        """
        Ouvre et renvoie une nouvelle session SQLAlchemy.

        L’appelant est responsable de fermer la session (via
        `session.close()` ou contexte *with*) après utilisation.
        """
        return self.SessionLocal()
