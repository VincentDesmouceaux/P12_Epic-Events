import datetime
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base, Role, User, Client, Contract, Event
from app.authentification.auth_controller import AuthController


def seed_db():
    """
    Insère rôles, utilisateurs, clients, contrats et 2 types d’événements :
      • avec support
      • sans support (pour tester le filtrage)
    """
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    session = conn.create_session()
    auth = AuthController()

    # ---------- 1) Rôles ----------
    roles = {}
    for name, desc in [("commercial", "Département commercial"),
                       ("support",    "Département support"),
                       ("gestion",    "Département gestion")]:
        role = session.query(Role).filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=desc)
            session.add(role)
            session.commit()
            print(f"Role '{name}' inséré (ID={role.id})")
        roles[name] = role

    # ---------- 2) Utilisateurs ----------
    users = {}
    for emp, fn, ln, mail, pwd, rname in [
        ("G001", "Alice",   "Gestion",   "alice.gestion@example.com",
         "SuperSecretGestion",   "gestion"),
        ("C001", "Bob",     "Commercial", "bob.commercial@example.com",
         "SuperSecretCommercial", "commercial"),
        ("S001", "Charlie", "Support",   "charlie.support@example.com",
         "SuperSecretSupport",   "support"),
    ]:
        u = session.query(User).filter_by(email=mail).first()
        if not u:
            u = User(employee_number=emp,
                     first_name=fn, last_name=ln, email=mail,
                     password_hash=auth.hasher.hash(pwd),
                     role_id=roles[rname].id)
            session.add(u)
            session.commit()
            print(f"Utilisateur '{mail}' inséré (ID={u.id})")
        users[rname] = u

    # ---------- 3) Clients ----------
    clients = {}
    for name, mail in [("Kevin Casey",    "kevin@startup.io"),
                       ("Laura Martin",   "laura.martin@techcorp.io"),
                       ("Michael Johnson", "michael.johnson@enterprise.com")]:
        c = session.query(Client).filter_by(email=mail).first()
        if not c:
            c = Client(full_name=name, email=mail, phone="0000000000",
                       company_name="DemoCorp", commercial_id=users["commercial"].id)
            session.add(c)
            session.commit()
            print(f"Client '{name}' inséré (ID={c.id})")
        clients[c.id] = c

    # ---------- 4) Contrats + événements ----------
    for cli in clients.values():
        ctr = session.query(Contract).filter_by(client_id=cli.id).first()
        if not ctr:
            ctr = Contract(client_id=cli.id, commercial_id=users["commercial"].id,
                           total_amount=20000.0, remaining_amount=10000.0,
                           is_signed=False)
            session.add(ctr)
            session.commit()
            print(f"Contrat #{ctr.id} créé pour client {cli.full_name}")

        # --- événement AVEC support ---
        if not session.query(Event).filter_by(contract_id=ctr.id,
                                              support_id=users["support"].id).first():
            ev = Event(contract_id=ctr.id, support_id=users["support"].id,
                       date_start=datetime.datetime(2023, 7, 1, 10, 0),
                       date_end=datetime.datetime(2023, 7, 1, 18, 0),
                       location="123 Event St.", attendees=150,
                       notes="Événement exemple")
            session.add(ev)
            session.commit()
            print(f"Événement (avec support) #{ev.id} ajouté.")

        # --- événement SANS support (utile pour le filtre) ---
        if not session.query(Event).filter_by(contract_id=ctr.id,
                                              support_id=None).first():
            ev_ns = Event(contract_id=ctr.id, support_id=None,
                          date_start=datetime.datetime(2023, 8, 1, 10, 0),
                          date_end=datetime.datetime(2023, 8, 1, 18, 0),
                          location="No-support venue", attendees=80,
                          notes="Demo event without support")
            session.add(ev_ns)
            session.commit()
            print(f"Événement (sans support) #{ev_ns.id} ajouté.")

    session.close()
    print("Seed terminé.")
