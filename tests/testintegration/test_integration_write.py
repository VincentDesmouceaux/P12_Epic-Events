# tests/testintegration/test_integration_write.py
import unittest
from datetime import datetime

from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from app.controllers.data_writer import DataWriter


class TestIntegrationWrite(unittest.TestCase):
    """
    Test d'intégration (sans décorateurs).
    On se connecte réellement à la base définie dans .env,
    puis on crée et modifie des données pour vérifier le bon fonctionnement.
    """

    def setUp(self):
        """
        Exécutée avant chaque test :
          - Lecture de la config via .env et initialisation de DatabaseConnection.
          - Création (ou recréation) des tables.
          - Ouverture d'une session SQLAlchemy.
          - Vérification/insertion du rôle commercial (id=2).
        """
        print("\n[INTEGRATION] setUp: Initialisation DatabaseConnection (via .env).")
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)
        Base.metadata.create_all(bind=self.db_connection.engine)
        self.session = self.db_connection.create_session()

        # Vérifie que le rôle commercial (id=2) est présent
        existing_role = self.session.query(Role).filter_by(id=2).first()
        if not existing_role:
            print("[INTEGRATION] setUp: Insertion du rôle id=2 (commercial).")
            role = Role(id=2, name="commercial",
                        description="Role for integration tests")
            self.session.add(role)
            self.session.commit()
        else:
            print("[INTEGRATION] setUp: Le rôle id=2 (commercial) existe déjà.")

        self.data_writer = DataWriter(self.db_connection)
        print("[INTEGRATION] setUp terminé.")

    def tearDown(self):
        """
        Exécutée après chaque test :
          - Fermeture de la session.
          - Suppression des tables (checkfirst=True) et fermeture de l'engine.
        """
        print("[INTEGRATION] tearDown: Fermeture de la session et drop des tables.")
        self.session.close()
        Base.metadata.drop_all(bind=self.db_connection.engine, checkfirst=True)
        self.db_connection.engine.dispose()
        print("[INTEGRATION] tearDown terminé.\n")

    def test_create_user_in_mysql(self):
        """
        Test d'intégration : création d'un utilisateur via DataWriter dans MySQL
        et vérification de son insertion dans la base.
        """
        print("[INTEGRATION] test_create_user_in_mysql: start")
        current_user = {"id": 999, "role": "gestion"}
        local_session = self.db_connection.create_session()

        new_user = self.data_writer.create_user(
            local_session,
            current_user=current_user,
            employee_number="EMP_INT001",
            first_name="Integration",
            last_name="User",
            email="integration.user@example.com",
            password_hash="hashed_integration",  # Simulé
            role_id=2  # rôle commercial
        )

        self.assertIsNotNone(new_user, "L'utilisateur doit être créé.")
        self.assertIsNotNone(new_user.id, "L'utilisateur doit avoir un ID.")
        print(f"[INTEGRATION] User created with ID={new_user.id}")

        found = local_session.query(User).filter_by(
            employee_number="EMP_INT001").first()
        self.assertIsNotNone(
            found, "L'utilisateur doit être retrouvé en base.")
        self.assertEqual(found.first_name, "Integration")
        self.assertEqual(found.role_id, 2)

        local_session.close()
        print("[INTEGRATION] test_create_user_in_mysql: end\n")

    def test_create_contract_in_mysql(self):
        """
        Test d'intégration :
          - Création d'un utilisateur commercial.
          - Création d'un client rattaché à ce commercial.
          - Création d'un contrat (la méthode create_contract récupère automatiquement
            le commercial associé au client).
          - Mise à jour du contrat en modifiant à la fois le montant total et le montant restant.
        """
        print("[INTEGRATION] test_create_contract_in_mysql: start")
        local_session = self.db_connection.create_session()
        current_user = {"id": 999, "role": "gestion"}

        # Création de l'utilisateur commercial
        new_user = self.data_writer.create_user(
            local_session,
            current_user,
            employee_number="EMP_INT002",
            first_name="Commercial",
            last_name="Integration",
            email="commercial.integration@example.com",
            password_hash="somehash",
            role_id=2  # rôle commercial
        )
        self.assertIsNotNone(
            new_user, "L'utilisateur commercial doit être créé.")
        self.assertIsNotNone(new_user.id)

        # Création d'un client associé au commercial
        new_client = self.data_writer.create_client(
            local_session,
            current_user,
            full_name="Client Int",
            email="client.int@example.com",
            phone="0123456789",
            company_name="Int Company",
            commercial_id=new_user.id
        )
        self.assertIsNotNone(new_client, "Le client doit être créé.")
        self.assertIsNotNone(new_client.id)

        # Création d'un contrat
        new_contract = self.data_writer.create_contract(
            local_session,
            current_user,
            client_id=new_client.id,
            total_amount=5000.0,
            remaining_amount=2500.0,
            is_signed=False
        )
        self.assertIsNotNone(new_contract, "Le contrat doit être créé.")
        self.assertIsNotNone(new_contract.id)
        print(f"[INTEGRATION] Contract created with ID={new_contract.id}")

        found = local_session.query(Contract).filter_by(
            id=new_contract.id).first()
        self.assertIsNotNone(found, "Le contrat doit exister en base.")
        self.assertEqual(found.remaining_amount, 2500.0)

        # Mise à jour du contrat : modification du total et du restant
        updated_contract = self.data_writer.update_contract(
            local_session,
            current_user,
            new_contract.id,
            total_amount=6000.0,
            remaining_amount=3000.0,
            is_signed=False
        )
        self.assertEqual(updated_contract.total_amount, 6000.0,
                         "Le montant total doit être mis à jour à 6000.0.")
        self.assertEqual(updated_contract.remaining_amount, 3000.0,
                         "Le montant restant doit être mis à jour à 3000.0.")

        local_session.close()
        print("[INTEGRATION] test_create_contract_in_mysql: end\n")

    def test_update_event_assign_by_employee_number(self):
        """
        Test d'intégration :
          - Création d'un contrat et d'un événement sans support.
          - Recherche d'un collaborateur support par employee_number ("S001").  
            Si aucun collaborateur ne correspond, le test le crée.
          - Mise à jour de l'événement pour y assigner le support trouvé.
        """
        print("[INTEGRATION] test_update_event_assign_by_employee_number: start")
        local_session = self.db_connection.create_session()
        current_user = {"id": 999, "role": "gestion"}

        # Création d'un utilisateur commercial et d'un client pour disposer d'un contrat.
        commercial_user = self.data_writer.create_user(
            local_session,
            current_user,
            employee_number="EMP_INT003",
            first_name="Commercial",
            last_name="User",
            email="commercial.user@example.com",
            password_hash="hash",
            role_id=2
        )
        new_client = self.data_writer.create_client(
            local_session,
            current_user,
            full_name="Event Client",
            email="event.client@example.com",
            phone="0123456789",
            company_name="Event Corp",
            commercial_id=commercial_user.id
        )
        new_contract = self.data_writer.create_contract(
            local_session,
            current_user,
            client_id=new_client.id,
            total_amount=8000.0,
            remaining_amount=4000.0,
            is_signed=True
        )
        self.assertIsNotNone(
            new_contract, "Le contrat doit être créé pour l'événement.")

        # Création d'un événement sans support
        new_event = self.data_writer.create_event(
            local_session,
            current_user,
            contract_id=new_contract.id,
            support_id=None,
            date_start=datetime(2023, 7, 10, 9, 0),
            date_end=datetime(2023, 7, 10, 17, 0),
            location="Event Location",
            attendees=100,
            notes="Initial event without support"
        )
        self.assertIsNotNone(new_event, "L'événement doit être créé.")

        # Recherche d'un collaborateur support par employee_number "S001"
        from app.models.user import User
        support_user = local_session.query(
            User).filter_by(employee_number="S001").first()
        if not support_user:
            support_user = self.data_writer.create_user(
                local_session,
                current_user,
                employee_number="S001",
                first_name="Support",
                last_name="User",
                email="support.user@example.com",
                password_hash="supporthash",
                # rôle support (ici on considère que le rôle support a l'ID 2)
                role_id=2
            )
        # Mise à jour de l'événement en assignant le support trouvé
        updated_event = self.data_writer.update_event(
            local_session,
            current_user,
            new_event.id,
            support_id=support_user.id
        )
        self.assertEqual(updated_event.support_id, support_user.id,
                         "Le support assigné doit correspondre à celui trouvé (via employee_number).")
        local_session.close()
        print("[INTEGRATION] test_update_event_assign_by_employee_number: end\n")


if __name__ == "__main__":
    unittest.main()
