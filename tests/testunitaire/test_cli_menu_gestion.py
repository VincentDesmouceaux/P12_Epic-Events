# tests/testunitaire/test_cli_menu_gestion.py
"""Parcours complet des menus pour un utilisateur *gestion*.

Le test simule toutes les branches (lecture + gestion) et s’assure
qu’aucune exception n’est levée ainsi que la bonne invocation
des méthodes internes patchées.
"""
import builtins
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch


# --- Doubles -----------------------------------------------------------------
class DummyRole:
    """Rôle fictif `gestion` – utilisé par *DummyUser*."""
    id = 3
    name = "gestion"


class DummyUser:
    """Utilisateur minimal possédant le rôle `gestion`."""

    def __init__(self):
        self.id = 1
        self.role = DummyRole()


class DummySession:
    """Session SQLAlchemy factice (aucune requête exécutée)."""

    def close(self): ...


class DummyDBConnection:
    """Connexion BD factice compatible avec `CLIInterface`."""

    def create_session(self):
        return DummySession()


class TestCLIMenuGestion(unittest.TestCase):
    """Tests de navigation pour le rôle *gestion*."""

    # ---------------------------------------------------------------------- #
    def setUp(self) -> None:
        """Crée la séquence d’inputs et applique les patches nécessaires."""
        self._inputs = iter([
            # Connexion
            "1", "gest@example.com", "pwd",
            # Lecture
            "2", "1", "2", "3", "0",
            # Gestion
            "3", "1", "2",           # collaborateurs / modifier
            "2", "0",                # contrats / retour
            "3", "1", "3", "2",      # événements (sans support + assigner)
            "0", "0"                 # retour + quitter
        ])
        self._orig_input = builtins.input
        builtins.input = lambda *_: next(self._inputs)

        # Redirection stdout pour ne pas polluer la console
        self._stdout = StringIO()
        self._redir = redirect_stdout(self._stdout)
        self._redir.__enter__()

        # Patch LoginView pour bypasser l’authentification
        self._patch_login = patch(
            "app.views.login_view.LoginView.login_with_credentials_return_user",
            return_value=DummyUser(),
        )
        self._patch_login.start()

        # Patch des méthodes appelées dans le scénario
        to_patch = {
            # lecture
            "app.views.data_reader_view.DataReaderView.display_clients_only",
            "app.views.data_reader_view.DataReaderView.display_contracts_only",
            "app.views.data_reader_view.DataReaderView.display_events_only",
            # écriture
            "app.views.data_writer_view.DataWriterView.update_user_cli",
            "app.views.data_writer_view.DataWriterView.delete_user_cli",
            "app.views.data_writer_view.DataWriterView.list_events_no_support",
            "app.views.data_writer_view.DataWriterView.assign_support_cli",
        }
        self._patchers = [patch(t, MagicMock()) for t in to_patch]
        for p in self._patchers:
            p.start()

        # Instanciation du CLI
        from app.views.cli_interface import CLIInterface
        self.cli = CLIInterface(DummyDBConnection())

    # ---------------------------------------------------------------------- #
    def tearDown(self) -> None:
        """Nettoyage des patches et restauration de *input* / stdout."""
        builtins.input = self._orig_input
        self._redir.__exit__(None, None, None)
        self._patch_login.stop()
        for p in self._patchers:
            p.stop()

    # ---------------------------------------------------------------------- #
    def test_full_cli_flow_for_gestion(self) -> None:
        """Exécute le scénario complet sans lever d’exception."""
        try:
            self.cli.run()
        except StopIteration:
            # Fin normale : plus d’inputs simulés
            pass

        # Vérifications sur les méthodes patchées
        from app.views.data_reader_view import DataReaderView
        from app.views.data_writer_view import DataWriterView

        DataReaderView.display_clients_only.assert_called_once()
        DataReaderView.display_contracts_only.assert_called_once()
        DataReaderView.display_events_only.assert_called_once()
        self.assertGreaterEqual(
            DataWriterView.update_user_cli.call_count, 1,
        )
        DataWriterView.list_events_no_support.assert_called_once()
        DataWriterView.assign_support_cli.assert_called_once()


if __name__ == "__main__":
    unittest.main()
