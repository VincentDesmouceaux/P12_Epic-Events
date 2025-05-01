"""
Parcours CLI pour un utilisateur de rôle « support »
----------------------------------------------------
Objectifs vérifiés
  • Le sous-menu Événements est bien accessible depuis Gestion.
  • L’action « Mes événements » est appelée exactement 1 fois.
  • L’action « Mettre à jour un événement » est appelée exactement 1 fois.
  • Aucune exception n’est levée pendant la navigation.
Toutes les méthodes DataWriterView utilisées sont patchées pour éviter
tout accès réel à la base.
"""

import builtins
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

# ------------------------------------------------------------------ #
#  Doubles très simples pour la couche « BD »                        #
# ------------------------------------------------------------------ #


class _DummySession:          # session inerte
    def close(self): ...


class _DummyDB:               # connection inerte
    def create_session(self): return _DummySession()

# ------------------------------------------------------------------ #
#  Suite de tests                                                    #
# ------------------------------------------------------------------ #


class TestCLISupportFlow(unittest.TestCase):
    # -------------------------- setUp ------------------------------ #
    def setUp(self):
        # ­Injecte les saisies clavier :
        #   1) Gestion->Événements
        #   2) Sous-menu: [1] Mes évts
        #   3) Sous-menu: [2] Update
        #   4) Retour sous-menu (0)
        #   5) Retour Gestion (0)
        self._orig_input = builtins.input
        seq = iter(["1", "1", "2", "0", "0"])
        builtins.input = lambda *_: next(seq)

        # Instancie le CLI avec une “BD” factice et un user support connecté
        from app.views.cli_interface import CLIInterface
        self.cli = CLIInterface(_DummyDB())
        self.cli.current_user = {"id": 42, "role": "support", "role_id": 2}

        # Patch des deux méthodes internes ajoutées dans DataWriterView
        # (_display_my_events et _update_my_event_cli)
        self._patch_display = patch.object(
            self.cli.writer_v, "_display_my_events", MagicMock())
        self._patch_update = patch.object(
            self.cli.writer_v, "_update_my_event_cli", MagicMock())

        self._patch_display.start()
        self._patch_update.start()

    # ------------------------- tearDown ---------------------------- #
    def tearDown(self):
        builtins.input = self._orig_input
        self._patch_display.stop()
        self._patch_update.stop()

    # --------------------------- test ------------------------------ #
    def test_full_flow(self):
        """Navigation complète : doit déclencher exactement les deux actions."""
        with StringIO() as buf, redirect_stdout(buf):
            # On teste uniquement le menu “Gestion”
            self.cli._write_menu()
            console_out = buf.getvalue()

        # === Assertions ============================================ #
        self.cli.writer_v._display_my_events.assert_called_once()
        self.cli.writer_v._update_my_event_cli.assert_called_once()

        # Vérifie que les entêtes principaux ont bien été imprimés.
        self.assertIn("-- Gestion --", console_out)
        self.assertIn("-- Événements (support) --", console_out)


# ------------------------------------------------------------------ #
#  Lancement direct du fichier                                       #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    unittest.main()
