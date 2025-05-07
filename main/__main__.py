# main/__main__.py
# ============================================================
# Point d’entrée de l’application  (python -m main)
# ============================================================
from __future__ import annotations

import os
from pathlib import Path                      # ← facultatif, laissé en place

# --- dépendances internes ---
from .init_db import init_db
from .seed_db import seed_db
from app.config.database import DatabaseConfig, DatabaseConnection
from app.views.cli_interface import CLIInterface
from app.observability.sentry import init_sentry

# ------------------------------------------------------------
# 1) Initialisation Sentry – AVANT toute exception potentielle
# ------------------------------------------------------------
init_sentry()                # active Sentry si SENTRY_DSN est présent


# ------------------------------------------------------------
# 2) Bloc de test Sentry (facultatif)
# ------------------------------------------------------------
_sentry_flag = os.getenv("SENTRY_TEST")

if _sentry_flag == "ping":                      # message simple
    import sentry_sdk
    import datetime as dt
    print("[SENTRY TEST] Envoi d’un « ping »...")
    sentry_sdk.capture_message(
        f"Sentry ping {dt.datetime.utcnow()}",
        level="error"                          # <-- visible dans Issues
    )
    sentry_sdk.flush(timeout=5.0)

elif _sentry_flag == "1":                       # exception non gérée
    import sentry_sdk
    import time
    print("[SENTRY TEST] ZeroDivisionError volontaire...")
    try:
        1 / 0
    except ZeroDivisionError:
        # on laisse Sentry faire sa capture automatique **et**
        # on la force en manuel pour être sûr.
        sentry_sdk.capture_exception()
        sentry_sdk.flush(timeout=5.0)
        # on NE relance PAS l’erreur : l’appli continue,
        # et vous verrez l’event arriver sous quelques secondes.


# ------------------------------------------------------------
# 3) Fonction principale
# ------------------------------------------------------------
def main() -> None:
    """Initialise la BD, charge les données de démo, lance le CLI."""
    print("→ Initialisation de la base de données…")
    init_db()

    print("\n→ Chargement des données d'exemple…")
    seed_db()

    print("\n→ Lancement de l'interface CLI Epic Events\n")
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    CLIInterface(conn).run()


# ------------------------------------------------------------
# 4) Exécution directe (python -m main)
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
