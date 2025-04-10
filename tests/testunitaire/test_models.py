# tests/testunitaire/test_models.py
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class TestModels(unittest.TestCase):
    """
    Tests pour vérifier la création des modèles et leurs relations.
    """

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Insertion d'un rôle de test
        self.test_role = Role(name="commercial", description="Test Role")
        self.session.add(self.test_role)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_create_user(self):
        user = User(
            employee_number="EMP001",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            password_hash="dummyhash",
            role_id=self.test_role.id
        )
        self.session.add(user)
        self.session.commit()
        queried = self.session.query(User).filter_by(
            email="john.doe@example.com").first()
        self.assertIsNotNone(queried, "L'utilisateur doit être créé.")
        self.assertEqual(queried.first_name, "John")

    def test_create_client(self):
        commercial = User(
            employee_number="EMP002",
            first_name="Alice",
            last_name="Smith",
            email="alice.smith@example.com",
            password_hash="dummyhash",
            role_id=self.test_role.id
        )
        self.session.add(commercial)
        self.session.commit()
        client = Client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+67812345678",
            company_name="Cool Startup LLC",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()
        queried_client = self.session.query(Client).filter_by(
            email="kevin@startup.io").first()
        self.assertIsNotNone(queried_client, "Le client doit être créé.")
        self.assertEqual(queried_client.commercial.first_name, "Alice")

    def test_create_contract(self):
        commercial = User(
            employee_number="EMP003",
            first_name="Bob",
            last_name="Martin",
            email="bob.martin@example.com",
            password_hash="dummyhash",
            role_id=self.test_role.id
        )
        self.session.add(commercial)
        self.session.commit()
        client = Client(
            full_name="Jane Doe",
            email="jane.doe@example.com",
            company_name="Acme Corp",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()
        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=10000.0,
            remaining_amount=5000.0,
            is_signed=True
        )
        self.session.add(contract)
        self.session.commit()
        queried_contract = self.session.query(
            Contract).filter_by(client_id=client.id).first()
        self.assertIsNotNone(queried_contract, "Le contrat doit être créé.")
        self.assertTrue(queried_contract.is_signed)
        self.assertEqual(queried_contract.total_amount, 10000.0)

    def test_create_event(self):
        commercial = User(
            employee_number="EMP004",
            first_name="Carol",
            last_name="Dupont",
            email="carol.dupont@example.com",
            password_hash="dummyhash",
            role_id=self.test_role.id
        )
        support = User(
            employee_number="EMP005",
            first_name="David",
            last_name="Lefevre",
            email="david.lefevre@example.com",
            password_hash="dummyhash",
            role_id=self.test_role.id
        )
        self.session.add_all([commercial, support])
        self.session.commit()
        client = Client(
            full_name="John Smith",
            email="john.smith@example.com",
            company_name="Smith Inc.",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()
        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=15000.0,
            remaining_amount=0.0,
            is_signed=True
        )
        self.session.add(contract)
        self.session.commit()
        event = Event(
            contract_id=contract.id,
            support_id=support.id,
            date_start=datetime(2023, 6, 4, 13, 0),
            date_end=datetime(2023, 6, 5, 2, 0),
            location="53 Rue du Château, Candé-sur-Beuvron, France",
            attendees=75,
            notes="Wedding starts at 3PM, by the river."
        )
        self.session.add(event)
        self.session.commit()
        queried_event = self.session.query(Event).filter_by(
            contract_id=contract.id).first()
        self.assertIsNotNone(queried_event, "L'événement doit être créé.")
        self.assertEqual(queried_event.support.first_name, "David")
        self.assertEqual(queried_event.location,
                         "53 Rue du Château, Candé-sur-Beuvron, France")


if __name__ == '__main__':
    unittest.main()
