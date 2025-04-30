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


# ----------------------------------------------------------------------------- #
#                         Infrastructure de base de test                        #
# ----------------------------------------------------------------------------- #
class DummyDBConnection:
    """Fournit simplement la méthode create_session attendue par les controllers"""

    def __init__(self, session_factory):
        self.SessionLocal = session_factory

    def create_session(self):
        return self.SessionLocal()


# ----------------------------------------------------------------------------- #
#                              Cas de test principaux                           #
# ----------------------------------------------------------------------------- #
class PermissionsTestCase(unittest.TestCase):
    def setUp(self):
        # ----------------------------- Base en mémoire ----------------------------- #
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_conn = DummyDBConnection(Session)
        self.session = self.db_conn.create_session()

        # ---------------------------------- Rôles ---------------------------------- #
        self.r_com = Role(id=1, name="commercial", description="")
        self.r_sup = Role(id=2, name="support", description="")
        self.r_ges = Role(id=3, name="gestion",  description="")
        self.session.add_all([self.r_com, self.r_sup, self.r_ges])
        self.session.commit()

        # ------------------------------ Utilisateurs ------------------------------ #
        self.u_com = User(employee_number="C001", first_name="Com", last_name="U",
                          email="com@x", password_hash="h", role_id=1)
        self.u_sup = User(employee_number="S001", first_name="Sup", last_name="U",
                          email="sup@x", password_hash="h", role_id=2)
        self.u_ges = User(employee_number="G001", first_name="Ges", last_name="U",
                          email="ges@x", password_hash="h", role_id=3)
        self.session.add_all([self.u_com, self.u_sup, self.u_ges])
        self.session.commit()

        # --------------------------------- Clients -------------------------------- #
        self.client_a = Client(full_name="A", email="a@x", phone="",
                               company_name="", commercial_id=self.u_com.id)
        self.client_b = Client(full_name="B", email="b@x", phone="",
                               company_name="", commercial_id=self.u_ges.id)
        self.session.add_all([self.client_a, self.client_b])
        self.session.commit()

        # -------------------------------- Contrats -------------------------------- #
        self.ctr_unsigned = Contract(client_id=self.client_a.id,
                                     commercial_id=self.u_com.id,
                                     total_amount=100, remaining_amount=100,
                                     is_signed=False)
        self.ctr_signed = Contract(client_id=self.client_a.id,
                                   commercial_id=self.u_com.id,
                                   total_amount=200, remaining_amount=200,
                                   is_signed=True)
        self.session.add_all([self.ctr_unsigned, self.ctr_signed])
        self.session.commit()

        # ------------------------------- Événement -------------------------------- #
        self.ev_other = Event(contract_id=self.ctr_signed.id,
                              support_id=self.u_sup.id,
                              date_start=datetime.utcnow(),
                              date_end=None,
                              location="", attendees=0, notes="")
        self.session.add(self.ev_other)
        self.session.commit()

        # --------------------------- Controllers testés --------------------------- #
        self.writer = DataWriter(self.db_conn)
        self.reader = DataReader(self.db_conn)

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    # ------------------------------------------------------------------------- #
    #                        Tests DataWriter.create_client                     #
    # ------------------------------------------------------------------------- #
    def test_commercial_create_client_auto_associe(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_com.id, "role": "commercial"}
        new = self.writer.create_client(
            sess, current, "New Cl", "new@x", "123", "Co", None)
        self.assertEqual(new.commercial_id, self.u_com.id)
        sess.close()

    def test_support_cannot_create_client(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_sup.id, "role": "support"}
        with self.assertRaises(Exception):
            self.writer.create_client(sess, current, "X", "x@x", "", "", None)
        sess.close()

    # ------------------------------------------------------------------------- #
    #                        Tests DataWriter.update_client                     #
    # ------------------------------------------------------------------------- #
    def test_commercial_update_own_client(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_com.id, "role": "commercial"}
        updated = self.writer.update_client(
            sess, current, self.client_a.id, full_name="A2")
        self.assertEqual(updated.full_name, "A2")
        sess.close()

    def test_commercial_cannot_update_other_client(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_com.id, "role": "commercial"}
        with self.assertRaises(Exception):
            self.writer.update_client(
                sess, current, self.client_b.id, full_name="B2")
        sess.close()

    def test_gestion_update_any_client(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_ges.id, "role": "gestion"}
        updated = self.writer.update_client(
            sess, current, self.client_b.id, full_name="B2")
        self.assertEqual(updated.full_name, "B2")
        sess.close()

    # ------------------------------------------------------------------------- #
    #                         Tests DataWriter.create_event                    #
    # ------------------------------------------------------------------------- #
    def test_commercial_cannot_create_event_if_not_signed(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_com.id, "role": "commercial"}
        with self.assertRaises(Exception):
            self.writer.create_event(
                sess, current,
                contract_id=self.ctr_unsigned.id,
                support_id=None,
                date_start=datetime.utcnow(),
                date_end=None,
                location="", attendees=0, notes=""
            )
        sess.close()

    def test_commercial_create_event_on_signed(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_com.id, "role": "commercial"}
        ev = self.writer.create_event(
            sess, current,
            contract_id=self.ctr_signed.id,
            support_id=None,
            date_start=datetime.utcnow(),
            date_end=None,
            location="L", attendees=1, notes="N"
        )
        self.assertIsNotNone(ev.id)
        sess.close()

    # ------------------------------------------------------------------------- #
    #                         Tests DataWriter.update_event                    #
    # ------------------------------------------------------------------------- #
    def test_support_update_own_event(self):
        sess = self.db_conn.create_session()
        current = {"id": self.u_sup.id, "role": "support"}
        updated = self.writer.update_event(
            sess, current, self.ev_other.id, notes="X")
        self.assertEqual(updated.notes, "X")
        sess.close()

    def test_support_cannot_update_others_event(self):
        sess = self.db_conn.create_session()
        ev2 = Event(contract_id=self.ctr_signed.id,
                    support_id=self.u_ges.id,
                    date_start=datetime.utcnow(),
                    date_end=None,
                    location="", attendees=0, notes="")
        sess.add(ev2)
        sess.commit()

        current = {"id": self.u_sup.id, "role": "support"}
        with self.assertRaises(Exception):
            self.writer.update_event(sess, current, ev2.id, notes="Y")
        sess.close()

    # ------------------------------------------------------------------------- #
    #                        Tests DataReader.get_all_clients                  #
    # ------------------------------------------------------------------------- #
    def test_reader_clients_filter_by_commercial(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_clients(
            sess, {"id": self.u_com.id, "role": "commercial"})
        self.assertTrue(all(c.commercial_id == self.u_com.id for c in lst))
        sess.close()

    def test_reader_clients_gestion_gets_all(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_clients(
            sess, {"id": self.u_ges.id, "role": "gestion"})
        self.assertEqual(len(lst), 2)
        sess.close()

    def test_reader_clients_support_forbidden(self):
        sess = self.db_conn.create_session()
        with self.assertRaises(Exception):
            self.reader.get_all_clients(
                sess, {"id": self.u_sup.id, "role": "support"})
        sess.close()

    # ------------------------------------------------------------------------- #
    #                       Tests DataReader.get_all_contracts                 #
    # ------------------------------------------------------------------------- #
    def test_reader_contracts_by_commercial(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_contracts(
            sess, {"id": self.u_com.id, "role": "commercial"})
        self.assertTrue(all(c.commercial_id == self.u_com.id for c in lst))
        sess.close()

    def test_reader_contracts_support_forbidden(self):
        sess = self.db_conn.create_session()
        with self.assertRaises(Exception):
            self.reader.get_all_contracts(
                sess, {"id": self.u_sup.id, "role": "support"})
        sess.close()

    # ------------------------------------------------------------------------- #
    #                        Tests DataReader.get_all_events                   #
    # ------------------------------------------------------------------------- #
    def test_reader_events_by_support(self):
        sess = self.db_conn.create_session()
        lst = self.reader.get_all_events(
            sess, {"id": self.u_sup.id, "role": "support"})
        self.assertTrue(all(e.support_id == self.u_sup.id for e in lst))
        sess.close()

    def test_reader_events_commercial_sees_their(self):
        sess = self.db_conn.create_session()
        # Ajout d'un événement supplémentaire lié au commercial
        ev = Event(contract_id=self.ctr_signed.id,
                   support_id=None,
                   date_start=datetime.utcnow(),
                   date_end=None,
                   location="", attendees=0, notes="")
        sess.add(ev)
        sess.commit()

        lst = self.reader.get_all_events(
            sess, {"id": self.u_com.id, "role": "commercial"})
        self.assertTrue(all(e.contract.commercial_id ==
                        self.u_com.id for e in lst))
        sess.close()

    def test_reader_events_gestion_sees_all(self):
        sess = self.db_conn.create_session()

        # ------- Ajout explicite d'un second événement -------
        extra_event = Event(
            contract_id=self.ctr_signed.id,
            support_id=None,
            date_start=datetime.utcnow(),
            date_end=None,
            location="",
            attendees=0,
            notes="extra",
        )
        sess.add(extra_event)
        sess.commit()
        # ------------------------------------------------------

        lst = self.reader.get_all_events(
            sess, {"id": self.u_ges.id, "role": "gestion"})
        # ev_other (créé dans setUp) + extra_event
        self.assertEqual(len(lst), 2)
        sess.close()


# ----------------------------------------------------------------------------- #
#                                Point d'entrée                                 #
# ----------------------------------------------------------------------------- #
if __name__ == "__main__":
    unittest.main()
