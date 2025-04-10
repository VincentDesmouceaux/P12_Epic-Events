import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.role import Role
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


class DummyDBConnection:
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        return self.SessionLocal()


class ContractManagementTestCase(unittest.TestCase):
    def setUp(self):
        # Créer une base de données SQLite en mémoire
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db_conn = DummyDBConnection(self.Session)
        self.session = self.db_conn.create_session()
        # Créer les rôles
        self.role_commercial = Role(
            id=1, name="commercial", description="Département commercial")
        self.role_gestion = Role(id=3, name="gestion",
                                 description="Équipe de gestion")
        self.session.add_all([self.role_commercial, self.role_gestion])
        self.session.commit()
        self.data_writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}
        # Insérer un client avec un commercial déjà défini
        from app.models.client import Client
        self.client = Client(
            full_name="Test Client",
            email="test.client@example.com",
            phone="0123456789",
            company_name="Test Corp",
            commercial_id=1
        )
        self.session.add(self.client)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_create_contract(self):
        contract = self.data_writer.create_contract(
            self.session,
            self.current_user,
            client_id=self.client.id,
            total_amount=15000.0,
            remaining_amount=15000.0,
            is_signed=False
        )
        self.assertIsNotNone(contract)
        self.assertEqual(contract.total_amount, 15000.0)
        # Le commercial doit être celui assigné au client
        self.assertEqual(contract.commercial_id, self.client.commercial_id)

    def test_update_contract(self):
        contract = self.data_writer.create_contract(
            self.session,
            self.current_user,
            client_id=self.client.id,
            total_amount=15000.0,
            remaining_amount=15000.0,
            is_signed=False
        )
        updated = self.data_writer.update_contract(
            self.session,
            self.current_user,
            contract.id,
            remaining_amount=0.0,
            is_signed=True
        )
        self.assertEqual(updated.remaining_amount, 0.0)
        self.assertTrue(updated.is_signed)


if __name__ == '__main__':
    unittest.main()
