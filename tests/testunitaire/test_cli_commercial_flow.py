# tests/testunitaire/test_cli_commercial_flow.py
"""Parcours complet du sous‑menu “Gestion” pour un utilisateur *commercial*.

But :
    • S’assurer qu’aucune exception n’est levée.
    • Chaque sous‑menu (clients, contrats, événements) est visité au moins
      une fois.
"""
import builtins
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

# --- Doubles simples -------------------------------------------------- #


class _DummySession:
    def close(self): ...


class _DummyDB:
    def create_session(self):  # noqa: D401  (méthode courte)
        return _DummySession()


class TestCLICommercialFlow(unittest.TestCase):
    """Tests du flux CLI pour le rôle *commercial*."""

    # ------------------------------------------------------------------ #
    def setUp(self) -> None:
        """Prépare les entrées simulées, patches et redirections stdout."""
        self._inputs = iter(
            ["1", "0",  # Clients
             "2", "0",  # Contrats
             "3", "0",  # Événements
             "0"]       # Quitter Gestion
        )
        self._orig_input = builtins.input
        builtins.input = lambda *_: next(self._inputs)

        self._patch_login = patch(
            "app.views.login_view.LoginView.login_with_credentials_return_user"
        )
        self._patch_login.start()
        self.addCleanup(self._patch_login.stop)

        self._buf = StringIO()
        self._redir_ctx = redirect_stdout(self._buf)
        self._redir_ctx.__enter__()
        self.addCleanup(self._redir_ctx.__exit__, None, None, None)

        from app.views.cli_interface import CLIInterface
        self.cli = CLIInterface(_DummyDB())
        self.cli.current_user = {"id": 42, "role": "commercial", "role_id": 1}

    def tearDown(self) -> None:
        """Restaure la fonction *input* d’origine."""
        builtins.input = self._orig_input

    # ------------------------------------------------------------------ #
    def test_full_flow(self) -> None:
        """Le sous‑menu Gestion se déroule sans lever d’exception."""
        try:
            self.cli._write_menu()
        except StopIteration:
            pass  # fin normale : plus d’inputs simulés

        out = self._buf.getvalue()
        self.assertIn("-- Clients --", out)
        self.assertIn("-- Contrats (commercial) --", out)
        self.assertIn("-- Événements (commercial) --", out)


if __name__ == "__main__":
    unittest.main()
