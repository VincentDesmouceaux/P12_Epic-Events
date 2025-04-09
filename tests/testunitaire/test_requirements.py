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
         - Chaque collaborateur doit avoir ses identifiants et être associé à un rôle.
         - La plateforme doit permettre de stocker et de lire les informations sur les clients, contrats, et événements.
        """
        # Enregistrer un utilisateur via AuthController.register_user (avec un mot de passe en clair)
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

        # Tester l'authentification
        auth_user = self.auth_controller.authenticate_user(
            self.session,
            email="general.user@example.com",
            password="GeneralPass123"
        )
        self.assertIsNotNone(
            auth_user, "L'authentification doit réussir pour le bon mot de passe.")
        # Assurez-vous que le rôle est accessible (avant de fermer la session)
        self.assertEqual(auth_user.role.name, "gestion",
                         "Le rôle de l'utilisateur doit être 'gestion'.")

        # Création d'objets liés (client, contrat, événement)
        # Création d'un utilisateur commercial
        commercial = self.auth_controller.register_user(
            self.session,
            employee_number="GEN002",
            first_name="Commer",
            last_name="Cial",
            email="commercial@example.com",
            password="CommercialPass123",
            role_id=self.roles["commercial"].id
        )
        # Création d'un client associé au commercial
        client = Client(
            full_name="Client General",
            email="client.general@example.com",
            phone="1234567890",
            company_name="General Corp",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()

        # Création d'un contrat pour ce client
        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=15000.0,
            remaining_amount=15000.0,
            is_signed=False
        )
        self.session.add(contract)
        self.session.commit()

        # Création d'un événement pour ce contrat
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
        clients = self.data_reader.get_all_clients(self.session, current_user)
        contracts = self.data_reader.get_all_contracts(
            self.session, current_user)
        events = self.data_reader.get_all_events(self.session, current_user)
        self.assertGreaterEqual(
            len(clients), 1, "Au moins un client doit être présent.")
        self.assertGreaterEqual(
            len(contracts), 1, "Au moins un contrat doit être présent.")
        self.assertGreaterEqual(
            len(events), 1, "Au moins un événement doit être présent.")

    def test_gestion_team_requirements(self):
        """
        Besoins équipe de gestion :
         - Créer et mettre à jour des collaborateurs, contrats et événements.
         - Modifier un événement pour lui assigner un membre support.
        """
        current_user = {"id": 1, "role": "gestion"}
        # Créer un collaborateur via DataWriter.create_user (uniquement 'gestion' autorisé)
        new_collab = self.data_writer.create_user(
            self.session,
            current_user,
            employee_number="G001",
            first_name="Gestion",
            last_name="User",
            email="gestion.user@example.com",
            password_hash=self.auth_controller.hasher.hash("GestionPass"),
            role_id=self.roles["gestion"].id
        )
        self.assertIsNotNone(new_collab, "Le collaborateur doit être créé.")

        # Mettre à jour le collaborateur
        updated_collab = self.data_writer.update_user(
            self.session,
            current_user,
            new_collab.id,
            first_name="GestionUpdated",
            email="gestion.updated@example.com"
        )
        self.assertEqual(updated_collab.first_name, "GestionUpdated")
        self.assertEqual(updated_collab.email, "gestion.updated@example.com")

        # Créer un contrat pour un client
        # D'abord créer un utilisateur commercial et un client associé
        commercial = self.auth_controller.register_user(
            self.session,
            employee_number="G002",
            first_name="Commercial",
            last_name="User",
            email="commercial.user@example.com",
            password="CommercialPass",
            role_id=self.roles["commercial"].id
        )
        client = Client(
            full_name="Gestion Client",
            email="client.gestion@example.com",
            phone="111222333",
            company_name="Gestion Corp",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()

        contract = self.data_writer.create_contract(
            self.session,
            current_user,
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=20000.0,
            remaining_amount=20000.0,
            is_signed=False
        )
        self.assertIsNotNone(contract, "Le contrat doit être créé.")

        # Mettre à jour le contrat : simuler le paiement complet
        updated_contract = self.data_writer.update_contract(
            self.session,
            current_user,
            contract.id,
            remaining_amount=0.0,
            is_signed=True
        )
        self.assertEqual(updated_contract.remaining_amount, 0.0)
        self.assertTrue(updated_contract.is_signed)

        # Créer un événement sans support assigné et ensuite l’assigner à un support
        event_ns = Event(
            contract_id=contract.id,
            support_id=None,
            date_start=datetime(2023, 2, 1, 9, 0),
            date_end=datetime(2023, 2, 1, 17, 0),
            location="No Support Location",
            attendees=50,
            notes="Event without support"
        )
        self.session.add(event_ns)
        self.session.commit()
        # Créer un support utilisateur
        support_user = self.auth_controller.register_user(
            self.session,
            employee_number="G003",
            first_name="Support",
            last_name="User",
            email="support.user@example.com",
            password="SupportPass",
            role_id=self.roles["support"].id
        )
        # Modifier l'événement pour lui assigner le support
        updated_event = self.data_writer.update_event(
            self.session,
            current_user,
            event_ns.id,
            support_id=support_user.id
        )
        self.assertEqual(updated_event.support_id, support_user.id)

    def test_commercial_team_requirements(self):
        """
        Besoins équipe commerciale :
         - Créer et mettre à jour des clients.
         - Créer et modifier des contrats.
         - Créer un événement pour un contrat signé.
        """
        current_user = {"id": 2, "role": "commercial"}
        # Créer un client via DataWriter.create_client
        new_client = self.data_writer.create_client(
            self.session,
            current_user,
            full_name="Commercial Client",
            email="client.commercial@example.com",
            phone="444555666",
            company_name="Commercial Inc.",
            commercial_id=2  # Pour le test, nous supposons que l'identifiant du commercial est 2
        )
        self.assertIsNotNone(new_client)
        # Mettre à jour le client
        updated_client = self.data_writer.update_client(
            self.session,
            current_user,
            new_client.id,
            full_name="Commercial Client Updated"
        )
        self.assertEqual(updated_client.full_name, "Commercial Client Updated")

        # Créer un contrat pour ce client
        contract = self.data_writer.create_contract(
            self.session,
            current_user,
            client_id=new_client.id,
            commercial_id=2,
            total_amount=8000.0,
            remaining_amount=8000.0,
            is_signed=False
        )
        self.assertIsNotNone(contract)

        # Mettre à jour le contrat pour simuler qu'il est entièrement payé et signé
        updated_contract = self.data_writer.update_contract(
            self.session,
            current_user,
            contract.id,
            remaining_amount=0.0,
            is_signed=True
        )
        self.assertEqual(updated_contract.remaining_amount, 0.0)
        self.assertTrue(updated_contract.is_signed)

        # Créer un événement pour le contrat signé
        event = self.data_writer.create_event(
            self.session,
            current_user,
            contract_id=contract.id,
            support_id=None,  # Pas encore assigné
            date_start=datetime(2023, 3, 1, 14, 0),
            date_end=datetime(2023, 3, 1, 20, 0),
            location="Event Location",
            attendees=150,
            notes="Commercial event"
        )
        self.assertIsNotNone(event)

    def test_support_team_requirements(self):
        """
        Besoins équipe support :
         - Filtrer et n’afficher que les événements qui leur sont attribués.
         - Mettre à jour un événement dont ils sont responsables.
        """
        # Créer un utilisateur support
        support_user = self.auth_controller.register_user(
            self.session,
            employee_number="S001",
            first_name="Support",
            last_name="Member",
            email="support.member@example.com",
            password="SupportSecret",
            role_id=self.roles["support"].id
        )
        # Créer un contrat et deux événements (un assigné au support, un non assigné)
        # Pour ce test, créons un client et un contrat dummy.
        dummy_commercial = self.auth_controller.register_user(
            self.session,
            employee_number="S002",
            first_name="Commer",
            last_name="Dummy",
            email="dummy.commercial@example.com",
            password="DummyPass",
            role_id=self.roles["commercial"].id
        )
        dummy_client = Client(
            full_name="Dummy Client",
            email="dummy.client@example.com",
            phone="000111222",
            company_name="Dummy Co",
            commercial_id=dummy_commercial.id
        )
        self.session.add(dummy_client)
        self.session.commit()

        contract = Contract(
            client_id=dummy_client.id,
            commercial_id=dummy_commercial.id,
            total_amount=5000.0,
            remaining_amount=5000.0,
            is_signed=False
        )
        self.session.add(contract)
        self.session.commit()

        # Événement 1 : assigné au support_user
        event_assigned = Event(
            contract_id=contract.id,
            support_id=support_user.id,
            date_start=datetime(2023, 4, 1, 10, 0),
            date_end=datetime(2023, 4, 1, 18, 0),
            location="Support Location",
            attendees=100,
            notes="Event for support member"
        )
        # Événement 2 : non assigné (ou assigné à un autre)
        event_not_assigned = Event(
            contract_id=contract.id,
            support_id=None,
            date_start=datetime(2023, 4, 2, 10, 0),
            date_end=datetime(2023, 4, 2, 18, 0),
            location="No Support Location",
            attendees=80,
            notes="Event without support"
        )
        self.session.add_all([event_assigned, event_not_assigned])
        self.session.commit()

        # En tant que support, DataReader.get_all_events doit renvoyer uniquement les événements dont support_id == support_user.id
        current_user = {"id": support_user.id, "role": "support"}
        events = self.data_reader.get_all_events(self.session, current_user)
        for ev in events:
            self.assertEqual(ev.support_id, support_user.id,
                             "L'événement doit être attribué au support.")

        # Mettre à jour l'événement assigné en tant que support
        updated_event = self.data_writer.update_event(
            self.session,
            {"id": support_user.id, "role": "support"},
            event_assigned.id,
            attendees=120,
            notes="Updated support event"
        )
        self.assertEqual(updated_event.attendees, 120)
        self.assertEqual(updated_event.notes, "Updated support event")


if __name__ == "__main__":
    unittest.main()
