"""
Tests rapides DataWriter :

1. création d’un utilisateur (gestion) ;
2. création d’un client ;
3. création puis mise à jour d’un contrat.
"""

from __future__ import annotations

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Role, Client
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


class _DummyDB:
    """Connexion SQLite en mémoire pour les tests unitaires."""

    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()


class TestDataWriterView(unittest.TestCase):
    """Vérifie un flux complet (utilisateur → client → contrat)."""

    def setUp(self) -> None:
        self.db = _DummyDB()
        self.session = self.db.create_session()
        self.auth = AuthController()
        self.writer = DataWriter(self.db)

        # rôle « gestion »
        role_gestion = Role(id=3, name="gestion")
        self.session.add(role_gestion)
        self.session.commit()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(self.db.engine)
        self.db.engine.dispose()

    def test_create_update_user_and_contract(self) -> None:
        """Flux complet : crée puis met à jour les entités."""
        # Utilisateur
        user = self.writer.create_user(
            self.session, self.current_user,
            employee_number=None,
            first_name="Jean-Pierre",
            last_name="Dupont",
            email="jp.dupont@example.com",
            password_hash=self.auth.hasher.hash("x"),
            role_id=3,
        )

        # Client
        client = Client(full_name="CL", email="cl@x", commercial_id=user.id)
        self.session.add(client)
        self.session.commit()

        # Contrat
        contract = self.writer.create_contract(
            self.session, self.current_user,
            client_id=client.id,
            total_amount=10_000.0,
            remaining_amount=5_000.0,
            is_signed=False,
        )

        # Mise à jour du contrat
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
