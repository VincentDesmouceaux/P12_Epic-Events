# Par exemple dans un script "init_db.py" (hors du code principal)
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base


def init_db():
    config = DatabaseConfig()
    connection = DatabaseConnection(config)
    engine = connection.engine

    # Création des tables
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")


if __name__ == "__main__":
    init_db()
