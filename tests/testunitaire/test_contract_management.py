"""
Tests unitaires – création et mise à jour de contrats (DataWriter).

On utilise une base SQLite en mémoire ; aucun accès MySQL n’est requis.
"""

from __future__ import annotations

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Role
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


class _DummyDBConnection:
    """Adapte une factory de session en objet ‘connexion’ attendu par le code."""

    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        return self.SessionLocal()


class ContractManagementTestCase(unittest.TestCase):
    """Vérifie create_contract() et update_contract() de DataWriter."""

    def setUp(self) -> None:
        # Base SQLite en mémoire
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_conn = _DummyDBConnection(Session)
        self.session = self.db_conn.create_session()

        # Rôles minimas
        self.session.add_all([
            Role(id=1, name="commercial"),
            Role(id=3, name="gestion"),
        ])
        self.session.commit()

        # Contrôleurs
        self.writer = DataWriter(self.db_conn)
        self.auth = AuthController()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}

        # Client rattaché à un commercial #
        from app.models.client import Client
        self.client = Client(
            full_name="Test Client",
            email="test.client@example.com",
            commercial_id=1,
        )
        self.session.add(self.client)
        self.session.commit()

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_create_contract(self) -> None:
        """Le contrat créé doit reprendre le commercial du client."""
        contract = self.writer.create_contract(
            self.session, self.current_user,
            client_id=self.client.id,
            total_amount=15_000.0,
            remaining_amount=15_000.0,
            is_signed=False,
        )
        self.assertIsNotNone(contract)
        self.assertEqual(contract.commercial_id, self.client.commercial_id)

    def test_update_contract(self) -> None:
        """Mise à jour : passage du restant à zéro et signature."""
        contract = self.writer.create_contract(
            self.session, self.current_user,
            client_id=self.client.id,
            total_amount=15_000.0,
            remaining_amount=15_000.0,
            is_signed=False,
        )
        updated = self.writer.update_contract(
            self.session, self.current_user,
            contract.id,
            remaining_amount=0.0,
            is_signed=True,
        )
        self.assertEqual(updated.remaining_amount, 0.0)
        self.assertTrue(updated.is_signed)


if __name__ == "__main__":
    unittest.main()
