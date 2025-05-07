# tests/testunitaire/test_gestion_team.py
# -*- coding: utf-8 -*-
"""
Suite de tests « équipe gestion ».

Couverture :
    • génération automatique du matricule collaborateur ;
    • mise à jour par `employee_number` ;
    • suppression d’un collaborateur par `employee_number`.
"""

import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


class DummyDBConnection:
    """Connexion BD in‑memory destinée aux tests."""

    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        """Renvoie une nouvelle session pour la base temporaire."""
        return self.SessionLocal()


class GestionTeamTestCase(unittest.TestCase):
    """Tests ciblant les fonctionnalités réservées au rôle *gestion*."""

    # ------------------------------------------------------------------ #
    # SET‑UP / TEAR‑DOWN                                                 #
    # ------------------------------------------------------------------ #
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.db_conn = DummyDBConnection()
        self.session = self.db_conn.create_session()

        self.role_commercial = Role(
            id=1, name="commercial", description="Département commercial"
        )
        self.role_gestion = Role(id=3, name="gestion",
                                 description="Équipe gestion")
        self.session.add_all([self.role_commercial, self.role_gestion])
        self.session.commit()

        self.data_writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    # ------------------------------------------------------------------ #
    # TESTS                                                              #
    # ------------------------------------------------------------------ #
    def test_auto_employee_number_for_commercial(self):
        """Le matricule auto‑généré pour un commercial doit commencer par `C`."""
        user1 = self.data_writer.create_user(
            self.session,
            self.current_user,
            employee_number=None,
            first_name="Test",
            last_name="Commercial1",
            email="comm1@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=1,
        )
        self.assertEqual(user1.employee_number, "C001")

        user2 = self.data_writer.create_user(
            self.session,
            self.current_user,
            employee_number=None,
            first_name="Test",
            last_name="Commercial2",
            email="comm2@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=1,
        )
        self.assertEqual(user2.employee_number, "C002")

    def test_update_user_by_employee_number(self):
        """La mise à jour par matricule doit modifier l’utilisateur ciblé."""
        user = self.data_writer.create_user(
            self.session,
            self.current_user,
            employee_number=None,
            first_name="Initial",
            last_name="Gestion",
            email="gestion@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=3,
        )
        updated = self.data_writer.update_user_by_employee_number(
            self.session,
            self.current_user,
            user.employee_number,
            first_name="UpdatedName",
        )
        self.assertEqual(updated.first_name, "UpdatedName")

    def test_delete_user_by_employee_number(self):
        """La suppression par matricule doit retirer l’utilisateur de la BD."""
        user = self.data_writer.create_user(
            self.session,
            self.current_user,
            employee_number=None,
            first_name="ToDelete",
            last_name="User",
            email="delete@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=3,
        )
        result = self.data_writer.delete_user(
            self.session, self.current_user, user.employee_number
        )
        self.assertTrue(result)
        self.assertIsNone(
            self.session.query(User)
            .filter_by(employee_number=user.employee_number)
            .first()
        )


if __name__ == "__main__":
    unittest.main()
