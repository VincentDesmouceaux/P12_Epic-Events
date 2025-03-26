import unittest
from io import StringIO
import sys
import builtins

from app.views.login_view import LoginView
from app.authentification.auth_controller import AuthController

# DummyDBConnection simule une connexion à la base (SQLite en mémoire) pour les tests


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_session(self):
        return self.SessionLocal()


class TestLoginView(unittest.TestCase):
    def setUp(self):
        # Sauvegarde de la fonction input d'origine
        self.original_input = builtins.input
        # Instanciation d'une connexion dummy
        self.db_conn = DummyDBConnection()
        # Instanciation de LoginView en lui passant la connexion dummy
        self.login_view = LoginView(self.db_conn)

    def tearDown(self):
        # Restauration de la fonction input d'origine
        builtins.input = self.original_input

    def fake_input(self, values):
        """Renvoie une fonction input simulée qui affiche le prompt et retourne les valeurs successivement."""
        self._input_values = iter(values)

        def fake_input_fn(prompt=""):
            print(prompt, end="")  # Simule l'affichage du prompt
            return next(self._input_values)
        return fake_input_fn

    def test_login_success(self):
        """
        Vérifie que le login réussit avec les bonnes informations.
        Pour ce test, nous patchons temporairement la méthode authenticate_user de AuthController.
        """
        auth_ctrl = AuthController()
        original_authenticate = auth_ctrl.authenticate_user

        def dummy_authenticate(session, email_arg, password_arg):
            if email_arg == "test@example.com" and password_arg == "password123":
                class DummyRole:
                    name = "commercial"

                class DummyUser:
                    def __init__(self, email):
                        self.id = 1
                        self.email = email
                        self.role = DummyRole()
                return DummyUser(email_arg)
            return None

        auth_ctrl.authenticate_user = dummy_authenticate
        self.login_view.auth_controller = auth_ctrl

        builtins.input = self.fake_input(["test@example.com", "password123"])
        captured_output = StringIO()
        sys.stdout = captured_output

        self.login_view.login()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Authentification réussie", output)
        self.assertIn("Votre jeton JWT est :", output)
        auth_ctrl.authenticate_user = original_authenticate

    def test_login_failure(self):
        """
        Vérifie que le login échoue avec un mauvais mot de passe.
        """
        auth_ctrl = AuthController()
        original_authenticate = auth_ctrl.authenticate_user

        def dummy_authenticate(session, email_arg, password_arg):
            return None

        auth_ctrl.authenticate_user = dummy_authenticate
        self.login_view.auth_controller = auth_ctrl

        builtins.input = self.fake_input(
            ["wrong@example.com", "wrongpassword"])
        captured_output = StringIO()
        sys.stdout = captured_output

        self.login_view.login()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Échec de l'authentification", output)
        auth_ctrl.authenticate_user = original_authenticate


if __name__ == "__main__":
    unittest.main()
