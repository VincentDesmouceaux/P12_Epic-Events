import unittest
from datetime import datetime
from app.models import Base
from app.models.user import User
from app.models.contract import Contract
from app.models.event import Event

from app.views.data_writer_view import DataWriterView
from app.config.database import DatabaseConfig, DatabaseConnection

# Classe DummyDBConnection : simule une connexion à la base en mémoire et crée les tables


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        # Créer toutes les tables définies dans Base
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.SessionLocal()


class TestDataWriterView(unittest.TestCase):
    def setUp(self):
        self.db_conn = DummyDBConnection()
        self.view = DataWriterView(self.db_conn)

    def tearDown(self):
        Base.metadata.drop_all(self.db_conn.engine)
        self.db_conn.engine.dispose()

    def test_run_creates_and_updates_entities(self):
        """
        Vérifie que l'exécution de run() de DataWriterView crée et met à jour
        les entités attendues (User, Contract, Event).
        """
        self.view.run()
        session = self.db_conn.create_session()
        # Vérifier la création et mise à jour de l'utilisateur
        user = session.query(User).filter_by(employee_number="EMP123").first()
        self.assertIsNotNone(user, "L'utilisateur devrait être créé.")
        self.assertEqual(user.first_name, "Jean-Pierre",
                         "Le prénom doit être mis à jour à 'Jean-Pierre'.")
        self.assertEqual(user.email, "jp.dupont@example.com",
                         "L'email doit être mis à jour à 'jp.dupont@example.com'.")

        # Vérifier que le contrat a été créé
        contract = session.query(Contract).first()
        self.assertIsNotNone(contract, "Le contrat devrait être créé.")
        self.assertEqual(contract.total_amount, 10000.0,
                         "Le montant total doit être 10000.0.")

        # Vérifier que l'événement a été créé et mis à jour
        event = session.query(Event).first()
        self.assertIsNotNone(event, "L'événement devrait être créé.")
        self.assertEqual(event.attendees, 80,
                         "Le nombre d'attendees doit être mis à jour à 80.")
        self.assertEqual(event.notes, "Updated notes for the event.",
                         "Les notes doivent être mises à jour.")
        session.close()


if __name__ == "__main__":
    unittest.main()
