import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseConfig:
    """
    Classe chargée de configurer les variables liées à la base de données
    MySQL (et éventuellement Sentry), en lisant le fichier .env.
    """

    def __init__(self):
        # Charge les variables depuis .env (s'il existe)
        load_dotenv()

        # Récupère le moteur (par ex "mysql+pymysql")
        self.db_engine = os.getenv("DB_ENGINE", "mysql+pymysql")
        self.db_user = os.getenv("DB_USER", "epicuser")
        self.db_password = os.getenv("DB_PASSWORD", "")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "3306")
        self.db_name = os.getenv("DB_NAME", "epic_db")

        # Sentry (optionnel)
        self.sentry_dsn = os.getenv("SENTRY_DSN", None)

        # Construit l'URL de connexion SQLAlchemy
        # Ex: mysql+pymysql://user:pass@host:port/dbname
        self.sqlalchemy_database_url = (
            f"{self.db_engine}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


class DatabaseConnection:
    """
    Classe gérant la connexion à la base via SQLAlchemy.
    """

    def __init__(self, config: DatabaseConfig):
        # On stocke l'objet de configuration
        self.config = config

        # Création de l'engine SQLAlchemy pour MySQL
        self.engine = create_engine(
            self.config.sqlalchemy_database_url,
            echo=False  # mettre True pour débug (affiche les requêtes)
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
