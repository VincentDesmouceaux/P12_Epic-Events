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
    Test d'intégration (sans aucun décorateur).
    On se connecte réellement à la base MySQL définie dans .env,
    puis on écrit/lit des données pour vérifier le bon fonctionnement.
    """

    def setUp(self):
        """
        Appelée avant CHAQUE test.
          - Lit la config via .env et initialise DatabaseConnection.
          - Crée toutes les tables dans la base.
          - Ouvre une session.
          - Insère un rôle (id=2, ex: "commercial") s'il n'existe pas.
        """
        print("\n[INTEGRATION] setUp: Initialisation DatabaseConnection (via .env).")
        # Lecture de la configuration depuis .env
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)
        # Création des tables dans la base MySQL
        Base.metadata.create_all(bind=self.db_connection.engine)
        # Ouverture d'une session
        self.session = self.db_connection.create_session()

        # Vérifier que le rôle avec id=2 existe ; sinon, l'insérer.
        existing_role = self.session.query(Role).filter_by(id=2).first()
        if not existing_role:
            print("[INTEGRATION] setUp: Insertion du rôle id=2.")
            role = Role(id=2, name="commercial",
                        description="Role for integration tests")
            self.session.add(role)
            self.session.commit()
        else:
            print("[INTEGRATION] setUp: Le rôle id=2 existe déjà.")

        # Instanciation du contrôleur DataWriter
        self.data_writer = DataWriter(self.db_connection)
        print("[INTEGRATION] setUp terminé.")

    def tearDown(self):
        """
        Appelée après CHAQUE test.
          - Ferme la session.
          - Pour garantir l'isolation des tests, on supprime toutes les tables.
        """
        print("[INTEGRATION] tearDown: Fermeture de la session et drop des tables.")
        self.session.close()
        Base.metadata.drop_all(bind=self.db_connection.engine)
        print("[INTEGRATION] tearDown terminé.\n")

    def test_create_user_in_mysql(self):
        """
        Test d'intégration : on crée un utilisateur via DataWriter dans MySQL 
        et on vérifie qu'il est correctement inséré en base.
        """
        print("[INTEGRATION] test_create_user_in_mysql: start")
        # Simule un utilisateur "gestion" autorisé à créer des utilisateurs
        current_user = {"id": 999, "role": "gestion"}

        # Création d'une session locale
        local_session = self.db_connection.create_session()

        new_user = self.data_writer.create_user(
            local_session,
            current_user=current_user,
            employee_number="EMP_INT001",
            first_name="Integration",
            last_name="User",
            email="integration.user@example.com",
            password_hash="hashed_integration",  # Pour le test, on simule un hash
            role_id=2  # Doit correspondre au rôle inséré dans setUp
        )

        # Vérification
        self.assertIsNotNone(new_user, "L'utilisateur doit être créé.")
        self.assertIsNotNone(new_user.id, "L'utilisateur doit avoir un ID.")
        print(f"[INTEGRATION] User created with ID={new_user.id}")

        found = local_session.query(User).filter_by(
            employee_number="EMP_INT001").first()
        self.assertIsNotNone(found, "On doit retrouver l'utilisateur en base.")
        self.assertEqual(found.first_name, "Integration")
        self.assertEqual(found.role_id, 2)
        local_session.close()
        print("[INTEGRATION] test_create_user_in_mysql: end\n")

    def test_create_contract_in_mysql(self):
        """
        Test d'intégration : on crée un utilisateur commercial, un client, puis un contrat.
        """
        print("[INTEGRATION] test_create_contract_in_mysql: start")
        local_session = self.db_connection.create_session()
        current_user = {"id": 999, "role": "gestion"}

        # Création d'un utilisateur commercial
        new_user = self.data_writer.create_user(
            local_session,
            current_user,
            employee_number="EMP_INT002",
            first_name="Commercial",
            last_name="Integration",
            email="commercial.integration@example.com",
            password_hash="somehash",
            role_id=2  # "commercial"
        )
        self.assertIsNotNone(
            new_user, "L'utilisateur commercial doit être créé.")
        self.assertIsNotNone(new_user.id)

        # Création d'un client associé à cet utilisateur
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
            commercial_id=new_user.id,
            total_amount=5000.0,
            remaining_amount=2500.0,
            is_signed=False
        )
        self.assertIsNotNone(new_contract, "Le contrat doit être créé.")
        self.assertIsNotNone(new_contract.id)
        print(f"[INTEGRATION] Contract created with ID={new_contract.id}")

        # Vérification du contrat en base
        found = local_session.query(Contract).filter_by(
            id=new_contract.id).first()
        self.assertIsNotNone(found, "Le contrat doit exister en base.")
        self.assertEqual(found.remaining_amount, 2500.0)
        local_session.close()
        print("[INTEGRATION] test_create_contract_in_mysql: end\n")


if __name__ == "__main__":
    unittest.main()
