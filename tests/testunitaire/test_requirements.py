# tests/testunitaire/test_requirements.py
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import des modules de l'application
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.authentification.auth_controller import AuthController
from app.controllers.data_writer import DataWriter
from app.controllers.data_reader import DataReader

# Dummy connexion DB pour les tests unitaires (simule DatabaseConnection)


class DummyDBConnection:
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        return self.SessionLocal()


class RequirementsTestCase(unittest.TestCase):
    def setUp(self):
        # Création d'une base SQLite en mémoire
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        # Création du schéma (tables)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db_connection = DummyDBConnection(self.Session)
        self.session = self.db_connection.create_session()

        # Insertion des rôles requis : commercial, support, gestion
        self.roles = {}
        for role_name in ["commercial", "support", "gestion"]:
            role = Role(name=role_name, description=f"Département {role_name}")
            self.session.add(role)
            self.session.commit()
            self.roles[role_name] = role

        # Initialisation des contrôleurs
        self.auth_controller = AuthController()
        self.data_writer = DataWriter(self.db_connection)
        self.data_reader = DataReader(self.db_connection)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_general_requirements(self):
        """
        Besoins généraux :
         - Chaque collaborateur a ses identifiants et un rôle.
         - La plateforme permet de stocker et de lire les informations sur les clients, contrats et événements.
        """
        # Inscription d'un utilisateur via register_user (mot de passe en clair)
        user = self.auth_controller.register_user(
            self.session,
            employee_number="GEN001",
            first_name="General",
            last_name="User",
            email="general.user@example.com",
            password="GeneralPass123",
            role_id=self.roles["gestion"].id
        )
        self.assertIsNotNone(user, "L'utilisateur doit être créé.")

        # Test de l'authentification avec le bon mot de passe
        auth_user = self.auth_controller.authenticate_user(
            self.session,
            email="general.user@example.com",
            password="GeneralPass123"
        )
        self.assertIsNotNone(
            auth_user, "L'authentification doit réussir pour le bon mot de passe.")
        self.assertEqual(auth_user.role.name, "gestion",
                         "Le rôle de l'utilisateur doit être 'gestion'.")

        # Création d'objets liés
        commercial = self.auth_controller.register_user(
            self.session,
            employee_number="GEN002",
            first_name="Commer",
            last_name="Cial",
            email="commercial@example.com",
            password="CommercialPass123",
            role_id=self.roles["commercial"].id
        )
        client = Client(
            full_name="Client General",
            email="client.general@example.com",
            phone="1234567890",
            company_name="General Corp",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()

        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=15000.0,
            remaining_amount=15000.0,
            is_signed=False
        )
        self.session.add(contract)
        self.session.commit()

        event = Event(
            contract_id=contract.id,
            support_id=None,
            date_start=datetime(2023, 1, 1, 10, 0),
            date_end=datetime(2023, 1, 1, 18, 0),
            location="General Location",
            attendees=100,
            notes="General event"
        )
        self.session.add(event)
        self.session.commit()

        # Vérifier via DataReader que les objets sont récupérables
        current_user = {"id": user.id, "role": "gestion"}
        clients_list = self.data_reader.get_all_clients(
            self.session, current_user)
        contracts_list = self.data_reader.get_all_contracts(
            self.session, current_user)
        events_list = self.data_reader.get_all_events(
            self.session, current_user)
        self.assertGreaterEqual(len(clients_list), 1,
                                "Au moins un client doit être présent.")
        self.assertGreaterEqual(len(contracts_list), 1,
                                "Au moins un contrat doit être présent.")
        self.assertGreaterEqual(len(events_list), 1,
                                "Au moins un événement doit être présent.")

    def test_verify_invalid_token(self):
        """
        Teste que verify_token lève une exception sur un token invalide.
        """
        with self.assertRaises(Exception) as context:
            self.auth_controller.verify_token("token_invalide")
        self.assertIn("Jeton invalide", str(context.exception))


if __name__ == "__main__":
    unittest.main()
