# app/config/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Exemple d'URL de connexion SQLite - on peut utiliser un chemin absolu ou relatif.
# Si vous utilisez python-dotenv, vous pouvez charger un .env contenant la variable DB_PATH
# DB_PATH = os.getenv("DB_PATH", "epic_events_crm.db")
DB_FILE = "epic_events_crm.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# Crée un engine SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # passer à True pour voir les requêtes SQL en debug
    # nécessaire uniquement pour SQLite (threads)
    connect_args={"check_same_thread": False}
)

# Crée une factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Générateur de sessions pour être utilisé, par exemple,
    dans les contrôleurs (ou plus tard, dans un contexte with).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
