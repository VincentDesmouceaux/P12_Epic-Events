# tests/testunitaire/test_gestion_team.py
import unittest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.role import Role
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController


class DummyDBConnection:
    def __init__(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return self.SessionLocal()


class GestionTeamTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db_conn = DummyDBConnection()
        self.session = self.db_conn.create_session()
        # Insertion du rôle gestion
        self.role_gestion = Role(
            name="gestion", description="Équipe de gestion")
        self.session.add(self.role_gestion)
        self.session.commit()
        self.data_writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()
        self.current_user = {"id": 999, "role": "gestion"}

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_auto_employee_number(self):
        """
        Vérifie l'auto-génération du numéro d'employé pour un collaborateur de gestion.
        """
        user1 = self.data_writer.create_user(
            self.session,
            self.current_user,
            first_name="Alice",
            last_name="Gestion",
            email="alice.gestion@test.com",
            password_hash=self.auth_controller.hasher.hash("Secret1"),
            role_id=self.role_gestion.id,
            employee_number=None
        )
        self.assertTrue(user1.employee_number.startswith("G"))
        self.assertEqual(user1.employee_number, "G001")

        user2 = self.data_writer.create_user(
            self.session,
            self.current_user,
            first_name="Betty",
            last_name="Gestion",
            email="betty.gestion@test.com",
            password_hash=self.auth_controller.hasher.hash("Secret2"),
            role_id=self.role_gestion.id,
            employee_number=None
        )
        self.assertEqual(user2.employee_number, "G002")

    def test_update_user_by_employee_number(self):
        """
        Vérifie la mise à jour d'un collaborateur identifié par son employee_number.
        """
        user = self.data_writer.create_user(
            self.session,
            self.current_user,
            first_name="Charlie",
            last_name="Gestion",
            email="charlie.gestion@test.com",
            password_hash=self.auth_controller.hasher.hash("Secret3"),
            role_id=self.role_gestion.id,
            employee_number=None
        )
        emp_num = user.employee_number
        updated = self.data_writer.update_user_by_employee_number(
            self.session,
            self.current_user,
            emp_num,
            first_name="Charles"
        )
        self.assertEqual(updated.first_name, "Charles")

    def test_delete_user(self):
        """
        Vérifie la suppression d'un collaborateur par employee_number.
        """
        user = self.data_writer.create_user(
            self.session,
            self.current_user,
            first_name="Diane",
            last_name="Gestion",
            email="diane.gestion@test.com",
            password_hash=self.auth_controller.hasher.hash("Secret4"),
            role_id=self.role_gestion.id,
            employee_number=None
        )
        emp_num = user.employee_number
        result = self.data_writer.delete_user(
            self.session, self.current_user, emp_num)
        self.assertTrue(result)
        user_check = self.session.query(user.__class__).filter_by(
            employee_number=emp_num).first()
        self.assertIsNone(user_check)


if __name__ == '__main__':
    unittest.main()
