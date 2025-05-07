# -*- coding: utf-8 -*-
"""
DataReader
==========

Couche « lecture » de l’application.  
Une fois authentifié, chaque collaborateur – quel que soit son rôle
(gestion / commercial / support) – peut consulter l’ensemble des
*clients*, *contrats* et *événements*.

Un filtre optionnel peut toutefois être appliqué :

* **commercial** : si le dictionnaire *current_user* contient la clé
  ``"force_filter"`` (True), seules les entités rattachées au commercial
  courant sont renvoyées ;
* **support**  : idem, mais limité aux événements assignés au
  technicien support.

Notes
-----
* Aucun décorateur n’est utilisé (pas de ``@staticmethod``).  
* Aucune trace de debug n’est émise ; les méthodes se contentent de
  renvoyer les listes demandées ou de lever une :class:`PermissionError`
  lorsqu’un utilisateur non authentifié les invoque.
"""

from __future__ import annotations

from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataReader:
    """Contrôleur de lecture (read‑only)."""

    # ------------------------------------------------------------------ #
    # Construction                                                       #
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection) -> None:
        self._db_connection = db_connection

    # ------------------------------------------------------------------ #
    # Helper interne                                                     #
    # ------------------------------------------------------------------ #
    def _ensure_authenticated(self, current_user: Dict) -> None:
        """Vérifie qu’un utilisateur est fourni et authentifié."""
        if not current_user:
            raise PermissionError("Utilisateur non authentifié.")

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def get_all_clients(self, session: Session, current_user: Dict) -> List[Client]:
        """
        Renvoie la liste des clients.

        • Tous les rôles voient l’intégralité des clients.  
        • Un commercial peut demander un filtrage forcé en ajoutant
          ``"force_filter": True`` à *current_user*.
        """
        self._ensure_authenticated(current_user)
        session.expire_all()

        if (
            current_user.get("role") == "commercial"
            and current_user.get("force_filter")
        ):
            return (
                session.query(Client)
                .filter(Client.commercial_id == current_user["id"])
                .all()
            )

        return session.query(Client).all()

    # ------------------------------------------------------------------ #
    def get_all_contracts(
        self, session: Session, current_user: Dict
    ) -> List[Contract]:
        """
        Renvoie la liste des contrats, avec la même règle de filtrage
        facultatif que :meth:`get_all_clients`.
        """
        self._ensure_authenticated(current_user)
        session.expire_all()

        if (
            current_user.get("role") == "commercial"
            and current_user.get("force_filter")
        ):
            return (
                session.query(Contract)
                .filter(Contract.commercial_id == current_user["id"])
                .all()
            )

        return session.query(Contract).all()

    # ------------------------------------------------------------------ #
    def get_all_events(self, session: Session, current_user: Dict) -> List[Event]:
        """
        Renvoie la liste des événements.

        *Commercial* : avec ``"force_filter": True``, seuls les événements
        liés aux contrats du commercial sont retournés.  
        *Support*    : avec ``"force_filter": True``, seuls les événements
        assignés au support courant sont retournés.
        """
        self._ensure_authenticated(current_user)
        session.expire_all()
        role = current_user.get("role")

        if role == "commercial" and current_user.get("force_filter"):
            return (
                session.query(Event)
                .join(Contract, Event.contract_id == Contract.id)
                .filter(Contract.commercial_id == current_user["id"])
                .all()
            )

        if role == "support" and current_user.get("force_filter"):
            return (
                session.query(Event)
                .filter(Event.support_id == current_user["id"])
                .all()
            )

        return session.query(Event).all()
