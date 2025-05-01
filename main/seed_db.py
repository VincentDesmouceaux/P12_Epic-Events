"""
Seed-script : remplit la base avec un jeu de données de démonstration.

Contenu inséré :
  • 3 rôles (commercial / support / gestion)
  • 3 commerciaux (C001-C003) + 1 support + 1 gestion
  • 1 client + 1 contrat pour chacun des 3 commerciaux
  • 2 contrats NON signés supplémentaires
  • 2 contrats NON totalement payés supplémentaires
  • Pour chaque contrat : 1 événement avec support + 1 sans support
"""

import datetime as dt
from typing import Dict

from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Role, User, Client, Contract, Event
from app.authentification.auth_controller import AuthController


# ------------------------------------------------------------------ #
#  OUTIL GÉNÉRIQUE : récupère l’objet ou le crée                     #
# ------------------------------------------------------------------ #
def _get_or_create(session, model, defaults: Dict = None, **search):
    """
    Renvoie (instance, créé_bool).  
    - si l’objet existe (filtre **search) → pas de création, créé_bool=False  
    - sinon, insère avec **defaults ∪ **search
    """
    instance = session.query(model).filter_by(**search).first()
    if instance:
        return instance, False

    params = {**(defaults or {}), **search}
    instance = model(**params)
    session.add(instance)
    session.commit()
    return instance, True


# ------------------------------------------------------------------ #
#  FONCTION PRINCIPALE                                               #
# ------------------------------------------------------------------ #
def seed_db() -> None:
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    session = conn.create_session()
    auth = AuthController()

    # ------------------------- 1. RÔLES ---------------------------- #
    role_defs = {
        "commercial": "Département commercial",
        "support":    "Département support",
        "gestion":    "Département gestion",
    }
    roles: Dict[str, Role] = {}
    for name, desc in role_defs.items():
        roles[name], created = _get_or_create(
            session, Role, {"description": desc}, name=name
        )
        if created:
            print(f"Role «{name}» inséré (ID={roles[name].id})")

    # ---------------------- 2. UTILISATEURS ------------------------ #
    user_defs = [
        # emp   first   last        mail                          pwd             rôle
        ("G001", "Alice",   "Gestion",  "alice.gestion@example.com",
         "SuperSecretGestion",   "gestion"),
        ("C001", "Bob",     "Commercial", "bob.commercial@example.com",
         "SuperSecretCommercial", "commercial"),
        ("S001", "Charlie", "Support",   "charlie.support@example.com",
         "SuperSecretSupport",    "support"),
        # --- commerciaux supplémentaires ---
        ("C002", "Diane",   "Commercial",     "diane.sales@example.com",
         "SuperSecretDiane",      "commercial"),
        ("C003", "Ethan",   "Commercial",    "ethan.seller@example.com",
         "SuperSecretEthan",      "commercial"),
    ]
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
            print(f"Utilisateur «{mail}» inséré (ID={user.id})")
        users[emp] = user        # on indexe par employee_number

    # ------------------------- 3. CLIENTS -------------------------- #
    client_defs = [
        # full name          email                             commercial_emp
        ("Kevin Casey",      "kevin@startup.io",               "C001"),
        ("Laura Martin",     "laura.martin@techcorp.io",       "C002"),
        ("Michael Johnson",  "michael.johnson@enterprise.com", "C003"),
    ]
    clients: Dict[int, Client] = {}
    for full_name, mail, emp_com in client_defs:
        commercial = users[emp_com]
        client, created = _get_or_create(
            session,
            Client,
            {
                "full_name":     full_name,         # <-- indispensable !
                "phone":         "0000000000",
                "company_name":  "DemoCorp",
                "commercial_id": commercial.id,
            },
            email=mail,
        )
        # si le client existait déjà, on met tout de même à jour son nom
        if not created and client.full_name != full_name:
            client.full_name = full_name
            session.commit()

        if created:
            print(f"Client «{full_name}» inséré (ID={client.id})")

        clients[client.id] = client

    # ------------------------ 4. CONTRATS -------------------------- #
    def _create_contract(client: Client, total: float,
                         remaining: float, signed: bool):
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

    contracts = []
    # 4-A : un contrat principal (non signé & partiellement payé) par client
    for cl in clients.values():
        contracts.append(_create_contract(
            cl, 20_000.0, 10_000.0, signed=False))

    # 4-B : 2 contrats supplémentaires non signés
    for i in range(2):
        cl = list(clients.values())[i % len(clients)]
        contracts.append(_create_contract(
            cl, 15_000.0, 15_000.0, signed=False))

    # 4-C : 2 contrats supplémentaires non totalement payés (signed=True)
    for i in range(2):
        cl = list(clients.values())[-(i + 1)]
        contracts.append(_create_contract(cl, 30_000.0, 5_000.0, signed=True))

    # ----------------------- 5. ÉVÉNEMENTS ------------------------- #
    support_user = users["S001"]
    for ctr in contracts:
        # – avec support –
        _get_or_create(
            session,
            Event,
            {
                "support_id": support_user.id,
                "date_start": dt.datetime(2023, 7, 1, 10, 0),
                "date_end":   dt.datetime(2023, 7, 1, 18, 0),
                "location":   "123 Event St.",
                "attendees":  150,
                "notes":      "Événement exemple",
            },
            contract_id=ctr.id,
            support_id=support_user.id,
        )
        # – sans support –
        _get_or_create(
            session,
            Event,
            {
                "support_id": None,
                "date_start": dt.datetime(2023, 8, 1, 10, 0),
                "date_end":   dt.datetime(2023, 8, 1, 18, 0),
                "location":   "No-support venue",
                "attendees":  80,
                "notes":      "Demo event without support",
            },
            contract_id=ctr.id,
            support_id=None,
        )

    session.close()
    print("Seed terminé ✅")


if __name__ == "__main__":
    seed_db()
