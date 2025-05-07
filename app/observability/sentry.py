# -*- coding: utf-8 -*-
"""
Initialisation Sentry – importé une seule fois (main/__main__.py).
Le DSN & l’environnement viennent du .env.
"""
from __future__ import annotations
import os
import sentry_sdk
from dotenv import load_dotenv

load_dotenv()                                    # charge le .env

_DSN = os.getenv("SENTRY_DSN")
_ENV = os.getenv("SENTRY_ENV", "prod")          # “prod” par défaut
_TRACES_RATE = float(os.getenv("SENTRY_TRACES", "0.0"))  # perf. désactivée


def init_sentry() -> None:
    """
    Initialise le SDK Sentry *si* un DSN est défini.
    - `send_default_pii=True` : envoie les IP / headers pour un suivi complet.
    - `traces_sample_rate`  : 0 → pas de traces de perf (modulable par var. d’env).
    """
    if not _DSN:
        return                                   # pas de DSN → Sentry OFF
    sentry_sdk.init(
        dsn=_DSN,
        environment=_ENV,
        send_default_pii=True,
        traces_sample_rate=_TRACES_RATE,
        enable_tracing=_TRACES_RATE > 0.0
    )
