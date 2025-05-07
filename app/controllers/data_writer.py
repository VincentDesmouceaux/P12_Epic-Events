# -*- coding: utf-8 -*-
"""
DataWriter
----------

Couche *métier* « écriture » responsable de la création et de la
modification des entités *User*, *Client*, *Contract* et *Event*.

Garanties principales :

* **Validation métier** :  
  - adresses e‑mail valides ;  
  - montants positifs et *remaining ≤ total* ;  
  - cohérence des dates (*end* ≥ *start*) ;  
  - respect des règles de droits selon le rôle connecté (*gestion*,
    *commercial* ou *support*).

* **Observabilité** :  
  Des points clés (création / modification de collaborateurs, signature
  d’un contrat) sont envoyés à Sentry via :py:meth:`_capture`.  
  Aucune action n’est entreprise si le SDK n’est pas initialisé.

!!! note
    Aucun décorateur n’est présent ; toutes les méthodes sont des
    méthodes d’instance.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any, Dict, List, Optional

import sentry_sdk
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataWriter:
    """
    Fournit toutes les opérations d’écriture.  
    Chaque méthode lève une exception explicite (*ValueError*,
    *PermissionError*, …) lorsqu’une règle n’est pas respectée.
    """

    # ------------------------------------------------------------------ #
    # Construction                                                       #
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        """
        Parameters
        ----------
        db_connection :
            Objet possédant une méthode ``create_session`` retournant une
            *Session SQLAlchemy*.
        """
        self.db = db_connection

    # ------------------------------------------------------------------ #
    # Aide Sentry                                                        #
    # ------------------------------------------------------------------ #
    def _capture(self, message: str, **context: Any) -> None:
        """
        Envoie un message **info** à Sentry, enrichi du contexte passé
        en mots‑clés.  Silencieux si le SDK n’est pas initialisé.
        """
        if sentry_sdk.Hub.current.client is None:
            return

        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level="info")

    # ------------------------------------------------------------------ #
    # Vérifications d’autorisation                                       #
    # ------------------------------------------------------------------ #
    def _check_auth(self, current_user: Optional[Dict[str, Any]]) -> None:
        """Vérifie qu’un utilisateur est connecté."""
        if not current_user:
            raise PermissionError("Utilisateur non authentifié.")

    def _check_permission(
        self,
        current_user: Dict[str, Any],
        allowed_roles: List[str],
    ) -> None:
        """Valide que le rôle connecté appartient à *allowed_roles*."""
        self._check_auth(current_user)
        if current_user.get("role") not in allowed_roles:
            raise PermissionError("Rôle non autorisé pour cette action.")

    # ------------------------------------------------------------------ #
    # Helpers divers                                                     #
    # ------------------------------------------------------------------ #
    _REG_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

    def _prefix_for(self, role_id: int) -> str:
        """Retourne le préfixe *C/S/G* selon l’ID du rôle."""
        return {1: "C", 2: "S", 3: "G"}.get(role_id, "X")

    def _generate_employee_number(self, sess: Session, role_id: int) -> str:
        """Génère le prochain matricule (ex. ``C004``) pour le rôle donné."""
        prefix = self._prefix_for(role_id)
        max_num = 0
        for (emp,) in sess.query(User.employee_number).filter(
            User.role_id == role_id
        ):
            if emp and emp.startswith(prefix):
                try:
                    max_num = max(max_num, int(emp[len(prefix):]))
                except ValueError:
                    pass
        return f"{prefix}{max_num + 1:03d}"

    # ================================================================== #
    #  COLLABORATEURS                                                    #
    # ================================================================== #
    def create_user(
        self,
        sess: Session,
        cur: Dict[str, Any],
        employee_number: Optional[str],
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        role_id: int,
    ) -> User:
        """Crée un nouvel utilisateur après validation complète."""
        self._check_permission(cur, ["gestion"])

        if not self._REG_EMAIL.match(email):
            raise ValueError("Email collaborateur invalide.")
        if role_id not in (1, 2, 3):
            raise ValueError("Rôle inconnu (1=Com,2=Sup,3=Gest).")

        if not employee_number:
            employee_number = self._generate_employee_number(sess, role_id)

        user = User(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
        )
        sess.add(user)
        try:
            sess.commit()
        except IntegrityError as err:
            sess.rollback()
            raise ValueError(f"Email déjà utilisé : {err}") from err

        self._capture("user_created", user_id=user.id, created_by=cur["id"])
        return user

    def update_user(
        self,
        sess: Session,
        cur: Dict[str, Any],
        user_id: int,
        **updates,
    ) -> User:
        """Met à jour un collaborateur identifié par *user_id*."""
        self._check_permission(cur, ["gestion"])

        if "email" in updates and updates["email"]:
            if not self._REG_EMAIL.match(updates["email"]):
                raise ValueError("Email collaborateur invalide.")

        user = sess.get(User, user_id)
        if not user:
            raise ValueError("Collaborateur non trouvé.")

        for key, value in updates.items():
            setattr(user, key, value)
        sess.commit()

        self._capture(
            "user_updated",
            user_id=user.id,
            updated_by=cur["id"],
            changes=list(updates.keys()),
        )
        return user

    def update_user_by_employee_number(
        self,
        sess: Session,
        cur: Dict[str, Any],
        employee_number: str,
        **updates,
    ) -> User:
        """Équivalent d’*update_user* mais via le matricule."""
        self._check_permission(cur, ["gestion"])

        if "email" in updates and updates["email"]:
            if not self._REG_EMAIL.match(updates["email"]):
                raise ValueError("Email collaborateur invalide.")

        user = (
            sess.query(User)
            .filter_by(employee_number=employee_number)
            .first()
        )
        if not user:
            raise ValueError("Collaborateur non trouvé.")

        for key, value in updates.items():
            setattr(user, key, value)
        sess.commit()

        self._capture(
            "user_updated",
            user_id=user.id,
            updated_by=cur["id"],
            changes=list(updates.keys()),
        )
        return user

    def delete_user(
        self,
        sess: Session,
        cur: Dict[str, Any],
        employee_number: str,
    ) -> bool:
        """Supprime définitivement le collaborateur *employee_number*."""
        self._check_permission(cur, ["gestion"])

        user = (
            sess.query(User)
            .filter_by(employee_number=employee_number)
            .first()
        )
        if not user:
            raise ValueError("Collaborateur non trouvé.")

        sess.delete(user)
        sess.commit()
        return True

    # ================================================================== #
    #  CLIENTS                                                           #
    # ================================================================== #
    def create_client(
        self,
        sess: Session,
        cur: Dict[str, Any],
        full_name: str,
        email: str,
        phone: Optional[str],
        company_name: Optional[str],
        commercial_id: Optional[int],
    ) -> Client:
        """Insère un nouveau client."""
        self._check_permission(cur, ["gestion", "commercial"])

        if not self._REG_EMAIL.match(email):
            raise ValueError("Email client invalide.")

        if cur["role"] == "commercial":
            commercial_id = cur["id"]

        client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            date_created=dt.datetime.utcnow(),
            commercial_id=commercial_id,
        )
        sess.add(client)
        sess.commit()
        return client

    def update_client(
        self,
        sess: Session,
        cur: Dict[str, Any],
        client_id: int,
        **updates,
    ) -> Client:
        """Met à jour les informations d’un client."""
        self._check_permission(cur, ["gestion", "commercial"])

        if "email" in updates and updates["email"]:
            if not self._REG_EMAIL.match(updates["email"]):
                raise ValueError("Email client invalide.")

        client = sess.get(Client, client_id)
        if not client:
            raise ValueError("Client introuvable.")

        if cur["role"] == "commercial" and client.commercial_id != cur["id"]:
            raise PermissionError("Client non autorisé.")

        for key, value in updates.items():
            setattr(client, key, value)
        client.date_last_contact = dt.datetime.utcnow()
        sess.commit()
        return client

    # ================================================================== #
    #  CONTRATS                                                          #
    # ================================================================== #
    def create_contract(
        self,
        sess: Session,
        cur: Dict[str, Any],
        client_id: int,
        total_amount: float,
        remaining_amount: float,
        is_signed: bool = False,
    ) -> Contract:
        """Crée un contrat pour le client *client_id*."""
        self._check_permission(cur, ["gestion"])

        if total_amount < 0 or remaining_amount < 0:
            raise ValueError("Montants négatifs interdits.")
        if remaining_amount > total_amount:
            raise ValueError("Restant > total.")

        client = sess.get(Client, client_id)
        if not client:
            raise ValueError("Client introuvable.")

        contract = Contract(
            client_id=client.id,
            commercial_id=client.commercial_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            is_signed=is_signed,
        )
        sess.add(contract)
        sess.commit()
        return contract

    def update_contract(
        self,
        sess: Session,
        cur: Dict[str, Any],
        contract_id: int,
        **updates,
    ) -> Contract:
        """Met à jour un contrat et détecte sa signature éventuelle."""
        self._check_permission(cur, ["gestion", "commercial"])

        contract = sess.get(Contract, contract_id)
        if not contract:
            raise ValueError("Contrat introuvable.")

        if (
            cur["role"] == "commercial"
            and contract.commercial_id != cur["id"]
        ):
            raise PermissionError("Contrat non autorisé.")
        if "commercial_id" in updates and cur["role"] == "commercial":
            raise PermissionError("Ré‑affectation interdite.")

        total = updates.get("total_amount", contract.total_amount)
        remain = updates.get("remaining_amount", contract.remaining_amount)
        if total < 0 or remain < 0:
            raise ValueError("Montants négatifs interdits.")
        if remain > total:
            raise ValueError("Restant > total.")

        was_signed = contract.is_signed
        will_be_signed = updates.get("is_signed", was_signed)

        for key, value in updates.items():
            setattr(contract, key, value)

        if (not was_signed) and will_be_signed:
            self._capture(
                "contract_signed",
                contract_id=contract.id,
                client_id=contract.client_id,
                signed_by=cur["id"],
            )

        sess.commit()
        return contract

    # ================================================================== #
    #  ÉVÉNEMENTS                                                        #
    # ================================================================== #
    def create_event(
        self,
        sess: Session,
        cur: Dict[str, Any],
        contract_id: int,
        support_id: Optional[int],
        date_start: dt.datetime,
        date_end: dt.datetime,
        location: Optional[str] = None,
        attendees: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Event:
        """Crée un événement rattaché à un contrat signé."""
        self._check_permission(cur, ["gestion", "commercial"])

        contract = sess.get(Contract, contract_id)
        if not contract:
            raise ValueError("Contrat introuvable.")

        if cur["role"] == "commercial":
            if contract.commercial_id != cur["id"]:
                raise PermissionError("Contrat non autorisé.")
            if not contract.is_signed:
                raise PermissionError("Contrat non signé.")

        if date_end < date_start:
            raise ValueError("Date fin < date début.")
        if attendees is not None and attendees < 0:
            raise ValueError("Participants négatifs.")

        event = Event(
            contract_id=contract_id,
            support_id=support_id,
            date_start=date_start,
            date_end=date_end,
            location=location,
            attendees=attendees,
            notes=notes,
        )
        sess.add(event)
        sess.commit()
        return event

    def update_event(
        self,
        sess: Session,
        cur: Dict[str, Any],
        event_id: int,
        **updates,
    ) -> Event:
        """Met à jour un événement en vérifiant les droits du rôle."""
        self._check_permission(cur, ["gestion", "commercial", "support"])

        event = sess.get(Event, event_id)
        if not event:
            raise ValueError("Événement introuvable.")

        if cur["role"] == "commercial":
            contract = sess.get(Contract, event.contract_id)
            if contract.commercial_id != cur["id"]:
                raise PermissionError("Non autorisé.")

        if cur["role"] == "support" and event.support_id != cur["id"]:
            raise PermissionError("Non autorisé.")

        new_start = updates.get("date_start", event.date_start)
        new_end = updates.get("date_end", event.date_end)
        if new_start and new_end and new_end < new_start:
            raise ValueError("Date fin < date début.")

        if (
            "attendees" in updates
            and updates["attendees"] is not None
            and updates["attendees"] < 0
        ):
            raise ValueError("Participants négatifs.")

        for key, value in updates.items():
            setattr(event, key, value)
        sess.commit()
        return event
