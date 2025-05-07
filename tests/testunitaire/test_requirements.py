# tests/testunitaire/test_requirements.py
# -*- coding: utf-8 -*-
"""
Tests d’acceptation – validation des « requirements » généraux.

Couvre :
    • création et authentification d’utilisateurs ;
    • persistance et récupération de clients, contrats et événements ;
    • détection d’un jeton JWT invalide.
"""

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
from app.authentification.auth_controller import AuthController
from app.controllers.data_writer import DataWriter
from app.controllers.data_reader import DataReader


class DummyDBConnection:
    """Connexion BD simulée pour injection dans les contrôleurs."""

    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        """Renvoie une nouvelle session SQLAlchemy."""
        return self.SessionLocal()


class RequirementsTestCase(unittest.TestCase):
    """Tests haut niveau vérifiant les besoins fonctionnels de base."""

    # ------------------------------------------------------------------ #
    # SET‑UP / TEAR‑DOWN                                                 #
    # ------------------------------------------------------------------ #
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.db_connection = DummyDBConnection(self.Session)
        self.session = self.db_connection.create_session()

        # Insertion des trois rôles indispensables
        self.roles = {}
        for name in ("commercial", "support", "gestion"):
            role = Role(name=name, description=f"Département {name}")
            self.session.add(role)
            self.session.commit()
            self.roles[name] = role

        self.auth_controller = AuthController()
        self.data_writer = DataWriter(self.db_connection)
        self.data_reader = DataReader(self.db_connection)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    # ------------------------------------------------------------------ #
    # TESTS                                                              #
    # ------------------------------------------------------------------ #
    def test_general_requirements(self):
        """Vérifie la chaîne complète : user → client → contrat → évènement."""
        user = self.auth_controller.register_user(
            self.session,
            employee_number="GEN001",
            first_name="General",
            last_name="User",
            email="general.user@example.com",
            password="GeneralPass123",
            role_id=self.roles["gestion"].id,
        )
        self.assertIsNotNone(user)

        auth_user = self.auth_controller.authenticate_user(
            self.session, email="general.user@example.com", password="GeneralPass123"
        )
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.role.name, "gestion")

        commercial = self.auth_controller.register_user(
            self.session,
            employee_number="GEN002",
            first_name="Commer",
            last_name="Cial",
            email="commercial@example.com",
            password="CommercialPass123",
            role_id=self.roles["commercial"].id,
        )
        client = Client(
            full_name="Client General",
            email="client.general@example.com",
            phone="1234567890",
            company_name="General Corp",
            commercial_id=commercial.id,
        )
        self.session.add(client)
        self.session.commit()

        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=15_000.0,
            remaining_amount=15_000.0,
            is_signed=False,
        )
        self.session.add(contract)
        self.session.commit()

        event = Event(
            contract_id=contract.id,
            support_id=None,
            date_start=datetime(2023, 1, 1, 10),
            date_end=datetime(2023, 1, 1, 18),
            location="General Location",
            attendees=100,
            notes="General event",
        )
        self.session.add(event)
        self.session.commit()

        current_user = {"id": user.id, "role": "gestion"}

        self.assertGreaterEqual(
            len(self.data_reader.get_all_clients(self.session, current_user)), 1
        )
        self.assertGreaterEqual(
            len(self.data_reader.get_all_contracts(
                self.session, current_user)), 1
        )
        self.assertGreaterEqual(
            len(self.data_reader.get_all_events(self.session, current_user)), 1
        )

    def test_verify_invalid_token(self):
        """`verify_token` doit lever une exception pour un JWT invalide."""
        with self.assertRaises(Exception) as ctx:
            self.auth_controller.verify_token("token_invalide")
        self.assertIn("Jeton invalide", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
