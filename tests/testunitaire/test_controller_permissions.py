"""
Tests permissions & filtres (DataReader / DataWriter).

On crée trois rôles, trois utilisateurs, un client, un contrat signé
et un événement ; puis on vérifie :

    • les filtres DataReader pour un commercial,
    • l’accès complet pour le support,
    • la capacité du support à modifier son propre événement.
"""

from __future__ import annotations

import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Role, User, Client, Contract, Event
from app.controllers.data_writer import DataWriter
from app.controllers.data_reader import DataReader


class _DummyDB:
    """Connex‑wrapper très simple autour d’un factory SQLAlchemy."""

    def __init__(self, session_factory):
        self.Session = session_factory

    def create_session(self):
        return self.Session()


class PermissionsTestCase(unittest.TestCase):
    """Regroupe les tests liés aux droits d’accès."""

    # ---------------------------------------------------------------- #
    # setUp / tearDown
    # ---------------------------------------------------------------- #
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.db = _DummyDB(Session)
        self.session = self.db.create_session()

        # Rôles
        self.r_com = Role(id=1, name="commercial")
        self.r_sup = Role(id=2, name="support")
        self.r_ges = Role(id=3, name="gestion")
        self.session.add_all([self.r_com, self.r_sup, self.r_ges])
        self.session.commit()

        # Utilisateurs
        self.u_com = User(employee_number="C001", first_name="Com", last_name="U",
                          email="c@x", password_hash="h", role_id=1)
        self.u_sup = User(employee_number="S001", first_name="Sup", last_name="U",
                          email="s@x", password_hash="h", role_id=2)
        self.u_ges = User(employee_number="G001", first_name="Ges", last_name="U",
                          email="g@x", password_hash="h", role_id=3)
        self.session.add_all([self.u_com, self.u_sup, self.u_ges])
        self.session.commit()

        # Client + contrat signé
        client = Client(full_name="A", email="a@x",
                        commercial_id=self.u_com.id)
        self.session.add(client)
        self.session.commit()
        ctr = Contract(client_id=client.id,
                       commercial_id=self.u_com.id,
                       total_amount=100,
                       remaining_amount=0,
                       is_signed=True)
        self.session.add(ctr)
        self.session.commit()

        # Événement affecté au support
        ev = Event(contract_id=ctr.id, support_id=self.u_sup.id,
                   date_start=datetime.utcnow(), date_end=None,
                   location="", attendees=1, notes="")
        self.session.add(ev)
        self.session.commit()

        # Contrôleurs
        self.reader = DataReader(self.db)
        self.writer = DataWriter(self.db)

    def tearDown(self) -> None:
        self.session.close()
        Base.metadata.drop_all(bind=self.session.get_bind())

    # ---------------------------------------------------------------- #
    # tests DataReader
    # ---------------------------------------------------------------- #
    def test_reader_filter_by_commercial(self) -> None:
        sess = self.db.create_session()
        result = self.reader.get_all_clients(
            sess,
            {"id": self.u_com.id, "role": "commercial", "force_filter": True},
        )
        self.assertTrue(all(c.commercial_id == self.u_com.id for c in result))
        sess.close()

    def test_reader_support_gets_all(self) -> None:
        sess = self.db.create_session()
        result = self.reader.get_all_clients(
            sess, {"id": self.u_sup.id, "role": "support"}
        )
        self.assertEqual(len(result), 1)
        sess.close()

    # ---------------------------------------------------------------- #
    # tests DataWriter
    # ---------------------------------------------------------------- #
    def test_support_can_update_own_event(self) -> None:
        sess = self.db.create_session()
        ev = sess.query(Event).first()
        updated = self.writer.update_event(
            sess,
            {"id": self.u_sup.id, "role": "support"},
            ev.id,
            notes="OK",
        )
        self.assertEqual(updated.notes, "OK")
        sess.close()


if __name__ == "__main__":
    unittest.main()
