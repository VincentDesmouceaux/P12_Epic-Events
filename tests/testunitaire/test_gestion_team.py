# tests/testunitaire/test_gestion_team.py
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.models.role import Role
from app.models.user import User
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
        # Création des rôles : commercial (ID=1) et gestion (ID=3)
        self.role_commercial = Role(
            id=1, name="commercial", description="Département commercial")
        self.role_gestion = Role(id=3, name="gestion",
                                 description="Équipe de gestion")
        self.session.add_all([self.role_commercial, self.role_gestion])
        self.session.commit()
        self.data_writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()
        self.current_user = {"id": 999, "role": "gestion", "role_id": 3}

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_auto_employee_number_for_commercial(self):
        """
        Pour un collaborateur commercial (role_id=1), le numéro doit être auto-généré avec préfixe "C".
        """
        current_user = {"id": 999, "role": "gestion", "role_id": 3}
        # Créer le premier collaborateur commercial
        user1 = self.data_writer.create_user(
            self.session,
            current_user,
            employee_number=None,
            first_name="Test",
            last_name="Commercial1",
            email="comm1@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=1
        )
        self.assertEqual(user1.employee_number, "C001")
        # Créer le second collaborateur commercial
        user2 = self.data_writer.create_user(
            self.session,
            current_user,
            employee_number=None,
            first_name="Test",
            last_name="Commercial2",
            email="comm2@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=1
        )
        self.assertEqual(user2.employee_number, "C002")

    def test_update_user_by_employee_number(self):
        """
        Vérifie que la mise à jour par employee_number fonctionne.
        """
        user = self.data_writer.create_user(
            self.session,
            self.current_user,
            employee_number=None,
            first_name="Initial",
            last_name="Gestion",
            email="gestion@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=3
        )
        emp_num = user.employee_number
        updated = self.data_writer.update_user_by_employee_number(
            self.session,
            self.current_user,
            emp_num,
            first_name="UpdatedName"
        )
        self.assertEqual(updated.first_name, "UpdatedName")

    def test_delete_user_by_employee_number(self):
        """
        Vérifie la suppression d'un collaborateur via son employee_number.
        """
        user = self.data_writer.create_user(
            self.session,
            self.current_user,
            employee_number=None,
            first_name="ToDelete",
            last_name="User",
            email="delete@test.com",
            password_hash=self.auth_controller.hasher.hash("pass"),
            role_id=3
        )
        emp_num = user.employee_number
        result = self.data_writer.delete_user(
            self.session, self.current_user, emp_num)
        self.assertTrue(result)
        user_check = self.session.query(User).filter_by(
            employee_number=emp_num).first()
        self.assertIsNone(user_check)


if __name__ == '__main__':
    unittest.main()
