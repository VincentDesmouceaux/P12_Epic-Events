import unittest
from io import StringIO
import sys
import builtins  # Pour accéder à la fonction input d'origine

from app.views.main_menu import MainMenu
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView

# Classe DummyDBConnection pour simuler une connexion à la base (SQLite en mémoire)


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_session(self):
        return self.SessionLocal()


class TestMainMenu(unittest.TestCase):
    def setUp(self):
        # Sauvegarder la fonction input d'origine via le module builtins
        self.original_input = builtins.input
        # Instanciation de MainMenu avec une connexion dummy
        dummy_conn = DummyDBConnection()
        self.menu = MainMenu(dummy_conn)

    def tearDown(self):
        # Restauration de la fonction input d'origine
        builtins.input = self.original_input

    def fake_input(self, values):
        """
        Renvoie une fonction input simulée qui affiche le prompt et retourne les valeurs de la liste l'une après l'autre.
        """
        self._input_values = iter(values)

        def fake_input_fn(prompt=""):
            print(prompt, end="")  # Simule l'affichage du prompt
            return next(self._input_values)
        return fake_input_fn

    def test_menu_quit(self):
        """
        Vérifie que l'option "3" permet de quitter le menu.
        """
        builtins.input = self.fake_input(["3"])
        captured_output = StringIO()
        sys.stdout = captured_output
        self.menu.show()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        # On vérifie que le prompt affiché contient "Choisissez"
        self.assertIn("Choisissez", output)

    def test_menu_login_called(self):
        """
        Vérifie que l'option "1" du menu appelle LoginView.login().
        """
        login_called = {"called": False}

        def dummy_login(self):
            login_called["called"] = True
        # Sauvegarder la méthode originale
        original_login = LoginView.login
        LoginView.login = dummy_login

        # Simuler la séquence : option "1", puis les entrées de login, puis "3" pour quitter
        builtins.input = self.fake_input(
            ["1", "test@example.com", "password123", "3"])
        self.menu.show()
        # Rétablir la méthode originale
        LoginView.login = original_login

        self.assertTrue(
            login_called["called"], "LoginView.login doit être appelée pour l'option 1.")

    def test_menu_data_reader_called(self):
        """
        Vérifie que l'option "2" du menu appelle DataReaderView.display_data().
        """
        display_called = {"called": False}

        def dummy_display(self, current_user):
            display_called["called"] = True
        # Sauvegarder la méthode originale
        original_display = DataReaderView.display_data
        DataReaderView.display_data = dummy_display

        # Simuler la séquence : option "2", puis "3" pour quitter
        builtins.input = self.fake_input(["2", "3"])
        self.menu.show()
        # Rétablir la méthode originale
        DataReaderView.display_data = original_display

        self.assertTrue(
            display_called["called"], "DataReaderView.display_data doit être appelée pour l'option 2.")


if __name__ == "__main__":
    unittest.main()
