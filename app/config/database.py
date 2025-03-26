# app/config/database.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseConfig:
    """
    Classe chargée de configurer les variables liées à la base de données
    et éventuellement le DSN Sentry, en lisant le fichier .env.
    """

    def __init__(self):
        # Charge les variables depuis .env (s'il existe)
        load_dotenv()

        # Lecture du chemin de la base SQLite
        db_file = os.getenv("DB_PATH", "epic_events_crm.db")
        # Stocke l'URL de connexion SQLite
        self.sqlalchemy_database_url = "sqlite:///" + db_file

        # Sentry (optionnel)
        self.sentry_dsn = os.getenv("SENTRY_DSN", None)


class DatabaseConnection:
    """
    Classe gérant la connexion à la base via SQLAlchemy.
    """

    def __init__(self, config: DatabaseConfig):
        # On stocke l'objet de configuration
        self.config = config

        # Création de l'engine SQLAlchemy
        self.engine = create_engine(
            self.config.sqlalchemy_database_url,
            echo=False,  # mettre True pour débug (affiche les requêtes SQL)
            # Requis pour SQLite en multi-threads
            connect_args={"check_same_thread": False}
        )

        # Factory de sessions
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_session(self):
        """
        Retourne une nouvelle session. À l'appelant de la fermer après usage:
            session = self.create_session()
            # ... session.execute() ...
            session.close()
        """
        return self.SessionLocal()
