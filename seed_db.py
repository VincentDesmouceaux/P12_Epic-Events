# seed_db.py
import datetime
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


def seed_db():
    """
    Cette fonction initialise la base de données avec des données d'exemple.
    Elle effectue les actions suivantes :
      - Crée (si besoin) les tables.
      - Insère des rôles (commercial, support, gestion) si non existants.
      - Insère des utilisateurs exemple pour chaque département.
      - Insère un client associé à un commercial.
      - Insère un contrat pour ce client.
      - Insère un événement pour ce contrat.
    """
    # Initialisation de la configuration et de la connexion à la DB
    config = DatabaseConfig()
    connection = DatabaseConnection(config)
    engine = connection.engine

    # Créer les tables si elles n'existent pas déjà
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès.")

    # Ouverture d'une session
    Session = connection.SessionLocal
    session = Session()

    # Insertion des rôles
    roles_definitions = {
        "commercial": "Département commercial",
        "support": "Département support",
        "gestion": "Département gestion"
    }
    inserted_roles = {}
    for role_name, role_desc in roles_definitions.items():
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=role_desc)
            session.add(role)
            session.commit()
            print(f"Role '{role_name}' inséré avec ID={role.id}.")
        else:
            print(f"Role '{role_name}' existe déjà avec ID={role.id}.")
        inserted_roles[role_name] = role

    # Insertion des utilisateurs
    users_data = [
        {
            "employee_number": "G001",
            "first_name": "Alice",
            "last_name": "Gestion",
            "email": "alice.gestion@example.com",
            "password_hash": "hashed_gestion",
            "role": "gestion"
        },
        {
            "employee_number": "C001",
            "first_name": "Bob",
            "last_name": "Commercial",
            "email": "bob.commercial@example.com",
            "password_hash": "hashed_commercial",
            "role": "commercial"
        },
        {
            "employee_number": "S001",
            "first_name": "Charlie",
            "last_name": "Support",
            "email": "charlie.support@example.com",
            "password_hash": "hashed_support",
            "role": "support"
        }
    ]
    inserted_users = {}
    for user_data in users_data:
        user = session.query(User).filter_by(email=user_data["email"]).first()
        if not user:
            user = User(
                employee_number=user_data["employee_number"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                role_id=inserted_roles[user_data["role"]].id
            )
            session.add(user)
            session.commit()
            print(f"Utilisateur '{user.email}' inséré avec ID={user.id}.")
        else:
            print(f"Utilisateur '{user.email}' existe déjà avec ID={user.id}.")
        inserted_users[user_data["role"]] = user

    # Insertion d'un client
    client = session.query(Client).filter_by(email="kevin@startup.io").first()
    if not client:
        client = Client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+67812345678",
            company_name="Cool Startup LLC",
            commercial_id=inserted_users["commercial"].id
        )
        session.add(client)
        session.commit()
        print(f"Client '{client.full_name}' inséré avec ID={client.id}.")
    else:
        print(f"Client '{client.full_name}' existe déjà avec ID={client.id}.")

    # Insertion d'un contrat pour ce client
    contract = session.query(Contract).filter_by(client_id=client.id).first()
    if not contract:
        contract = Contract(
            client_id=client.id,
            commercial_id=inserted_users["commercial"].id,
            total_amount=10000.0,
            remaining_amount=5000.0,
            is_signed=True
        )
        session.add(contract)
        session.commit()
        print(
            f"Contrat inséré avec ID={contract.id} pour le client {client.full_name}.")
    else:
        print(
            f"Un contrat existe déjà pour le client {client.full_name} avec ID={contract.id}.")

    # Insertion d'un événement pour ce contrat
    event = session.query(Event).filter_by(contract_id=contract.id).first()
    if not event:
        event = Event(
            contract_id=contract.id,
            support_id=inserted_users["support"].id,
            date_start=datetime.datetime(2023, 6, 4, 13, 0),
            date_end=datetime.datetime(2023, 6, 5, 2, 0),
            location="53 Rue du Château, 41120 Candé-sur-Beuvron, France",
            attendees=75,
            notes=("Wedding starts at 3PM, by the river. Catering is organized, "
                   "reception starts at 5PM. Kate needs to organize the DJ for after party.")
        )
        session.add(event)
        session.commit()
        print(
            f"Événement inséré avec ID={event.id} pour le contrat ID={contract.id}.")
    else:
        print(
            f"Un événement existe déjà pour le contrat ID={contract.id} avec ID={event.id}.")

    # Afficher un récapitulatif
    print("\n--- Récapitulatif de l'initialisation ---")
    print("Rôles insérés :", {
          role: inserted_roles[role].id for role in inserted_roles})
    print("Utilisateurs insérés :", {
          key: inserted_users[key].email for key in inserted_users})
    print("Client :", client.full_name, "ID =", client.id)
    print("Contrat ID :", contract.id)
    print("Événement ID :", event.id)

    session.close()
    print("Initialisation terminée.")


if __name__ == "__main__":
    seed_db()
