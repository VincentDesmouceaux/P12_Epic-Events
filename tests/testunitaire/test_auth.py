# tests/testunitaire/test_auth.py
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.authentification.auth_controller import AuthController
from app.config.database import DatabaseConfig, DatabaseConnection


class TestAuthController(unittest.TestCase):
    """
    Tests pour AuthController : enregistrement, authentification, et gestion des tokens.
    """

    def setUp(self):
        # Création d'une base SQLite en mémoire pour les tests
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Insérer un rôle de test
        self.test_role = Role(
            name="commercial", description="Test commercial role")
        self.session.add(self.test_role)
        self.session.commit()

        # Instanciation du contrôleur d'authentification
        self.auth_controller = AuthController()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_register_and_authenticate_user(self):
        # Enregistrer un utilisateur
        new_user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP100",
            first_name="Alice",
            last_name="Dupont",
            email="alice.dupont@example.com",
            password="SuperSecret123",
            role_id=self.test_role.id
        )
        self.assertIsNotNone(new_user, "L'utilisateur doit être créé.")

        # Authentifier avec le bon mot de passe
        auth_user = self.auth_controller.authenticate_user(
            self.session,
            email="alice.dupont@example.com",
            password="SuperSecret123"
        )
        self.assertIsNotNone(
            auth_user, "L'authentification doit réussir avec le bon mot de passe.")
        self.assertEqual(auth_user.first_name, "Alice")

        # Authentifier avec un mauvais mot de passe
        failed_user = self.auth_controller.authenticate_user(
            self.session,
            email="alice.dupont@example.com",
            password="WrongPassword"
        )
        self.assertIsNone(
            failed_user, "L'authentification doit échouer avec un mauvais mot de passe.")

    def test_generate_and_verify_token(self):
        # Enregistrer un utilisateur pour générer un token
        user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP101",
            first_name="Bob",
            last_name="Martin",
            email="bob.martin@example.com",
            password="SecretBob",
            role_id=self.test_role.id
        )
        token = self.auth_controller.generate_token(user)
        self.assertIsInstance(token, str, "Le token doit être une chaîne.")

        # Vérifier le token généré
        payload = self.auth_controller.verify_token(token)
        self.assertEqual(payload["user_id"], user.id)
        self.assertEqual(payload["role"], user.role.name)

    def test_is_authorized(self):
        # Enregistrer un utilisateur et générer un token
        user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP102",
            first_name="Carol",
            last_name="Dupont",
            email="carol.dupont@example.com",
            password="SecretCarol",
            role_id=self.test_role.id
        )
        token = self.auth_controller.generate_token(user)
        # Tester avec le rôle autorisé
        self.assertTrue(
            self.auth_controller.is_authorized(token, "commercial"))
        # Tester avec un rôle non autorisé
        self.assertFalse(self.auth_controller.is_authorized(token, "support"))

    def test_verify_expired_token(self):
        # Pour tester un token expiré, on peut générer un token avec une expiration très courte.
        self.auth_controller.jwt_expiration_minutes = -1  # expiration passée
        user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP103",
            first_name="Dave",
            last_name="Smith",
            email="dave.smith@example.com",
            password="SecretDave",
            role_id=self.test_role.id
        )
        token = self.auth_controller.generate_token(user)
        with self.assertRaises(Exception) as context:
            self.auth_controller.verify_token(token)
        self.assertIn("Le jeton est expiré", str(context.exception))


if __name__ == '__main__':
    unittest.main()
