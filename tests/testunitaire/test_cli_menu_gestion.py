import builtins
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from contextlib import redirect_stdout


# ====================== doubles minimalistes ====================== #
class DummyRole:
    id = 3
    name = "gestion"


class DummyUser:
    """Objet User minimal doté d’un rôle « gestion »."""

    def __init__(self):
        self.id = 1
        self.role = DummyRole()


class DummySession:
    """Session factice : aucune vraie requête SQL exécutée."""

    def close(self):
        pass


class DummyDBConnection:
    """Connexion factice utilisée par le CLI."""

    def create_session(self):
        return DummySession()


# ============================ Tests =============================== #
class TestCLIMenuGestion(unittest.TestCase):
    """
    Parcours complet des menus pour un utilisateur de rôle « gestion ».

    Branches visitées :
      • Lecture   : clients, contrats, événements
      • Gestion   : collaborateurs (modifier),
                    contrats      (afficher puis retour),
                    événements    (afficher sans support puis assigner support)
    Aucune exception ne doit être levée pendant l’exécution.
    """

    # --------------------------- setUp ----------------------------- #
    def setUp(self):
        # 1) Script des réponses passées à input()
        self._inputs = iter([
            # ===== Connexion =====
            "1", "gest@example.com", "pwd",

            # ===== Menu Lecture (principal -> 2) =====
            "2",        # ouvrir menu Lecture
            "1",  # clients
            "2",  # contrats
            "3",  # événements
            "0",  # retour menu principal

            # ===== Menu Gestion (principal -> 3) =====
            "3",

            # -- Collaborateurs : Modifier --
            "1",  # menu Collaborateurs
            "2",  # modifier

            # -- Contrats : simple affichage --
            "2",  # menu Contrats
            "0",  # retour sous-menu Contrats

            # -- Événements : afficher sans support puis assigner --
            "3", "1",  # afficher sans support
            "3", "2",  # assigner / modifier support

            # -- Quitter --
            "0",  # retour menu Gestion
            "0"  # quitter application
        ])
        self._orig_input = builtins.input
        builtins.input = lambda *_: next(self._inputs)

        # 2) Redirige la sortie standard pour ne rien afficher
        self._stdout_buf = StringIO()
        self._redirect_ctx = redirect_stdout(self._stdout_buf)
        self._redirect_ctx.__enter__()

        # 3) Patch du LoginView (auth toujours OK)
        self._patch_login = patch(
            "app.views.login_view.LoginView.login_with_credentials_return_user",
            return_value=DummyUser()
        )
        self._patch_login.start()

        # 4) Patch des méthodes appelées dans le scénario
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

        # 5) Instanciation du CLI avec la connexion factice
        from app.views.cli_interface import CLIInterface
        self.cli = CLIInterface(DummyDBConnection())

    # -------------------------- tearDown --------------------------- #
    def tearDown(self):
        builtins.input = self._orig_input
        self._redirect_ctx.__exit__(None, None, None)
        self._patch_login.stop()
        for p in self._patchers:
            p.stop()

    # ---------------------------- test ----------------------------- #
    def test_full_cli_flow_for_gestion(self):
        """Exécution complète : doit se terminer sans exception."""
        try:
            self.cli.run()
        except StopIteration:
            # Fin normale : l’itérateur d’inputs est épuisé.
            pass

        # Classes déjà patchées
        from app.views.data_reader_view import DataReaderView
        from app.views.data_writer_view import DataWriterView

        # ===== Vérifications Lecture =====
        DataReaderView.display_clients_only.assert_called_once()
        DataReaderView.display_contracts_only.assert_called_once()
        DataReaderView.display_events_only.assert_called_once()

        # ===== Vérifications Gestion =====
        self.assertGreaterEqual(
            DataWriterView.update_user_cli.call_count, 1,
            "update_user_cli (modifier collaborateur) doit être appelé ≥ 1 fois"
        )
        DataWriterView.list_events_no_support.assert_called_once()
        DataWriterView.assign_support_cli.assert_called_once()


if __name__ == "__main__":
    unittest.main()
