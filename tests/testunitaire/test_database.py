# tests/testunitaire/test_database.py
import unittest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base


class TestDatabaseConnection(unittest.TestCase):
    """
    Tests pour la connexion à la base de données.
    """

    def setUp(self):
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)

    def tearDown(self):
        # Optionnel : fermer l'engine si nécessaire
        self.db_connection.engine.dispose()

    def test_session_creation(self):
        session = self.db_connection.create_session()
        self.assertIsNotNone(session, "La session doit être créée.")
        session.close()

    def test_select_one(self):
        session = self.db_connection.create_session()
        result = session.execute(text("SELECT 1"))
        row = result.fetchone()
        self.assertIsNotNone(
            row, "La requête doit retourner au moins une ligne.")
        self.assertEqual(row[0], 1, "La requête SELECT 1 doit retourner 1.")
        session.close()


if __name__ == '__main__':
    unittest.main()
