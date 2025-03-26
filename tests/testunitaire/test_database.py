import unittest
from app.config.database import DatabaseConfig, DatabaseConnection
from sqlalchemy import text


class TestDatabaseConnection(unittest.TestCase):
    """
    Classe de tests unitaires pour la connexion à la base de données MySQL.
    """

    def setUp(self):
        """
        Méthode appelée avant chaque test.
        On instancie la config et la connexion DB.
        """
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)

    def tearDown(self):
        """
        Méthode appelée après chaque test.
        Ici, on pourrait fermer ou nettoyer la DB, si besoin.
        """
        pass

    def test_session_creation(self):
        """
        Teste la création d'une session via la DatabaseConnection.
        """
        session = self.db_connection.create_session()
        self.assertIsNotNone(session, "La session ne doit pas être None.")
        session.close()

    def test_select_one(self):
        """
        Exécute une requête simple pour vérifier que la base MySQL répond.
        """
        session = self.db_connection.create_session()
        result = session.execute(text("SELECT 1"))
        row = result.fetchone()
        self.assertIsNotNone(
            row, "La requête SELECT 1 doit retourner au moins une ligne.")
        self.assertEqual(row[0], 1, "SELECT 1 doit retourner 1.")
        session.close()


if __name__ == '__main__':
    unittest.main()
