# tests/testintegration/test_integration_write.py
# ==============================================================
# Tests d’intégration : vérifie, sur une vraie base de données
# définie dans .env, que les opérations d’écriture fonctionnent
# correctement (créations, mises à jour, relations).
# ==============================================================

from __future__ import annotations
import unittest
from datetime import datetime

from app.config.database import DatabaseConfig, DatabaseConnection
from app.models import Base
from app.models.role import Role
from app.models.user import User

from app.controllers.data_writer import DataWriter


class TestIntegrationWrite(unittest.TestCase):
    """
    Batteries de tests d’intégration pour la couche DataWriter.

    Chaque test :
        • se connecte à la base MySQL renseignée dans le fichier .env ;
        • crée (ou ré‑initialise) le schéma complet ;
        • effectue une ou plusieurs opérations d’écriture ;
        • vérifie par requête directe que la base reflète bien l’action.
    """

    # ------------------------------------------------------------------
    # Phase de préparation / nettoyage
    # ------------------------------------------------------------------
    def setUp(self) -> None:
        """Initialise une base neuve et prépare un DataWriter pour les tests."""
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)

        # Création du schéma (idempotent).
        Base.metadata.create_all(bind=self.db_connection.engine)
        self.session = self.db_connection.create_session()

        # S’assure que le rôle « commercial » (id = 2) existe.
        if not self.session.query(Role).filter_by(id=2).first():
            self.session.add(Role(id=2, name="commercial",
                                  description="Role for integration tests"))
            self.session.commit()

        # Outil métier sous test
        self.data_writer = DataWriter(self.db_connection)

    def tearDown(self) -> None:
        """Nettoie la base après chaque test pour repartir d’un état vierge."""
        self.session.close()
        Base.metadata.drop_all(bind=self.db_connection.engine, checkfirst=True)
        self.db_connection.engine.dispose()

    # ------------------------------------------------------------------
    # Cas de test
    # ------------------------------------------------------------------
    def test_create_user_in_mysql(self) -> None:
        """Création simple d’un collaborateur commercial puis vérification."""
        current_user = {"id": 999, "role": "gestion"}
        local_session = self.db_connection.create_session()

        # Création
        new_user = self.data_writer.create_user(
            local_session,
            current_user,
            employee_number="EMP_INT001",
            first_name="Integration",
            last_name="User",
            email="integration.user@example.com",
            password_hash="hashed_integration",
            role_id=2
        )

        # Vérifications en base
        self.assertIsNotNone(new_user)
        self.assertIsNotNone(new_user.id)

        found = local_session.query(User).filter_by(
            employee_number="EMP_INT001").first()
        self.assertIsNotNone(found)
        self.assertEqual(found.first_name, "Integration")
        self.assertEqual(found.role_id, 2)

        local_session.close()

    def test_create_contract_in_mysql(self) -> None:
        """
        • Crée un commercial ;
        • Crée un client lié ;
        • Crée un contrat puis le met à jour ;
        • Vérifie chaque étape.
        """
        local_session = self.db_connection.create_session()
        current_user = {"id": 999, "role": "gestion"}

        commercial = self.data_writer.create_user(
            local_session,
            current_user,
            employee_number="EMP_INT002",
            first_name="Commercial",
            last_name="Integration",
            email="commercial.integration@example.com",
            password_hash="somehash",
            role_id=2
        )

        client = self.data_writer.create_client(
            local_session,
            current_user,
            full_name="Client Int",
            email="client.int@example.com",
            phone="0123456789",
            company_name="Int Company",
            commercial_id=commercial.id
        )

        contract = self.data_writer.create_contract(
            local_session,
            current_user,
            client_id=client.id,
            total_amount=5000.0,
            remaining_amount=2500.0,
            is_signed=False
        )

        # Mise à jour
        updated = self.data_writer.update_contract(
            local_session,
            current_user,
            contract.id,
            total_amount=6000.0,
            remaining_amount=3000.0,
            is_signed=False
        )

        # Vérifications
        self.assertEqual(updated.total_amount, 6000.0)
        self.assertEqual(updated.remaining_amount, 3000.0)

        local_session.close()

    def test_update_event_assign_by_employee_number(self) -> None:
        """
        Crée un contrat + événement sans support, puis assigne un support
        identifié par son *employee_number*.
        """
        local_session = self.db_connection.create_session()
        current_user = {"id": 999, "role": "gestion"}

        # Préparation : commercial, client, contrat signé
        commercial = self.data_writer.create_user(
            local_session,
            current_user,
            employee_number="EMP_INT003",
            first_name="Commercial",
            last_name="User",
            email="commercial.user@example.com",
            password_hash="hash",
            role_id=2
        )

        client = self.data_writer.create_client(
            local_session,
            current_user,
            full_name="Event Client",
            email="event.client@example.com",
            phone="0123456789",
            company_name="Event Corp",
            commercial_id=commercial.id
        )

        contract = self.data_writer.create_contract(
            local_session,
            current_user,
            client_id=client.id,
            total_amount=8000.0,
            remaining_amount=4000.0,
            is_signed=True
        )

        # Événement sans support
        event = self.data_writer.create_event(
            local_session,
            current_user,
            contract_id=contract.id,
            support_id=None,
            date_start=datetime(2023, 7, 10, 9, 0),
            date_end=datetime(2023, 7, 10, 17, 0),
            location="Event Location",
            attendees=100,
            notes="Initial event without support"
        )

        # Récupération ou création du support « S001 »
        support = local_session.query(User).filter_by(
            employee_number="S001").first()
        if not support:
            support = self.data_writer.create_user(
                local_session,
                current_user,
                employee_number="S001",
                first_name="Support",
                last_name="User",
                email="support.user@example.com",
                password_hash="supporthash",
                role_id=2
            )

        # Assignation du support
        updated_event = self.data_writer.update_event(
            local_session,
            current_user,
            event.id,
            support_id=support.id
        )

        self.assertEqual(updated_event.support_id, support.id)
        local_session.close()


if __name__ == "__main__":
    unittest.main()
