import unittest
import builtins
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

from app.views.login_view import LoginView
from app.authentification.auth_controller import AuthController


# -------- petite connexion factice -------- #
class DummyDBConnection:
    def create_session(self):
        class S:            # session vide
            def close(self): pass
        return S()


class TestLoginView(unittest.TestCase):
    def setUp(self):
        self.orig_input = builtins.input
        self.db = DummyDBConnection()
        self.view = LoginView(self.db)

    def tearDown(self):
        builtins.input = self.orig_input

    # ---------- helper pour injecter les réponses ---------- #
    def _feed_input(self, *values):
        it = iter(values)
        builtins.input = lambda *_: next(it)

    # ------------------- succès ---------------------------- #
    def test_login_success(self):
        ctrl = AuthController()

        # objet user minimaliste mais suffisamment rempli
        MockRole = type("Role", (), {"name": "commercial"})
        MockUser = type(
            "User", (),
            {"id": 1, "role": MockRole, "email": "good@x"}
        )

        with patch.object(ctrl, "authenticate_user", return_value=MockUser):
            self.view.auth_controller = ctrl
            self._feed_input("good@x", "pwd")

            buff = StringIO()
            with redirect_stdout(buff):
                self.view.login()

            self.assertIn("Authentification réussie", buff.getvalue())

    # ------------------- échec ----------------------------- #
    def test_login_failure(self):
        ctrl = AuthController()
        with patch.object(ctrl, "authenticate_user", return_value=None):
            self.view.auth_controller = ctrl
            self._feed_input("bad@x", "bad")

            buff = StringIO()
            with redirect_stdout(buff):
                self.view.login()

            self.assertIn("Échec de l'authentification", buff.getvalue())
