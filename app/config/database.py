# app/config/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()


class DatabaseConfig:
    """
    Configuration de la base de données à partir des variables d'environnement.
    """

    def __init__(self):
        self.db_engine = os.getenv("DB_ENGINE")            # ex: mysql+pymysql
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.sqlalchemy_database_url = (
            f"{self.db_engine}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class DatabaseConnection:
    """
    Gère la connexion à la base via SQLAlchemy.
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(
            self.config.sqlalchemy_database_url, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_session(self):
        return self.SessionLocal()
