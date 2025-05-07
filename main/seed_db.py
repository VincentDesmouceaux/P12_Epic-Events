# -*- coding: utf-8 -*-
"""
Jeu de données de démonstration.

Insère :

* 3 rôles : « commercial », « support », « gestion »
* 5 utilisateurs (3 commerciaux, 1 support, 1 gestion)
* 3 clients (un par commercial)
* 7 contrats (signés ou non, payés ou non)
* 1 événement « avec support » et 1 « sans support » pour chaque contrat
"""

from __future__ import annotations

import datetime as dt
from typing import Dict, Tuple

from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Role, User, Client, Contract, Event
from app.authentification.auth_controller import AuthController


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _get_or_create(session, model, defaults: Dict | None = None, **search):
    """
    Récupère l’instance *model* correspondant au filtre ``**search`` ;
    la crée avec ``defaults | search`` si elle n’existe pas.

    Retourne un tuple ``(instance, created_bool)``.
    """
    instance = session.query(model).filter_by(**search).first()
    if instance:
        return instance, False

    params = {**(defaults or {}), **search}
    instance = model(**params)
    session.add(instance)
    session.commit()
    return instance, True


def _create_contract(session, client: Client,
                     total: float, remaining: float, signed: bool) -> Contract:
    """
    Ajoute un contrat pour *client* puis le persiste.
    """
    contract = Contract(
        client_id=client.id,
        commercial_id=client.commercial_id,
        total_amount=total,
        remaining_amount=remaining,
        is_signed=signed,
    )
    session.add(contract)
    session.commit()
    print(f"Contrat #{contract.id} créé pour client {client.full_name}")
    return contract


# --------------------------------------------------------------------------- #
# Fonction principale                                                         #
# --------------------------------------------------------------------------- #
def seed_db() -> None:
    """
    Alimente la base avec un jeu de données cohérent destiné aux tests
    et aux démonstrations.
    """
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    session = conn.create_session()
    auth = AuthController()

    # ------------------------- 1. Rôles ----------------------------------- #
    role_defs = {
        "commercial": "Département commercial",
        "support": "Département support",
        "gestion": "Département gestion",
    }
    roles: Dict[str, Role] = {}
    for name, desc in role_defs.items():
        roles[name], created = _get_or_create(
            session, Role, {"description": desc}, name=name
        )
        if created:
            print(f"Rôle « {name} » inséré (ID={roles[name].id})")

    # ---------------------- 2. Utilisateurs ------------------------------ #
    user_defs: Tuple[Tuple[str, str, str, str, str, str], ...] = (
        ("G001", "Alice", "Gestion", "alice.gestion@example.com",
         "SuperSecretGestion", "gestion"),
        ("C001", "Bob", "Commercial", "bob.commercial@example.com",
         "SuperSecretCommercial", "commercial"),
        ("S001", "Charlie", "Support", "charlie.support@example.com",
         "SuperSecretSupport", "support"),
        ("C002", "Diane", "Commercial", "diane.sales@example.com",
         "SuperSecretDiane", "commercial"),
        ("C003", "Ethan", "Commercial", "ethan.seller@example.com",
         "SuperSecretEthan", "commercial"),
    )

    users: Dict[str, User] = {}
    for emp, fn, ln, mail, pwd, role_name in user_defs:
        user, created = _get_or_create(
            session,
            User,
            {
                "employee_number": emp,
                "first_name": fn,
                "last_name": ln,
                "password_hash": auth.hasher.hash(pwd),
                "role_id": roles[role_name].id,
            },
            email=mail,
        )
        if created:
            print(f"Utilisateur « {mail} » inséré (ID={user.id})")
        users[emp] = user

    # ------------------------- 3. Clients -------------------------------- #
    client_defs = (
        ("Kevin Casey", "kevin@startup.io", "C001"),
        ("Laura Martin", "laura.martin@techcorp.io", "C002"),
        ("Michael Johnson", "michael.johnson@enterprise.com", "C003"),
    )
    clients: Dict[int, Client] = {}
    for full_name, mail, emp_com in client_defs:
        commercial = users[emp_com]
        client, created = _get_or_create(
            session,
            Client,
            {
                "full_name": full_name,
                "phone": "0000000000",
                "company_name": "DemoCorp",
                "commercial_id": commercial.id,
            },
            email=mail,
        )
        if created:
            print(f"Client « {full_name} » inséré (ID={client.id})")
        clients[client.id] = client

    # ------------------------- 4. Contrats ------------------------------- #
    contracts: list[Contract] = []

    # 4‑A : 1 contrat principal non signé / client
    for cl in clients.values():
        contracts.append(_create_contract(
            session, cl, 20_000.0, 10_000.0, False))

    # 4‑B : 2 contrats supplémentaires non signés
    for i in range(2):
        cl = list(clients.values())[i % len(clients)]
        contracts.append(_create_contract(
            session, cl, 15_000.0, 15_000.0, False))

    # 4‑C : 2 contrats partiellement payés (signés)
    for i in range(2):
        cl = list(clients.values())[-(i + 1)]
        contracts.append(_create_contract(
            session, cl, 30_000.0, 5_000.0, True))

    # ------------------------- 5. Événements ----------------------------- #
    support_user = users["S001"]
    for ctr in contracts:
        # avec support
        _get_or_create(
            session,
            Event,
            {
                "support_id": support_user.id,
                "date_start": dt.datetime(2023, 7, 1, 10, 0),
                "date_end": dt.datetime(2023, 7, 1, 18, 0),
                "location": "123 Event St.",
                "attendees": 150,
                "notes": "Événement exemple",
            },
            contract_id=ctr.id,
            support_id=support_user.id,
        )
        # sans support
        _get_or_create(
            session,
            Event,
            {
                "support_id": None,
                "date_start": dt.datetime(2023, 8, 1, 10, 0),
                "date_end": dt.datetime(2023, 8, 1, 18, 0),
                "location": "No‑support venue",
                "attendees": 80,
                "notes": "Demo event without support",
            },
            contract_id=ctr.id,
            support_id=None,
        )

    session.close()
    print("Seed terminé ✅")


# --------------------------------------------------------------------------- #
# Lancement direct                                                            #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    seed_db()
