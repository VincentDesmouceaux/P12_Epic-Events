# tests/testunitaire/test_cli_interface.py
import unittest
from io import StringIO
import sys
import builtins
from unittest.mock import patch

from app.views.cli_interface import CLIInterface
from app.models import Base
from app.models.role import Role

# DummyDBConnection simulant une connexion DB in-memory


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        # Insérer un rôle minimal
        session = self.create_session()
        role = Role(id=2, name="commercial", description="Test Role")
        session.add(role)
        session.commit()
        session.close()

    def create_session(self):
        return self.SessionLocal()


class TestCLIInterface(unittest.TestCase):
    def setUp(self):
        self.original_input = builtins.input
        self.db_conn = DummyDBConnection()
        self.cli = CLIInterface(self.db_conn)
        # Simuler un utilisateur connecté pour tester les menus internes
        self.cli.current_user = {"id": 1, "role": "gestion"}

    def tearDown(self):
        builtins.input = self.original_input

    def fake_input(self, values):
        self._input_values = iter(values)

        def fake_input_fn(prompt=""):
            print(prompt, end="")
            return next(self._input_values)
        return fake_input_fn

    def test_menu_quit(self):
        # Test que l'option 4 quitte le CLI
        user_inputs = ["4"]
        with patch('builtins.input', self.fake_input(user_inputs)), patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.run()
            output = fake_out.getvalue()
        self.assertIn("Au revoir.", output)

    def test_menu_invalid_choice(self):
        # Test pour une option invalide suivie de quitter
        user_inputs = ["9", "4"]
        with patch('builtins.input', self.fake_input(user_inputs)), patch('sys.stdout', new=StringIO()) as fake_out:
            self.cli.run()
            output = fake_out.getvalue()
        self.assertIn("Option invalide.", output)

    def test_menu_login_fail_then_quit(self):
        # Simuler un login qui échoue
        def dummy_login_fail(email, pwd):
            return None

        with patch.object(self.cli.login_view, 'login_with_credentials_return_user', side_effect=dummy_login_fail):
            user_inputs = ["1", "bad@example.com", "wrongpass", "4"]
            with patch('builtins.input', self.fake_input(user_inputs)), patch('sys.stdout', new=StringIO()) as fake_out:
                self.cli.run()
                output = fake_out.getvalue()
            self.assertIn("Échec de l'authentification.", output)

    def test_menu_login_success_then_quit(self):
        # Simuler un login réussi
        class DummyRole:
            name = "gestion"

        class DummyUser:
            def __init__(self):
                self.id = 42
                self.role = DummyRole()

        def dummy_login_success(email, pwd):
            return DummyUser()

        with patch.object(self.cli.login_view, 'login_with_credentials_return_user', side_effect=dummy_login_success):
            user_inputs = ["1", "good@example.com", "secretpass", "4"]
            with patch('builtins.input', self.fake_input(user_inputs)), patch('sys.stdout', new=StringIO()) as fake_out:
                self.cli.run()
                output = fake_out.getvalue()
            self.assertIn("Authentification réussie.", output)
            self.assertIn("Rôle=gestion", output)


if __name__ == "__main__":
    unittest.main()
