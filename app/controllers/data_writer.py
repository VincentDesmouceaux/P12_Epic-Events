# -*- coding: utf-8 -*-
"""
DataWriter – couche « métier » (écriture) sécurisée.
- Aucun décorateur (@staticmethod) – tout est méthode d’instance.
- Signatures IDENTIQUES à la version d’origine.
- Vérifications ajoutées : e‑mail, montants positifs, restant ≤ total,
  dates « fin ≥ début », rôle/permissions inchangés.
"""
from __future__ import annotations

import datetime as dt
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataWriter:
    # ------------------------------------------------------------------ #
    #  Construction & log                                                #
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        self.db = db_connection

    def _debug(self, tag: str, **kv):
        print(f"[DataWriter][DEBUG] {tag} -> {kv}")

    # ------------------------------------------------------------------ #
    #  Permissions                                                       #
    # ------------------------------------------------------------------ #
    def _check_auth(self, cur: Optional[Dict[str, Any]]):
        self._debug("_check_auth", cur=cur)
        if not cur:
            raise PermissionError("Utilisateur non authentifié.")

    def _check_permission(self, cur: Dict[str, Any], allowed: List[str]):
        self._check_auth(cur)
        if cur.get("role") not in allowed:
            raise PermissionError("Rôle non autorisé pour cette action.")

    # ------------------------------------------------------------------ #
    #  Aides                                                             #
    # ------------------------------------------------------------------ #
    _REG_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")

    def _prefix_for(self, role_id: int) -> str:
        return {1: "C", 2: "S", 3: "G"}.get(role_id, "X")

    def _generate_employee_number(self, sess: Session, role_id: int) -> str:
        prefix = self._prefix_for(role_id)
        maxi = 0
        for (emp,) in sess.query(User.employee_number).filter(User.role_id == role_id):
            if emp and emp.startswith(prefix):
                try:
                    maxi = max(maxi, int(emp[len(prefix):]))
                except ValueError:
                    pass
        new_emp = f"{prefix}{maxi + 1:03d}"
        self._debug("_generate_employee_number", new_emp=new_emp)
        return new_emp

    # ================================================================== #
    #  ======================= COLLABORATEURS ========================== #
    # ================================================================== #
    def create_user(
            self, sess: Session, cur: Dict[str, Any],
            employee_number: Optional[str], first_name: str, last_name: str,
            email: str, password_hash: str, role_id: int) -> User:

        self._debug("create_user", email=email, role_id=role_id)
        self._check_permission(cur, ["gestion"])

        if not self._REG_EMAIL.match(email):
            raise ValueError("Email collaborateur invalide.")

        if role_id not in (1, 2, 3):
            raise ValueError("Rôle inconnu (1=Com,2=Sup,3=Gest).")

        if not employee_number:
            employee_number = self._generate_employee_number(sess, role_id)

        user = User(employee_number=employee_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password_hash=password_hash,
                    role_id=role_id)
        sess.add(user)
        try:
            sess.commit()
        except IntegrityError as err:
            sess.rollback()
            raise ValueError(f"Email déjà utilisé : {err}") from err

        return user

    def update_user(self, sess: Session, cur: Dict[str, Any],
                    user_id: int, **updates):

        self._debug("update_user", user_id=user_id, updates=updates)
        self._check_permission(cur, ["gestion"])

        if "email" in updates and updates["email"]:
            if not self._REG_EMAIL.match(updates["email"]):
                raise ValueError("Email collaborateur invalide.")

        usr = sess.get(User, user_id)
        if not usr:
            raise ValueError("Collaborateur non trouvé.")

        for k, v in updates.items():
            setattr(usr, k, v)
        sess.commit()
        return usr

    def update_user_by_employee_number(self, sess: Session, cur: Dict[str, Any],
                                       employee_number: str, **updates):

        self._debug("update_user_by_emp", emp=employee_number, updates=updates)
        self._check_permission(cur, ["gestion"])

        if "email" in updates and updates["email"]:
            if not self._REG_EMAIL.match(updates["email"]):
                raise ValueError("Email collaborateur invalide.")

        usr = sess.query(User).filter_by(
            employee_number=employee_number).first()
        if not usr:
            raise ValueError("Collaborateur non trouvé.")

        for k, v in updates.items():
            setattr(usr, k, v)
        sess.commit()
        return usr

    def delete_user(self, sess: Session, cur: Dict[str, Any], employee_number: str):
        self._debug("delete_user", emp=employee_number)
        self._check_permission(cur, ["gestion"])

        usr = sess.query(User).filter_by(
            employee_number=employee_number).first()
        if not usr:
            raise ValueError("Collaborateur non trouvé.")
        sess.delete(usr)
        sess.commit()
        return True

    # ================================================================== #
    #  ============================ CLIENTS ============================ #
    # ================================================================== #
    def create_client(self, sess: Session, cur: Dict[str, Any],
                      full_name: str, email: str, phone: Optional[str],
                      company_name: Optional[str], commercial_id: Optional[int]):

        self._debug("create_client", email=email)
        self._check_permission(cur, ["gestion", "commercial"])

        if not self._REG_EMAIL.match(email):
            raise ValueError("Email client invalide.")

        if cur["role"] == "commercial":
            commercial_id = cur["id"]

        cli = Client(full_name=full_name, email=email, phone=phone,
                     company_name=company_name,
                     date_created=dt.datetime.utcnow(),
                     commercial_id=commercial_id)
        sess.add(cli)
        sess.commit()
        return cli

    def update_client(self, sess: Session, cur: Dict[str, Any],
                      client_id: int, **updates):

        self._debug("update_client", id=client_id, updates=updates)
        self._check_permission(cur, ["gestion", "commercial"])

        if "email" in updates and updates["email"]:
            if not self._REG_EMAIL.match(updates["email"]):
                raise ValueError("Email client invalide.")

        cli = sess.get(Client, client_id)
        if not cli:
            raise ValueError("Client introuvable.")

        if cur["role"] == "commercial" and cli.commercial_id != cur["id"]:
            raise PermissionError("Client non autorisé.")

        for k, v in updates.items():
            setattr(cli, k, v)
        cli.date_last_contact = dt.datetime.utcnow()
        sess.commit()
        return cli

    # ================================================================== #
    #  ============================ CONTRATS =========================== #
    # ================================================================== #
    def create_contract(self, sess: Session, cur: Dict[str, Any],
                        client_id: int, total_amount: float,
                        remaining_amount: float, is_signed: bool = False):

        self._debug("create_contract", client=client_id)
        self._check_permission(cur, ["gestion"])

        if total_amount < 0 or remaining_amount < 0:
            raise ValueError("Montants négatifs interdits.")
        if remaining_amount > total_amount:
            raise ValueError("Restant > total.")

        cli = sess.get(Client, client_id)
        if not cli:
            raise ValueError("Client introuvable.")

        ctr = Contract(client_id=cli.id,
                       commercial_id=cli.commercial_id,
                       total_amount=total_amount,
                       remaining_amount=remaining_amount,
                       is_signed=is_signed)
        sess.add(ctr)
        sess.commit()
        return ctr

    def update_contract(self, sess: Session, cur: Dict[str, Any],
                        contract_id: int, **updates):

        self._debug("update_contract", id=contract_id, updates=updates)
        self._check_permission(cur, ["gestion", "commercial"])

        ctr = sess.get(Contract, contract_id)
        if not ctr:
            raise ValueError("Contrat introuvable.")

        if cur["role"] == "commercial" and ctr.commercial_id != cur["id"]:
            raise PermissionError("Contrat non autorisé.")

        if "commercial_id" in updates and cur["role"] == "commercial":
            raise PermissionError("Ré‑affectation interdite.")

        # cohérence des montants
        total = updates.get("total_amount", ctr.total_amount)
        remain = updates.get("remaining_amount", ctr.remaining_amount)
        if total < 0 or remain < 0:
            raise ValueError("Montants négatifs interdits.")
        if remain > total:
            raise ValueError("Restant > total.")

        for k, v in updates.items():
            setattr(ctr, k, v)
        sess.commit()
        return ctr

    # ================================================================== #
    #  =========================== ÉVÉNEMENTS ========================== #
    # ================================================================== #
    def create_event(self, sess: Session, cur: Dict[str, Any],
                     contract_id: int, support_id: Optional[int],
                     date_start: dt.datetime, date_end: dt.datetime,
                     location: Optional[str] = None,
                     attendees: Optional[int] = None,
                     notes: Optional[str] = None):

        self._debug("create_event", ctr=contract_id)
        self._check_permission(cur, ["gestion", "commercial"])

        ctr = sess.get(Contract, contract_id)
        if not ctr:
            raise ValueError("Contrat introuvable.")
        if cur["role"] == "commercial":
            if ctr.commercial_id != cur["id"]:
                raise PermissionError("Contrat non autorisé.")
            if not ctr.is_signed:
                raise PermissionError("Contrat non signé.")
        if date_end < date_start:
            raise ValueError("Date fin < date début.")
        if attendees is not None and attendees < 0:
            raise ValueError("Participants négatifs.")

        evt = Event(contract_id=contract_id, support_id=support_id,
                    date_start=date_start, date_end=date_end,
                    location=location, attendees=attendees, notes=notes)
        sess.add(evt)
        sess.commit()
        return evt

    def update_event(self, sess: Session, cur: Dict[str, Any],
                     event_id: int, **updates):

        self._debug("update_event", id=event_id, updates=updates)
        self._check_permission(cur, ["gestion", "commercial", "support"])

        evt = sess.get(Event, event_id)
        if not evt:
            raise ValueError("Événement introuvable.")

        if cur["role"] == "commercial":
            ctr = sess.get(Contract, evt.contract_id)
            if ctr.commercial_id != cur["id"]:
                raise PermissionError("Non autorisé.")
        if cur["role"] == "support" and evt.support_id != cur["id"]:
            raise PermissionError("Non autorisé.")

        new_start = updates.get("date_start", evt.date_start)
        new_end = updates.get("date_end", evt.date_end)
        if new_start and new_end and new_end < new_start:
            raise ValueError("Date fin < date début.")
        if "attendees" in updates and updates["attendees"] is not None:
            if updates["attendees"] < 0:
                raise ValueError("Participants négatifs.")

        for k, v in updates.items():
            setattr(evt, k, v)
        sess.commit()
        return evt
