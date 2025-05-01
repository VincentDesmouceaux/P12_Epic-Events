"""
Tests unitaires – LoginView
---------------------------
Vérifie l’affichage des messages :
  • succès si l’authentification fonctionne
  • échec sinon
"""

import builtins
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

from app.views.login_view import LoginView
from app.authentification.auth_controller import AuthController


# ------------------------------------------------------------------ #
#  Double très simple pour la connexion BD                           #
# ------------------------------------------------------------------ #
class _DummyDB:
    def create_session(self):
        class _Sess:          # session inerte (pas de SGBDR réel)
            def close(self): ...
        return _Sess()


# ------------------------------------------------------------------ #
#  Suite de tests                                                    #
# ------------------------------------------------------------------ #
class TestLoginView(unittest.TestCase):
    # ----------------------------- setUp --------------------------- #
    def setUp(self):
        self._orig_input = builtins.input
        self.db = _DummyDB()
        self.view = LoginView(self.db)

    # --------------------------- tearDown -------------------------- #
    def tearDown(self):
        builtins.input = self._orig_input

    # ------------------ aide : injection d’inputs ------------------ #
    def _feed_input(self, *vals):
        """Remplace la fonction input pour renvoyer en séquence `vals`."""
        it = iter(vals)
        builtins.input = lambda *_: next(it)

    # ------------------------ test succès -------------------------- #
    def test_login_success(self):
        ctrl = AuthController()

        # --- objet utilisateur minimal mais complet -----------------
        MockRole = type("Role", (), {"name": "commercial"})
        MockUser = type(
            "User",
            (),
            {"id": 1, "role": MockRole(), "email": "good@x"}
        )()

        # on patch :  authenticate_user (→ MockUser)
        #             generate_token     (→ valeur factice)
        with patch.object(ctrl, "authenticate_user", return_value=MockUser), \
                patch.object(ctrl, "generate_token", return_value="TOKEN"):
            self.view.auth_controller = ctrl
            self._feed_input("good@x", "pwd")

            capture = StringIO()
            with redirect_stdout(capture):
                self.view.login()

            self.assertIn("Authentification réussie", capture.getvalue())

    # ------------------------ test échec --------------------------- #
    def test_login_failure(self):
        ctrl = AuthController()
        with patch.object(ctrl, "authenticate_user", return_value=None):
            self.view.auth_controller = ctrl
            self._feed_input("bad@x", "bad")

            capture = StringIO()
            with redirect_stdout(capture):
                self.view.login()

            self.assertIn("Échec de l'authentification", capture.getvalue())


# ------------------------------------------------------------------ #
#  Exécution directe                                                 #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    unittest.main()
