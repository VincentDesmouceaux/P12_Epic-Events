# tests/testunitaire/test_login_view.py
# -*- coding: utf-8 -*-
"""
Tests unitaires – `LoginView`.

Vérifie :
    • le message affiché après un succès d’authentification ;
    • le message affiché après un échec.
"""

import builtins
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

from app.views.login_view import LoginView
from app.authentification.auth_controller import AuthController


class _DummyDB:
    """Double simplifié de connexion BD (aucun accès réel)."""

    def create_session(self):
        class _Sess:
            """Session vide qui respecte simplement l’interface attendue."""

            def close(self):
                """Fin de session (noop)."""
                ...

        return _Sess()


class TestLoginView(unittest.TestCase):
    """Tests portant sur l’affichage de `LoginView.login()`."""

    # ------------------------------------------------------------------ #
    # SET‑UP / TEAR‑DOWN                                                 #
    # ------------------------------------------------------------------ #
    def setUp(self):
        self._orig_input = builtins.input
        self.db = _DummyDB()
        self.view = LoginView(self.db)

    def tearDown(self):
        builtins.input = self._orig_input

    # ------------------------------------------------------------------ #
    # OUTILS                                                             #
    # ------------------------------------------------------------------ #
    def _feed_input(self, *values):
        """Substitue `input()` pour retourner les valeurs fournies."""
        iterator = iter(values)
        builtins.input = lambda *_: next(iterator)

    # ------------------------------------------------------------------ #
    # TESTS                                                              #
    # ------------------------------------------------------------------ #
    def test_login_success(self):
        """Le message de succès doit être affiché après une connexion valide."""
        ctrl = AuthController()

        MockRole = type("Role", (), {"name": "commercial"})
        MockUser = type(
            "User", (), {"id": 1, "role": MockRole(), "email": "good@x"}
        )()

        with patch.object(ctrl, "authenticate_user", return_value=MockUser), patch.object(
            ctrl, "generate_token", return_value="TOKEN"
        ):
            self.view.auth_controller = ctrl
            self._feed_input("good@x", "pwd")

            capture = StringIO()
            with redirect_stdout(capture):
                self.view.login()

            self.assertIn("Authentification réussie", capture.getvalue())

    def test_login_failure(self):
        """Le message d’échec doit apparaître si l’authentification rate."""
        ctrl = AuthController()
        with patch.object(ctrl, "authenticate_user", return_value=None):
            self.view.auth_controller = ctrl
            self._feed_input("bad@x", "bad")

            capture = StringIO()
            with redirect_stdout(capture):
                self.view.login()

            self.assertIn("Échec de l'authentification", capture.getvalue())


if __name__ == "__main__":
    unittest.main()
