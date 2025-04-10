import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.role import Role
from app.models.event import Event
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


class DummyDBConnection:
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        return self.SessionLocal()


class EventManagementTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db_conn = DummyDBConnection(self.Session)
        self.session = self.db_conn.create_session()
        # Créer des rôles
        self.role_support = Role(id=2, name="support",
                                 description="Département support")
        self.role_gestion = Role(id=3, name="gestion",
                                 description="Équipe de gestion")
        self.session.add_all([self.role_support, self.role_gestion])
        self.session.commit()
        self.data_writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}
        # Créer un contrat fictif pour les événements
        from app.models.client import Client
        from app.models.contract import Contract
        self.client = Client(
            full_name="Test Client",
            email="test.client@example.com",
            phone="0123456789",
            company_name="Test Corp",
            commercial_id=1
        )
        self.session.add(self.client)
        self.session.commit()
        self.contract = Contract(
            client_id=self.client.id,
            commercial_id=1,
            total_amount=20000.0,
            remaining_amount=10000.0,
            is_signed=False
        )
        self.session.add(self.contract)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_consult_events_without_support(self):
        # Créer deux événements, dont l'un sans support
        event1 = Event(
            contract_id=self.contract.id,
            support_id=None,
            date_start=datetime(2023, 7, 1, 10, 0),
            date_end=datetime(2023, 7, 1, 18, 0),
            location="Location A",
            attendees=100,
            notes="Event without support"
        )
        event2 = Event(
            contract_id=self.contract.id,
            support_id=2,
            date_start=datetime(2023, 7, 2, 10, 0),
            date_end=datetime(2023, 7, 2, 18, 0),
            location="Location B",
            attendees=80,
            notes="Event with support"
        )
        self.session.add_all([event1, event2])
        self.session.commit()
        events_no_support = self.session.query(
            Event).filter(Event.support_id == None).all()
        self.assertEqual(len(events_no_support), 1)
        self.assertEqual(events_no_support[0].location, "Location A")

    def test_update_event_assign_support(self):
        # Créer un événement sans support
        event = Event(
            contract_id=self.contract.id,
            support_id=None,
            date_start=datetime(2023, 7, 3, 10, 0),
            date_end=datetime(2023, 7, 3, 18, 0),
            location="Location C",
            attendees=120,
            notes="Event without support"
        )
        self.session.add(event)
        self.session.commit()
        event_id = event.id
        updated_event = self.data_writer.update_event(
            self.session,
            self.current_user,
            event_id,
            support_id=2
        )
        self.assertEqual(updated_event.support_id, 2)


if __name__ == '__main__':
    unittest.main()
