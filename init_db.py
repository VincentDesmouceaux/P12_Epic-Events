# app/init_db.py
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base


def init_db():
    config = DatabaseConfig()
    connection = DatabaseConnection(config)
    engine = connection.engine

    print("Suppression des tables existantes...")
    Base.metadata.drop_all(bind=engine)
    print("Création du schéma (tables)...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")


if __name__ == "__main__":
    init_db()
