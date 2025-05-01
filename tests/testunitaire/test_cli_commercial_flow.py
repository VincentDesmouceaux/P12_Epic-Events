"""
Navigation complète dans le menu **Gestion** pour un utilisateur
« commercial ».  
On s’assure qu’aucune exception n’est levée et que chaque sous-menu
s’affiche au moins une fois.
"""

import builtins
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch

# ------------------------------------------------------------------ #
#  Doubles                                                            #
# ------------------------------------------------------------------ #


class _DummySession:
    def close(self): ...


class _DummyDB:
    def create_session(self): return _DummySession()


# ------------------------------------------------------------------ #
class TestCLICommercialFlow(unittest.TestCase):
    def setUp(self):
        # séquence d’inputs clavier
        self._inputs = iter([
            "1", "0",      # Clients  → retour
            "2", "0",      # Contrats → retour
            "3", "0",      # Événements → retour
            "0"            # Quitter Gestion
        ])
        self._orig_input = builtins.input
        builtins.input = lambda *_: next(self._inputs)

        # patch LoginView pour éviter l’authent
        self._patch_login = patch(
            "app.views.login_view.LoginView.login_with_credentials_return_user"
        )
        self._patch_login.start()
        self.addCleanup(self._patch_login.stop)

        # redirection stdout
        self._buf = StringIO()
        self._redir_ctx = redirect_stdout(self._buf)
        self._redir_ctx.__enter__()
        self.addCleanup(self._redir_ctx.__exit__, None, None, None)

        # instanciation CLI
        from app.views.cli_interface import CLIInterface
        self.cli = CLIInterface(_DummyDB())
        self.cli.current_user = {"id": 42, "role": "commercial", "role_id": 1}

    def tearDown(self):
        builtins.input = self._orig_input

    def test_full_flow(self):
        """Le sous-menu Gestion doit se dérouler sans erreur."""
        try:
            self.cli._write_menu()     # uniquement le menu Gestion
        except StopIteration:
            pass                       # fin normale

        out = self._buf.getvalue()
        # Les trois entêtes doivent apparaître
        self.assertIn("-- Clients --", out)
        self.assertIn("-- Contrats (commercial) --", out)
        self.assertIn("-- Événements (commercial) --", out)


if __name__ == "__main__":
    unittest.main()
