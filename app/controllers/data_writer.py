"""
DataWriter – Couche « métier » pour toutes les opérations d’écriture.

Rappels de permission
---------------------
gestion    : accès total (CRUD sur tous les objets)
commercial : créer / modifier SES clients, modifier SES contrats,
             pas de création de contrat, pas de ré-affectation à d’autres commerciaux
support    : mise à jour des événements qui lui sont assignés
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


# --------------------------------------------------------------------------- #
#  DataWriter                                                                 #
# --------------------------------------------------------------------------- #
class DataWriter:
    def __init__(self, db_connection):
        self.db = db_connection

    # -------------------------- helpers debug -------------------------- #
    @staticmethod
    def _debug(label: str, **kv):
        print(f"[DataWriter][DEBUG] {label} -> {kv}")

    # ------------------- authentification / rôles --------------------- #
    def _check_auth(self, current_user: Optional[Dict[str, Any]]):
        self._debug("_check_auth", current_user=current_user)
        if not current_user:
            raise PermissionError("Utilisateur non authentifié.")

    # ------------------------------------------------------------------ #
    def _check_permission(self, current_user: Dict[str, Any],
                          allowed_roles: list[str]):
        self._check_auth(current_user)
        self._debug("_check_permission",
                    user_role=current_user.get("role"),
                    allowed=allowed_roles)
        if current_user.get("role") not in allowed_roles:
            raise PermissionError("Accès refusé pour ce rôle.")

    # ------------------------------------------------------------------ #
    @staticmethod
    def _prefix_for(role_id: int) -> str:
        return {1: "C", 2: "S", 3: "G"}.get(role_id, "X")

    def _generate_employee_number(self, session: Session, role_id: int) -> str:
        prefix = self._prefix_for(role_id)
        max_index = 0
        for (emp,) in session.query(User.employee_number)\
                             .filter(User.role_id == role_id):
            if emp and emp.startswith(prefix):
                try:
                    num = int(emp[len(prefix):])
                    max_index = max(max_index, num)
                except ValueError:
                    continue
        new_emp = f"{prefix}{max_index + 1:03d}"
        self._debug("_generate_employee_number", role_id=role_id,
                    new_employee_number=new_emp)
        return new_emp

    # ================================================================== #
    #  =======================   COLLABORATEURS   ====================== #
    # ================================================================== #
    def create_user(self, session: Session, current_user: Dict[str, Any],
                    employee_number: Optional[str], first_name: str,
                    last_name: str, email: str, password_hash: str,
                    role_id: int) -> User:
        self._debug("create_user appelé", current_user=current_user,
                    employee_number=employee_number, email=email, role_id=role_id)
        self._check_permission(current_user, ["gestion"])

        if not employee_number:
            employee_number = self._generate_employee_number(session, role_id)

        user = User(employee_number=employee_number,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password_hash=password_hash,
                    role_id=role_id)
        session.add(user)
        try:
            session.commit()
        except IntegrityError as err:
            session.rollback()
            self._debug("create_user IntegrityError", err=str(err))
            existing = session.query(User).filter_by(email=email).first()
            if existing:
                return existing
            raise

        self._debug("Utilisateur créé", id=user.id,
                    employee_number=user.employee_number)
        return user

    # ------------------------------------------------------------------ #
    def update_user(self, session: Session, current_user: Dict[str, Any],
                    user_id: int, **updates) -> User:
        self._debug("update_user appelé", current_user=current_user,
                    user_id=user_id, updates=updates)
        self._check_permission(current_user, ["gestion"])

        user = session.get(User, user_id)
        if not user:
            raise ValueError("Collaborateur non trouvé.")

        for k, v in updates.items():
            setattr(user, k, v)
        session.commit()
        self._debug("Collaborateur mis à jour", id=user.id, updates=updates)
        return user

    # ------------------------------------------------------------------ #
    def update_user_by_employee_number(self, session: Session,
                                       current_user: Dict[str, Any],
                                       employee_number: str,
                                       **updates) -> User:
        self._debug("update_user_by_employee_number appelé",
                    employee_number=employee_number, updates=updates)
        self._check_permission(current_user, ["gestion"])

        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise ValueError("Collaborateur non trouvé.")

        for k, v in updates.items():
            setattr(user, k, v)
        session.commit()
        self._debug("Collaborateur mis à jour", id=user.id, updates=updates)
        return user

    # ------------------------------------------------------------------ #
    def delete_user(self, session: Session, current_user: Dict[str, Any],
                    employee_number: str) -> bool:
        self._debug("delete_user appelé", employee_number=employee_number)
        self._check_permission(current_user, ["gestion"])

        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise ValueError("Collaborateur non trouvé.")
        session.delete(user)
        session.commit()
        self._debug("Collaborateur supprimé", employee_number=employee_number)
        return True

    # ================================================================== #
    #  ==========================   CLIENTS   ========================== #
    # ================================================================== #
    def create_client(self, session: Session, current_user: Dict[str, Any],
                      full_name: str, email: str,
                      phone: Optional[str], company_name: Optional[str],
                      commercial_id: Optional[int]) -> Client:
        self._debug("create_client appelé", current_user=current_user,
                    full_name=full_name, commercial_id_param=commercial_id)
        self._check_permission(current_user, ["gestion", "commercial"])

        # Un commercial affecte automatiquement le client à lui-même
        if current_user["role"] == "commercial":
            commercial_id = current_user["id"]

        client = Client(full_name=full_name,
                        email=email,
                        phone=phone,
                        company_name=company_name,
                        date_created=dt.datetime.utcnow(),
                        commercial_id=commercial_id)
        session.add(client)
        session.commit()
        self._debug("Client créé", id=client.id,
                    commercial_id=client.commercial_id)
        return client

    # ------------------------------------------------------------------ #
    def update_client(self, session: Session, current_user: Dict[str, Any],
                      client_id: int, **updates) -> Client:
        self._debug("update_client appelé", current_user=current_user,
                    client_id=client_id, updates=updates)
        self._check_permission(current_user, ["gestion", "commercial"])

        client = session.get(Client, client_id)
        if not client:
            raise ValueError("Client non trouvé.")

        # Propriété : un commercial ne modifie QUE ses clients
        if (current_user["role"] == "commercial"
                and client.commercial_id != current_user["id"]):
            raise PermissionError("Vous n’êtes pas responsable de ce client.")

        for k, v in updates.items():
            setattr(client, k, v)
        client.date_last_contact = dt.datetime.utcnow()
        session.commit()
        self._debug("Client mis à jour", id=client.id, updates=updates)
        return client

    # ================================================================== #
    #  =========================   CONTRATS   ========================= #
    # ================================================================== #
    def create_contract(self, session: Session, current_user: Dict[str, Any],
                        client_id: int, total_amount: float,
                        remaining_amount: float, is_signed: bool = False) -> Contract:
        """Seul « gestion » a le droit de créer de nouveaux contrats."""
        self._debug("create_contract appelé", current_user=current_user,
                    client_id=client_id)
        self._check_permission(current_user, ["gestion"])

        client = session.get(Client, client_id)
        if not client:
            raise ValueError("Client introuvable.")

        contract = Contract(client_id=client.id,
                            commercial_id=client.commercial_id,
                            total_amount=total_amount,
                            remaining_amount=remaining_amount,
                            is_signed=is_signed)
        session.add(contract)
        session.commit()
        self._debug("Contrat créé", id=contract.id)
        return contract

    # ------------------------------------------------------------------ #
    def update_contract(self, session: Session, current_user: Dict[str, Any],
                        contract_id: int, **updates) -> Contract:
        self._debug("update_contract appelé", current_user=current_user,
                    contract_id=contract_id, updates=updates)
        self._check_permission(current_user, ["gestion", "commercial"])

        contract = session.get(Contract, contract_id)
        if not contract:
            raise ValueError("Contrat non trouvé.")

        # restriction « propriété » pour un commercial
        if (current_user["role"] == "commercial"
                and contract.commercial_id != current_user["id"]):
            raise PermissionError("Vous n’êtes pas responsable de ce contrat.")

        # un commercial ne peut pas changer l’affectation à un autre commercial
        if "commercial_id" in updates and current_user["role"] == "commercial":
            raise PermissionError(
                "Ré-affectation interdite pour un commercial.")

        for k, v in updates.items():
            setattr(contract, k, v)
        session.commit()
        self._debug("Contrat mis à jour", id=contract.id, updates=updates)
        return contract

    # ================================================================== #
    #  =========================   EVENEMENTS   ======================== #
    # ================================================================== #
    def create_event(self, session: Session, current_user: Dict[str, Any],
                     contract_id: int, support_id: Optional[int],
                     date_start: Optional[dt.datetime] = None,
                     date_end: Optional[dt.datetime] = None,
                     location: Optional[str] = None,
                     attendees: Optional[int] = None,
                     notes: Optional[str] = None) -> Event:
        """
        Un commercial crée un événement **uniquement** sur un contrat signé
        dont il est le propriétaire.
        Un support ne peut pas créer d’événement.
        """
        self._debug("create_event appelé", current_user=current_user,
                    contract_id=contract_id, support_id=support_id)
        self._check_permission(current_user, ["gestion", "commercial"])

        contract = session.get(Contract, contract_id)
        if not contract:
            raise ValueError("Contrat introuvable.")

        if current_user["role"] == "commercial":
            if contract.commercial_id != current_user["id"]:
                raise PermissionError("Contrat non autorisé.")
            if not contract.is_signed:
                raise PermissionError("Contrat non signé.")

        event = Event(contract_id=contract_id,
                      support_id=support_id,
                      date_start=date_start,
                      date_end=date_end,
                      location=location,
                      attendees=attendees,
                      notes=notes)
        session.add(event)
        session.commit()
        self._debug("Événement créé", id=event.id)
        return event

    # ------------------------------------------------------------------ #
    def update_event(self, session: Session, current_user: Dict[str, Any],
                     event_id: int, **updates) -> Event:
        self._debug("update_event appelé", current_user=current_user,
                    event_id=event_id, updates=updates)
        self._check_permission(
            current_user, ["gestion", "commercial", "support"])

        event = session.get(Event, event_id)
        if not event:
            raise ValueError("Événement non trouvé.")

        if current_user["role"] == "commercial":
            ctr = session.get(Contract, event.contract_id)
            if ctr.commercial_id != current_user["id"]:
                raise PermissionError("Événement non autorisé.")
        if current_user["role"] == "support" and event.support_id != current_user["id"]:
            raise PermissionError("Événement non autorisé.")

        for k, v in updates.items():
            setattr(event, k, v)
        session.commit()
        self._debug("Événement mis à jour", id=event.id, updates=updates)
        return event
