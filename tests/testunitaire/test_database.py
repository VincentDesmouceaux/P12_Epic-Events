"""
Tests basiques de la couche DatabaseConnection.

• Création d’une session SQLAlchemy ;
• exécution d’un `SELECT 1` pour vérifier la connectivité.
"""

from __future__ import annotations

import unittest
from sqlalchemy import text


from app.config.database import DatabaseConfig, DatabaseConnection


class TestDatabaseConnection(unittest.TestCase):
    """Assure la bonne configuration d’une connexion SQLAlchemy."""

    def setUp(self) -> None:
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)

    def tearDown(self) -> None:
        # Ferme proprement l’engine pour libérer les ressources.
        self.db_connection.engine.dispose()

    def test_session_creation(self) -> None:
        """Une session doit pouvoir être ouverte puis fermée."""
        session = self.db_connection.create_session()
        self.assertIsNotNone(session)
        session.close()

    def test_select_one(self) -> None:
        """`SELECT 1` doit retourner exactement 1."""
        session = self.db_connection.create_session()
        result = session.execute(text("SELECT 1"))
        self.assertEqual(result.scalar_one(), 1)
        session.close()


if __name__ == "__main__":
    unittest.main()
