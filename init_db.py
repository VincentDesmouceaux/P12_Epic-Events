# init_db.py
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base


def init_db():
    config = DatabaseConfig()
    connection = DatabaseConnection(config)
    engine = connection.engine

    # Création (ou mise à jour) des tables.
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")


if __name__ == "__main__":
    init_db()
