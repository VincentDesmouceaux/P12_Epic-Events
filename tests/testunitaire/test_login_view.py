import unittest
from io import StringIO
import sys
from unittest.mock import patch

from app.views.login_view import LoginView
from app.config.database import DatabaseConfig, DatabaseConnection
from app.authentification.auth_controller import AuthController
from app.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.role import Role


class TestLoginView(unittest.TestCase):
    """
    Tests unitaires pour la vue de connexion (LoginView)
    """

    def setUp(self):
        # Créer une base de données SQLite en mémoire pour les tests
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Insérer un rôle de test (ex: "commercial")
        test_role = Role(name="commercial", description="Rôle de test")
        session.add(test_role)
        session.commit()

        # Initialiser l'AuthController et enregistrer un utilisateur de test
        auth_ctrl = AuthController()
        # On enregistre l'utilisateur avec email "test@example.com" et mot de passe "password123"
        auth_ctrl.register_user(
            session=session,
            employee_number="EMP100",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="password123",
            role_id=test_role.id
        )
        session.close()

        # Instancier LoginView et forcer l'utilisation de notre base en mémoire
        self.login_view = LoginView()
        # Remplacer l'engine et la factory de sessions de la connexion pour utiliser la DB en mémoire
        self.login_view.db_conn.engine = self.engine
        self.login_view.db_conn.SessionLocal = Session
        # Utiliser notre instance d'AuthController (pour garantir la cohérence)
        self.login_view.auth_controller = auth_ctrl

    def test_login_success(self):
        """
        Vérifie que le login réussit avec les bonnes informations.
        """
        # Simuler l'input utilisateur pour email et mot de passe corrects
        with patch('builtins.input', side_effect=["test@example.com", "password123"]):
            captured_output = StringIO()
            sys.stdout = captured_output
            self.login_view.login()
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            self.assertIn("Authentification réussie", output)
            self.assertIn("Votre jeton JWT est :", output)

    def test_login_failure(self):
        """
        Vérifie que le login échoue avec un mauvais mot de passe.
        """
        with patch('builtins.input', side_effect=["test@example.com", "wrongpassword"]):
            captured_output = StringIO()
            sys.stdout = captured_output
            self.login_view.login()
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            self.assertIn("Échec de l'authentification", output)


if __name__ == '__main__':
    unittest.main()
