# app/seed_db.py
import datetime
from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event

# Pour hacher les mots de passe
from app.authentification.auth_controller import AuthController


def seed_db():
    """
    Cette fonction insère des données d'exemple dans la base de données.
    Les actions effectuées sont :
      - Insérer (si non existant) les rôles : commercial, support, gestion.
      - Insérer des utilisateurs exemples pour chaque département, avec des mots de passe hachés.
      - Insérer plusieurs clients, contrats et événements.
      - Si la donnée existe déjà (identifiée par un email ou autre identifiant unique),
        elle n'est pas réinsérée.
    Note : Ce script ne vide pas la base.
    """
    # Initialisation de la configuration et de la connexion
    config = DatabaseConfig()
    connection = DatabaseConnection(config)
    engine = connection.engine

    print("Insertion des données d'exemple...")
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

    # Instanciation d'AuthController pour hacher les mots de passe
    auth_controller = AuthController()

    # Insertion d'exemples d'utilisateurs pour chaque département.
    users_data = [
        {
            "employee_number": "G001",
            "first_name": "Alice",
            "last_name": "Gestion",
            "email": "alice.gestion@example.com",
            "password": "SuperSecretGestion",
            "role": "gestion"
        },
        {
            "employee_number": "C001",
            "first_name": "Bob",
            "last_name": "Commercial",
            "email": "bob.commercial@example.com",
            "password": "SuperSecretCommercial",
            "role": "commercial"
        },
        {
            "employee_number": "S001",
            "first_name": "Charlie",
            "last_name": "Support",
            "email": "charlie.support@example.com",
            "password": "SuperSecretSupport",
            "role": "support"
        }
    ]
    inserted_users = {}
    for user_data in users_data:
        user = session.query(User).filter_by(email=user_data["email"]).first()
        if not user:
            hashed_password = auth_controller.hasher.hash(
                user_data["password"])
            user = User(
                employee_number=user_data["employee_number"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                password_hash=hashed_password,
                role_id=inserted_roles[user_data["role"]].id
            )
            session.add(user)
            session.commit()
            print(f"Utilisateur '{user.email}' inséré avec ID={user.id}.")
        else:
            print(f"Utilisateur '{user.email}' existe déjà avec ID={user.id}.")
        inserted_users[user_data["role"]] = user

    # Insertion de plusieurs clients
    clients_data = [
        {
            "full_name": "Kevin Casey",
            "email": "kevin@startup.io",
            "phone": "+67812345678",
            "company_name": "Cool Startup LLC",
            "commercial_role": "commercial"
        },
        {
            "full_name": "Laura Martin",
            "email": "laura.martin@techcorp.io",
            "phone": "+11234567890",
            "company_name": "TechCorp Inc.",
            "commercial_role": "commercial"
        },
        {
            "full_name": "Michael Johnson",
            "email": "michael.johnson@enterprise.com",
            "phone": "+33123456789",
            "company_name": "Enterprise Solutions",
            "commercial_role": "commercial"
        }
    ]
    inserted_clients = {}
    for client_data in clients_data:
        client = session.query(Client).filter_by(
            email=client_data["email"]).first()
        if not client:
            client = Client(
                full_name=client_data["full_name"],
                email=client_data["email"],
                phone=client_data["phone"],
                company_name=client_data["company_name"],
                commercial_id=inserted_users[client_data["commercial_role"]].id
            )
            session.add(client)
            session.commit()
            print(f"Client '{client.full_name}' inséré avec ID={client.id}.")
        else:
            print(
                f"Client '{client.full_name}' existe déjà avec ID={client.id}.")
        inserted_clients[client_data["email"]] = client

    # Insertion de contrats pour chacun des clients
    inserted_contracts = {}
    for client in inserted_clients.values():
        contract = session.query(Contract).filter_by(
            client_id=client.id).first()
        if not contract:
            contract = Contract(
                client_id=client.id,
                commercial_id=inserted_users["commercial"].id,
                total_amount=20000.0,
                remaining_amount=10000.0,
                is_signed=False  # Exemple : contrat non signé
            )
            session.add(contract)
            session.commit()
            print(
                f"Contrat inséré avec ID={contract.id} pour le client {client.full_name}.")
        else:
            print(
                f"Contrat existe déjà pour le client {client.full_name} avec ID={contract.id}.")
        inserted_contracts[client.id] = contract

    # Insertion d'événements pour certains contrats
    for client_id, contract in inserted_contracts.items():
        event = session.query(Event).filter_by(contract_id=contract.id).first()
        if not event:
            event = Event(
                contract_id=contract.id,
                support_id=inserted_users["support"].id,
                date_start=datetime.datetime(2023, 7, 1, 10, 0),
                date_end=datetime.datetime(2023, 7, 1, 18, 0),
                location="123 Event Street, Cityville",
                attendees=150,
                notes="Événement d'exemple organisé pour le client."
            )
            session.add(event)
            session.commit()
            print(
                f"Événement inséré avec ID={event.id} pour le contrat ID={contract.id}.")
        else:
            print(
                f"Événement existe déjà pour le contrat ID={contract.id} avec ID={event.id}.")

    # Récapitulatif
    print("\n--- Récapitulatif de l'initialisation ---")
    print("Rôles insérés :", {
          role: inserted_roles[role].id for role in inserted_roles})
    print("Utilisateurs insérés :", {
          key: inserted_users[key].email for key in inserted_users})
    for client in inserted_clients.values():
        print("Client :", client.full_name, "ID =", client.id)
    for contract in inserted_contracts.values():
        print("Contrat ID :", contract.id)
        event = session.query(Event).filter_by(contract_id=contract.id).first()
        print(f"  Événement ID = {event.id if event else 'None'}")

    session.close()
    print("Initialisation terminée.")


if __name__ == "__main__":
    seed_db()
