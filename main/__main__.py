# -*- coding: utf-8 -*-
"""
Point d’entrée de l’application : ``python -m main``

Enchaîne, dans l’ordre :
1. Initialisation de Sentry (si un DSN est présent dans le `.env`).
2. Éventuels tests Sentry déclenchés par la variable d’environnement
   ``SENTRY_TEST`` :
   * ``ping``  → envoi d’un simple message au niveau *error* ;
   * ``1``    → capture d’une `ZeroDivisionError`.
3. Création du schéma SQL et population de données de démonstration.
4. Lancement de l’interface CLI.
"""

from __future__ import annotations

import os
from pathlib import Path  # conservé pour montrer que l’import fonctionne

# --- dépendances internes ------------------------------------------------- #
from .init_db import init_db
from .seed_db import seed_db
from app.config.database import DatabaseConfig, DatabaseConnection
from app.views.cli_interface import CLIInterface
from app.observability.sentry import init_sentry

# ------------------------------------------------------------------------- #
# 1) Activation de Sentry très tôt dans le cycle de vie du processus
# ------------------------------------------------------------------------- #
init_sentry()

# ------------------------------------------------------------------------- #
# 2) Bloc de test Sentry (facultatif – contrôlé par la variable SENTRY_TEST)
# ------------------------------------------------------------------------- #
_sentry_flag = os.getenv("SENTRY_TEST")

if _sentry_flag == "ping":
    import sentry_sdk
    from datetime import datetime as _dt

    print("[SENTRY TEST] Envoi d’un « ping » vers Sentry…")
    sentry_sdk.capture_message(
        f"Sentry ping {_dt.utcnow()}",
        level="error",            # visible dans l’onglet « Issues »
    )
    sentry_sdk.flush(timeout=5.0)

elif _sentry_flag == "1":
    import sentry_sdk

    print("[SENTRY TEST] Génération d’une ZeroDivisionError…")
    try:
        _ = 1 / 0  # division volontaire
    except ZeroDivisionError:
        # on capture manuellement pour garantir l’envoi
        sentry_sdk.capture_exception()
        sentry_sdk.flush(timeout=5.0)
        # on ne relance pas l’exception : l’application peut poursuivre


# ------------------------------------------------------------------------- #
# 3) Fonction principale                                                    #
# ------------------------------------------------------------------------- #
def main() -> None:
    """
    Crée (ou recrée) les tables, charge un jeu de données de démonstration
    puis lance l’interface CLI Epic Events.
    """
    print("→ Initialisation de la base de données…")
    init_db()

    print("\n→ Chargement des données d'exemple…")
    seed_db()

    print("\n→ Lancement de l'interface CLI Epic Events\n")
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    CLIInterface(conn).run()


# ------------------------------------------------------------------------- #
# 4) Exécution directe                                                     #
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
