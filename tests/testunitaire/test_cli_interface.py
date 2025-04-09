# tests/testunitaire/test_cli_interface.py
import unittest
from io import StringIO
import sys
import builtins
from unittest.mock import patch
from app.views.cli_interface import CLIInterface

# On a besoin de DummyDBConnection + éventuellement, on crée les tables
from app.models import Base
from app.models.role import Role


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        # On peut créer les tables ici
        Base.metadata.create_all(self.engine)
        # Créer au moins un rôle id=2
        session = self.create_session()
        new_role = Role(id=2, name="commercial", description="Dummy test role")
        session.add(new_role)
        session.commit()
        session.close()

    def create_session(self):
        return self.SessionLocal()


class TestCLIInterface(unittest.TestCase):
    def setUp(self):
        self.original_input = builtins.input
        self.db_conn = DummyDBConnection()
        self.cli = CLIInterface(self.db_conn)

    def tearDown(self):
        builtins.input = self.original_input
        # Optionnel : Base.metadata.drop_all(self.db_conn.engine)
        # self.db_conn.engine.dispose()

    def fake_input(self, values):
        self._input_values = iter(values)

        def fake_input_fn(prompt=""):
            print(prompt, end="")
            return next(self._input_values)
        return fake_input_fn

    def test_menu_quit(self):
        user_inputs = ["4"]
        builtin_input = self.fake_input(user_inputs)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with patch('builtins.input', builtin_input):
                self.cli.run()
            output = fake_out.getvalue()
            self.assertIn("Au revoir.", output)

    def test_menu_invalid_choice(self):
        user_inputs = ["9", "4"]
        builtin_input = self.fake_input(user_inputs)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            with patch('builtins.input', builtin_input):
                self.cli.run()
            output = fake_out.getvalue()
            self.assertIn("Option invalide.", output)

    def test_menu_login_fail_then_quit(self):
        """
        Teste un login raté => auth renvoie None
        """
        def dummy_login_with_credentials_return_user(email, pwd):
            return None

        with patch.object(
            self.cli.login_view,
            'login_with_credentials_return_user',
            side_effect=dummy_login_with_credentials_return_user
        ):
            user_inputs = [
                "1",                    # Choix=login
                "bad@example.com",      # email
                "wrongpass",            # password
                "4"                     # quitter
            ]
            builtin_input = self.fake_input(user_inputs)
            with patch('sys.stdout', new=StringIO()) as fake_out:
                with patch('builtins.input', builtin_input):
                    self.cli.run()
                output = fake_out.getvalue()
                self.assertIn("Échec de l'authentification.", output)

    def test_menu_login_success_then_quit(self):
        class DummyUser:
            def __init__(self, user_id, role_name):
                self.id = user_id

                class DummyRole:
                    name = role_name
                self.role = DummyRole()

        def dummy_login_ok(email, pwd):
            return DummyUser(42, "gestion")

        with patch.object(
            self.cli.login_view,
            'login_with_credentials_return_user',
            side_effect=dummy_login_ok
        ):
            user_inputs = [
                "1",        # login
                "good@example.com",
                "secretpass",
                "4"         # quit
            ]
            builtin_input = self.fake_input(user_inputs)
            with patch('sys.stdout', new=StringIO()) as fake_out:
                with patch('builtins.input', builtin_input):
                    self.cli.run()
                output = fake_out.getvalue()
                self.assertIn("Authentification réussie.", output)
                self.assertIn("Rôle=gestion", output)


if __name__ == "__main__":
    unittest.main()
