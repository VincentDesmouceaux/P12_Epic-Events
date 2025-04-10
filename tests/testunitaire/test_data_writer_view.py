# tests/testunitaire/test_data_writer_view.py
import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.contract import Contract
from app.models.event import Event
from app.views.data_writer_view import DataWriterView
from app.config.database import DatabaseConfig, DatabaseConnection

# Dummy DB connection in memory


class DummyDBConnection:
    def __init__(self):
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.SessionLocal()


class TestDataWriterView(unittest.TestCase):
    def setUp(self):
        print("\n[TEST setUp] Création de la DB in-memory et insertion du rôle id=2.")
        self.db_conn = DummyDBConnection()

        # Insérer un rôle avec id=2 (pour simuler "commercial")
        session = self.db_conn.create_session()
        role = Role(id=2, name="commercial",
                    description="Test role commercial")
        session.add(role)
        session.commit()
        session.close()

        self.view = DataWriterView(self.db_conn)

    def tearDown(self):
        print("[TEST tearDown] Suppression des tables.")
        Base.metadata.drop_all(self.db_conn.engine)
        self.db_conn.engine.dispose()

    def test_run_creates_and_updates_entities(self):
        """
        Vérifie que DataWriterView.run() crée et met à jour user, contrat et événement.
        """
        self.view.run()

        session = self.db_conn.create_session()
        user = session.query(User).filter_by(employee_number="EMP123").first()
        self.assertIsNotNone(user, "L'utilisateur doit être créé.")
        if user:
            self.assertEqual(user.first_name, "Jean-Pierre",
                             "Prénom attendu 'Jean-Pierre'.")
            self.assertEqual(user.email, "jp.dupont@example.com",
                             "Email attendu 'jp.dupont@example.com'.")

        contract = session.query(Contract).first()
        self.assertIsNotNone(contract, "Le contrat doit être créé.")
        if contract:
            self.assertEqual(contract.total_amount, 10000.0,
                             "Total attendu 10000.0.")

        event = session.query(Event).first()
        self.assertIsNotNone(event, "L'événement doit être créé.")
        if event:
            self.assertEqual(event.attendees, 80, "Attendees attendus 80.")
            self.assertEqual(
                event.notes, "Updated notes for the event.", "Notes attendues mises à jour.")

        session.close()


if __name__ == "__main__":
    unittest.main()
