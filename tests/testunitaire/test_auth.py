# tests/testunitaire/test_auth.py
"""Tests unitaires du contrôleur d’authentification.

Objectifs :
    • Vérifier l’enregistrement et l’authentification d’un utilisateur.
    • Tester la génération, la vérification et l’expiration d’un JWT.
    • Contrôler la fonction de vérification d’autorisation par rôle.
"""
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.models.role import Role
from app.authentification.auth_controller import AuthController


class TestAuthController(unittest.TestCase):
    """Suite de tests pour le module :class:`AuthController`."""

    # --------------------------------------------------------------------- #
    # Cycle de vie de la base de tests
    # --------------------------------------------------------------------- #
    def setUp(self) -> None:
        """Crée une base SQLite en mémoire et prépare un rôle de test."""
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.test_role = Role(name="commercial", description="Test role")
        self.session.add(self.test_role)
        self.session.commit()

        self.auth_controller = AuthController()

    def tearDown(self) -> None:
        """Ferme la session et détruit la base en mémoire."""
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    # --------------------------------------------------------------------- #
    # Cas : création + authentification
    # --------------------------------------------------------------------- #
    def test_register_and_authenticate_user(self) -> None:
        """Un utilisateur peut être enregistré puis authentifié."""
        new_user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP100",
            first_name="Alice",
            last_name="Dupont",
            email="alice.dupont@example.com",
            password="SuperSecret123",
            role_id=self.test_role.id,
        )
        self.assertIsNotNone(new_user)

        auth_user = self.auth_controller.authenticate_user(
            self.session,
            email="alice.dupont@example.com",
            password="SuperSecret123",
        )
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.first_name, "Alice")

        failed_user = self.auth_controller.authenticate_user(
            self.session,
            email="alice.dupont@example.com",
            password="WrongPassword",
        )
        self.assertIsNone(failed_user)

    # --------------------------------------------------------------------- #
    # Cas : génération et vérification d’un token
    # --------------------------------------------------------------------- #
    def test_generate_and_verify_token(self) -> None:
        """Le token JWT contient l’ID utilisateur et son rôle."""
        user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP101",
            first_name="Bob",
            last_name="Martin",
            email="bob.martin@example.com",
            password="SecretBob",
            role_id=self.test_role.id,
        )
        token = self.auth_controller.generate_token(user)
        self.assertIsInstance(token, str)

        payload = self.auth_controller.verify_token(token)
        self.assertEqual(payload["user_id"], user.id)
        self.assertEqual(payload["role"], user.role.name)

    # --------------------------------------------------------------------- #
    # Cas : vérification d’autorisation
    # --------------------------------------------------------------------- #
    def test_is_authorized(self) -> None:
        """`is_authorized` renvoie True/False selon le rôle demandé."""
        user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP102",
            first_name="Carol",
            last_name="Dupont",
            email="carol.dupont@example.com",
            password="SecretCarol",
            role_id=self.test_role.id,
        )
        token = self.auth_controller.generate_token(user)
        self.assertTrue(
            self.auth_controller.is_authorized(token, "commercial"))
        self.assertFalse(self.auth_controller.is_authorized(token, "support"))

    # --------------------------------------------------------------------- #
    # Cas : token expiré
    # --------------------------------------------------------------------- #
    def test_verify_expired_token(self) -> None:
        """Un token expiré lève une exception avec un message explicite."""
        self.auth_controller.jwt_expiration_minutes = -1  # token déjà expiré
        user = self.auth_controller.register_user(
            self.session,
            employee_number="EMP103",
            first_name="Dave",
            last_name="Smith",
            email="dave.smith@example.com",
            password="SecretDave",
            role_id=self.test_role.id,
        )
        token = self.auth_controller.generate_token(user)
        with self.assertRaises(Exception) as ctx:
            self.auth_controller.verify_token(token)
        self.assertIn("Le jeton est expiré", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
