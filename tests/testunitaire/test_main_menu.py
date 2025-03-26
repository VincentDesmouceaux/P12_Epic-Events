import unittest
from io import StringIO
import sys
import builtins  # Pour accéder à la fonction input d'origine

from app.views.main_menu import MainMenu
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.models import Base

# Classe DummyDBConnection qui crée une DB SQLite en mémoire et les tables


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        # Créer les tables (toutes les tables déclarées dans Base)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.SessionLocal()


class TestMainMenu(unittest.TestCase):
    def setUp(self):
        self.original_input = builtins.input
        dummy_conn = DummyDBConnection()
        self.menu = MainMenu(dummy_conn)

    def tearDown(self):
        builtins.input = self.original_input

    def fake_input(self, values):
        self._input_values = iter(values)

        def fake_input_fn(prompt=""):
            print(prompt, end="")  # simule l'affichage du prompt
            return next(self._input_values)
        return fake_input_fn

    def test_menu_quit(self):
        """
        Vérifie que l'option "4" permet de quitter le menu.
        """
        builtins.input = self.fake_input(["4"])
        captured_output = StringIO()
        sys.stdout = captured_output
        self.menu.show()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Choisissez", output)

    def test_menu_login_called(self):
        """
        Vérifie que l'option "1" du menu appelle LoginView.login().
        """
        login_called = {"called": False}

        def dummy_login(self):
            login_called["called"] = True
        original_login = LoginView.login
        LoginView.login = dummy_login

        builtins.input = self.fake_input(
            ["1", "test@example.com", "password123", "4"])
        self.menu.show()
        LoginView.login = original_login
        self.assertTrue(
            login_called["called"], "La méthode login() doit être appelée pour l'option 1.")

    def test_menu_data_reader_called(self):
        """
        Vérifie que l'option "2" du menu appelle DataReaderView.display_data().
        """
        display_called = {"called": False}

        def dummy_display(self, current_user):
            display_called["called"] = True
        original_display = DataReaderView.display_data
        DataReaderView.display_data = dummy_display

        builtins.input = self.fake_input(["2", "4"])
        self.menu.show()
        DataReaderView.display_data = original_display
        self.assertTrue(
            display_called["called"], "La méthode display_data() doit être appelée pour l'option 2.")


if __name__ == "__main__":
    unittest.main()
