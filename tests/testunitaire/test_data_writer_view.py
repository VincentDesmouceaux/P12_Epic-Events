import unittest
from datetime import datetime

from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.models.contract import Contract
from app.models.event import Event

from app.views.data_writer_view import DataWriterView
from app.config.database import DatabaseConfig, DatabaseConnection


class DummyDBConnection:
    """
    Classe simulant une connexion à la base via SQLite en mémoire.
    Crée les tables (Base.metadata.create_all) dès l'instanciation.
    """

    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.SessionLocal()


class TestDataWriterView(unittest.TestCase):
    def setUp(self):
        """
        - Instancie la connexion "in memory" (DummyDBConnection).
        - Crée un rôle id=2 pour que DataWriterView.run() puisse créer un user role_id=2.
        - Instancie DataWriterView.
        """
        print("\n[TEST setUp] Creating DB in memory, inserting role id=2.")
        self.db_conn = DummyDBConnection()

        # On insère un rôle ayant id=2 (ex: "commercial"),
        # car DataWriterView.run() l'utilise
        session = self.db_conn.create_session()
        new_role = Role(id=2, name="commercial",
                        description="Test role commercial")
        session.add(new_role)
        session.commit()
        session.close()

        self.view = DataWriterView(self.db_conn)

    def tearDown(self):
        print("[TEST tearDown] Dropping tables.\n")
        Base.metadata.drop_all(self.db_conn.engine)
        self.db_conn.engine.dispose()

    def test_run_creates_and_updates_entities(self):
        """
        Vérifie que l'exécution de run() de DataWriterView crée 
        et met à jour les entités attendues (User, Contract, Event).
        """
        print("[TEST] test_run_creates_and_updates_entities : Start")
        self.view.run()

        session = self.db_conn.create_session()

        # 1) Vérifier l'utilisateur
        user = session.query(User).filter_by(employee_number="EMP123").first()
        print("[TEST] user found? =>", user)
        self.assertIsNotNone(user, "L'utilisateur devrait être créé.")
        if user:
            self.assertEqual(user.first_name, "Jean-Pierre",
                             "Le prénom doit être mis à jour à 'Jean-Pierre'.")
            self.assertEqual(user.email, "jp.dupont@example.com",
                             "L'email doit être mis à jour à 'jp.dupont@example.com'.")

        # 2) Vérifier le contrat
        contract = session.query(Contract).first()
        print("[TEST] contract found? =>", contract)
        self.assertIsNotNone(contract, "Le contrat devrait être créé.")
        if contract:
            self.assertEqual(contract.total_amount, 10000.0,
                             "Le montant total doit être 10000.0.")

        # 3) Vérifier l'événement
        event = session.query(Event).first()
        print("[TEST] event found? =>", event)
        self.assertIsNotNone(event, "L'événement devrait être créé.")
        if event:
            self.assertEqual(event.attendees, 80,
                             "Le nombre d'attendees doit être mis à jour à 80.")
            self.assertEqual(event.notes, "Updated notes for the event.",
                             "Les notes doivent être mises à jour.")

        session.close()
        print("[TEST] test_run_creates_and_updates_entities : End\n")


if __name__ == "__main__":
    unittest.main()
