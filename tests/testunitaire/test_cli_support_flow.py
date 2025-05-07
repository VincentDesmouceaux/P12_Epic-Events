"""
Tests CLI – parcours complet pour un utilisateur « support ».

But :
    • s’assurer que le sous‑menu *Événements* est bien accessible
      depuis la section *Gestion* ;
    • vérifier que les deux actions internes
        – _display_my_events
        – _update_my_event_cli
      sont appelées exactement une fois ;
    • garantir l’absence d’exception pendant la navigation.

Toutes les méthodes de DataWriterView sont patchées : jamais d’accès
réel à la base de données.
"""

from __future__ import annotations

import builtins
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import MagicMock, patch


class _DummySession:
    """Session SQLAlchemy vide : aucune requête exécutée."""

    def close(self) -> None:  # noqa: D401
        pass


class _DummyDB:
    """Connexion factice : renvoie toujours une _DummySession."""

    def create_session(self) -> _DummySession:  # noqa: D401
        return _DummySession()


class TestCLISupportFlow(unittest.TestCase):
    """Parcours “Gestion → Événements” pour un rôle support."""

    # ---------------------------------------------------------------- #
    # setUp / tearDown
    # ---------------------------------------------------------------- #
    def setUp(self) -> None:
        """Prépare le CLI, un utilisateur support et les patches nécessaires."""
        # Injection de la séquence de réponses clavier
        self._orig_input = builtins.input
        answers = iter(["1", "1", "2", "0", "0"])
        builtins.input = lambda *_: next(answers)

        # Instanciation du CLI avec une base factice
        from app.views.cli_interface import CLIInterface
        self.cli = CLIInterface(_DummyDB())
        self.cli.current_user = {"id": 42, "role": "support", "role_id": 2}

        # Patch des deux actions internes
        self.p_display = patch.object(self.cli.writer_v,
                                      "_display_my_events",
                                      MagicMock())
        self.p_update = patch.object(self.cli.writer_v,
                                     "_update_my_event_cli",
                                     MagicMock())
        self.p_display.start()
        self.p_update.start()

    def tearDown(self) -> None:
        builtins.input = self._orig_input
        self.p_display.stop()
        self.p_update.stop()

    # ---------------------------------------------------------------- #
    # tests
    # ---------------------------------------------------------------- #
    def test_full_flow(self) -> None:
        """La navigation doit appeler exactement les deux actions attendues."""
        with StringIO() as buf, redirect_stdout(buf):
            self.cli._write_menu()
            output = buf.getvalue()

        # Vérifications des appels
        self.cli.writer_v._display_my_events.assert_called_once()
        self.cli.writer_v._update_my_event_cli.assert_called_once()

        # Vérification du contenu affiché
        self.assertIn("-- Gestion --", output)
        self.assertIn("-- Événements (support) --", output)


if __name__ == "__main__":
    unittest.main()
