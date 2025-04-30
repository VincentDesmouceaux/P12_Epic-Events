# main/seed_db.py

import datetime
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.authentification.auth_controller import AuthController


def seed_db():
    """
    Insère des jeux de données d'exemple sans supprimer la base.
    - Rôles : commercial, support, gestion
    - Utilisateurs pour chaque rôle (avec mot de passe haché)
    - Quelques clients, contrats et événements
    """
    config = DatabaseConfig()
    connection = DatabaseConnection(config)
    session = connection.create_session()

    auth = AuthController()

    # 1) Rôles
    roles = {}
    for name, desc in [
        ("commercial", "Département commercial"),
        ("support", "Département support"),
        ("gestion", "Département gestion")
    ]:
        r = session.query(Role).filter_by(name=name).first()
        if not r:
            r = Role(name=name, description=desc)
            session.add(r)
            session.commit()
            print(f"Role '{name}' inséré (ID={r.id})")
        else:
            print(f"Role '{name}' existe (ID={r.id})")
        roles[name] = r

    # 2) Utilisateurs
    users_def = [
        ("G001", "Alice", "Gestion", "alice.gestion@example.com",
         "SuperSecretGestion", "gestion"),
        ("C001", "Bob", "Commercial", "bob.commercial@example.com",
         "SuperSecretCommercial", "commercial"),
        ("S001", "Charlie", "Support", "charlie.support@example.com",
         "SuperSecretSupport", "support"),
    ]
    users = {}
    for emp, fn, ln, mail, pwd, role in users_def:
        u = session.query(User).filter_by(email=mail).first()
        if not u:
            pwd_hash = auth.hasher.hash(pwd)
            u = User(
                employee_number=emp,
                first_name=fn,
                last_name=ln,
                email=mail,
                password_hash=pwd_hash,
                role_id=roles[role].id
            )
            session.add(u)
            session.commit()
            print(f"Utilisateur '{mail}' inséré (ID={u.id})")
        else:
            print(f"Utilisateur '{mail}' existe (ID={u.id})")
        users[role] = u

    # 3) Clients
    clients_def = [
        ("Kevin Casey", "kevin@startup.io",
         "+67812345678", "Cool Startup LLC", "commercial"),
        ("Laura Martin", "laura.martin@techcorp.io",
         "+11234567890", "TechCorp Inc.", "commercial"),
        ("Michael Johnson", "michael.johnson@enterprise.com",
         "+33123456789", "Enterprise Solutions", "commercial"),
    ]
    clients = {}
    for name, mail, phone, comp, role in clients_def:
        c = session.query(Client).filter_by(email=mail).first()
        if not c:
            c = Client(
                full_name=name,
                email=mail,
                phone=phone,
                company_name=comp,
                commercial_id=users[role].id
            )
            session.add(c)
            session.commit()
            print(f"Client '{name}' inséré (ID={c.id})")
        else:
            print(f"Client '{name}' existe (ID={c.id})")
        clients[c.id] = c

    # 4) Contrats + événements
    for c in clients.values():
        ctr = session.query(Contract).filter_by(client_id=c.id).first()
        if not ctr:
            ctr = Contract(
                client_id=c.id,
                commercial_id=users["commercial"].id,
                total_amount=20000.0,
                remaining_amount=10000.0,
                is_signed=False
            )
            session.add(ctr)
            session.commit()
            print(f"Contrat inséré (ID={ctr.id}) pour client {c.full_name}")
        else:
            print(f"Contrat existe (ID={ctr.id}) pour client {c.full_name}")

        ev = session.query(Event).filter_by(contract_id=ctr.id).first()
        if not ev:
            ev = Event(
                contract_id=ctr.id,
                support_id=users["support"].id,
                date_start=datetime.datetime(2023, 7, 1, 10, 0),
                date_end=datetime.datetime(2023, 7, 1, 18, 0),
                location="123 Event Street, Cityville",
                attendees=150,
                notes="Événement exemple"
            )
            session.add(ev)
            session.commit()
            print(f"Événement inséré (ID={ev.id}) pour contrat {ctr.id}")
        else:
            print(f"Événement existe (ID={ev.id}) pour contrat {ctr.id}")

    session.close()
    print("Seed terminé.")
