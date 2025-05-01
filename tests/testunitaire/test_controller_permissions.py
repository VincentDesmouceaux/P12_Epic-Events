"""
Tests unitaires – règles d’autorisation / DataReader & DataWriter
Tous les rôles PEUVENT lire ; les filtres ne s’activent que si
`current_user` contient force_filter=True.
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
from app.controllers.data_writer import DataWriter
from app.controllers.data_reader import DataReader


# --------------------------------------------------------------------------- #
#  Connexion factice (équivalent minimal de DatabaseConnection)               #
# --------------------------------------------------------------------------- #
class DummyDBConnection:
    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        return self.SessionLocal()


# --------------------------------------------------------------------------- #
#                                 Cas de test                                 #
# --------------------------------------------------------------------------- #
class PermissionsTestCase(unittest.TestCase):
    def setUp(self):
        # ---------- base en mémoire + session ----------
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_conn = DummyDBConnection(Session)
        self.session = self.db_conn.create_session()

        # ---------- rôles ----------
        self.r_com = Role(id=1, name="commercial")
        self.r_sup = Role(id=2, name="support")
        self.r_ges = Role(id=3, name="gestion")
        self.session.add_all([self.r_com, self.r_sup, self.r_ges])
        self.session.commit()

        # ---------- utilisateurs  (last_name obligatoire !) ----------
        self.u_com = User(employee_number="C001", first_name="Com", last_name="User",
                          email="c@x", password_hash="h", role_id=1)
        self.u_sup = User(employee_number="S001", first_name="Sup", last_name="User",
                          email="s@x", password_hash="h", role_id=2)
        self.u_ges = User(employee_number="G001", first_name="Ges", last_name="User",
                          email="g@x", password_hash="h", role_id=3)
        self.session.add_all([self.u_com, self.u_sup, self.u_ges])
        self.session.commit()

        # ---------- clients ----------
        self.client_a = Client(full_name="A", email="a@x",
                               commercial_id=self.u_com.id)
        self.client_b = Client(full_name="B", email="b@x",
                               commercial_id=self.u_ges.id)
        self.session.add_all([self.client_a, self.client_b])
        self.session.commit()

        # ---------- contrat signé ----------
        self.ctr_signed = Contract(client_id=self.client_a.id,
                                   commercial_id=self.u_com.id,
                                   total_amount=100, remaining_amount=0,
                                   is_signed=True)
        self.session.add(self.ctr_signed)
        self.session.commit()

        # ---------- événement ----------
        self.ev_other = Event(contract_id=self.ctr_signed.id,
                              support_id=self.u_sup.id,
                              date_start=datetime.utcnow(),
                              date_end=None,
                              location="", attendees=1, notes="")
        self.session.add(self.ev_other)
        self.session.commit()

        # contrôleurs
        self.writer = DataWriter(self.db_conn)
        self.reader = DataReader(self.db_conn)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    # ---------------------- DataReader ---------------------- #
    def test_reader_clients_filter_by_commercial(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_clients(
            sess,
            {"id": self.u_com.id, "role": "commercial", "force_filter": True}
        )
        self.assertTrue(all(c.commercial_id == self.u_com.id for c in lst))
        sess.close()

    def test_reader_clients_support_gets_all(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_clients(
            sess, {"id": self.u_sup.id, "role": "support"})
        self.assertEqual(len(lst), 2)      # plus de restriction
        sess.close()

    def test_reader_contracts_support_gets_all(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_contracts(
            sess, {"id": self.u_sup.id, "role": "support"})
        self.assertGreaterEqual(len(lst), 1)
        sess.close()

    # ---------------------- DataWriter ---------------------- #
    def test_support_update_own_event(self):
        sess = self.db_conn.create_session()
        updated = self.writer.update_event(
            sess,
            {"id": self.u_sup.id, "role": "support"},
            self.ev_other.id,
            notes="ok"
        )
        self.assertEqual(updated.notes, "ok")
        sess.close()
