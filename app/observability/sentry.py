# app/observability/sentry.py
# -*- coding: utf-8 -*-
"""
Observabilité : initialisation de Sentry
=======================================

Ce module est importé **une seule fois** – idéalement dès le démarrage
de l’application (cf. *main/__main__.py*) – afin d’initialiser le SDK
*Sentry* avec les paramètres définis dans le fichier `.env`.

Variables d’environnement reconnues
-----------------------------------

``SENTRY_DSN``               clé de projet fournie par Sentry (obligatoire)  
``SENTRY_ENV``               environnement logique ; *prod* par défaut  
``SENTRY_TRACES``            taux d’échantillonnage pour l’APM (*0.0 → off*)  

Toutes les autres options conservent leurs valeurs par défaut.

Exemple de contenu minimal du *.env* ::

    # Sentry
    SENTRY_DSN=https://…@…ingest.sentry.io/123456
    SENTRY_ENV=prod
    SENTRY_TRACES=0.25        # 25 % des transactions tracées
"""
from __future__ import annotations

import os

from dotenv import load_dotenv
import sentry_sdk

# ---------------------------------------------------------------------------#
# Chargement du fichier .env (s’il existe)                                    #
# ---------------------------------------------------------------------------#
load_dotenv()  # Aucune erreur si le fichier est absent

# ---------------------------------------------------------------------------#
# Lecture des variables d’environnement                                       #
# ---------------------------------------------------------------------------#
_DSN: str | None = os.getenv("SENTRY_DSN")
_ENV: str = os.getenv("SENTRY_ENV", "prod")
_TRACES_RATE: float = float(
    os.getenv("SENTRY_TRACES", "0.0"))  # 0.0 ➜ désactivé


def init_sentry() -> None:
    """
    Démarre le SDK **Sentry** si – et seulement si – un DSN est présent.

    La fonction est *idempotente* : appeler plusieurs fois ``init_sentry()``
    n’a aucun effet secondaire.
    """
    if not _DSN:
        # Aucune configuration trouvée : on ne fait rien, l’application
        # continue simplement sans remontée vers Sentry.
        return

    # Initialisation « basique » : seules les options réellement utiles dans
    # le cadre du projet sont renseignées ; le reste suit la configuration
    # par défaut du SDK.
    sentry_sdk.init(
        dsn=_DSN,
        environment=_ENV,
        send_default_pii=True,          # envoie IP, User‑Agent, etc.
        traces_sample_rate=_TRACES_RATE,
        enable_tracing=_TRACES_RATE > 0.0,
    )
