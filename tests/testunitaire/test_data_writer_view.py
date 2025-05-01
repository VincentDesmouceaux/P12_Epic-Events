"""
Tests rapides : création d’un utilisateur puis d’un client & contrat,
puis mise à jour du contrat – le tout via DataWriter (pas la vue CLI).
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Role, User, Client
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


# ------------------------------------------------------------------ #
#  Connexion factice                                                 #
# ------------------------------------------------------------------ #
class _DummyDB:
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()


# ------------------------------------------------------------------ #
#  Suite                                                             #
# ------------------------------------------------------------------ #
class TestDataWriterView(unittest.TestCase):
    def setUp(self):
        self.db = _DummyDB()
        self.session = self.db.create_session()
        self.auth = AuthController()
        self.writer = DataWriter(self.db)

        # rôle « gestion »
        self.role_g = Role(id=3, name="gestion")
        self.session.add(self.role_g)
        self.session.commit()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.db.engine)
        self.db.engine.dispose()

    def test_create_update_user_and_contract(self):
        # ----- utilisateur -----
        user = self.writer.create_user(
            self.session, self.current_user,
            employee_number=None,
            first_name="Jean-Pierre",
            last_name="Dupont",
            email="jp.dupont@example.com",
            password_hash=self.auth.hasher.hash("x"),
            role_id=3,
        )
        self.assertTrue(user.employee_number.startswith("G"))

        # ----- client -----
        client = Client(full_name="CL", email="cl@x", commercial_id=user.id)
        self.session.add(client)
        self.session.commit()

        # ----- contrat -----
        contract = self.writer.create_contract(
            self.session, self.current_user,
            client_id=client.id,
            total_amount=10_000.0,
            remaining_amount=5_000.0,
            is_signed=False,
        )
        self.assertEqual(contract.total_amount, 10_000.0)

        # ----- mise à jour -----
        updated = self.writer.update_contract(
            self.session,
            self.current_user,
            contract.id,
            remaining_amount=0.0,
            is_signed=True,
        )
        self.assertEqual(updated.remaining_amount, 0.0)
        self.assertTrue(updated.is_signed)


if __name__ == "__main__":
    unittest.main()
