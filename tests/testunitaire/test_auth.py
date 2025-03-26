import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importer Base pour enregistrer les modèles dans le metadata
from app.models import Base
from app.models.role import Role
from app.models.user import User
from app.authentification.auth_controller import AuthController
from app.config.database import DatabaseConfig, DatabaseConnection


class TestAuthController(unittest.TestCase):
    """
    Tests unitaires pour AuthController, vérifiant l'enregistrement et l'authentification.
    """

    def setUp(self):
        # Crée une base de données SQLite en mémoire pour les tests
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        # Importer explicitement les modèles pour que leurs tables soient enregistrées
        from app.models.role import Role
        from app.models.user import User
        # Créer toutes les tables
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Insérer un rôle de test (ex: "commercial")
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
        # Enregistrer un utilisateur avec le rôle inséré
        new_user = self.auth_controller.register_user(
            session=self.session,
            employee_number="EMP100",
            first_name="Alice",
            last_name="Dupont",
            email="alice.dupont@example.com",
            password="SuperSecret123",
            role_id=self.test_role.id
        )

        # Vérifier que l'utilisateur est créé
        queried = self.session.query(User).filter_by(
            email="alice.dupont@example.com").first()
        self.assertIsNotNone(
            queried, "L'utilisateur doit être créé et récupéré.")

        # Test de l'authentification réussie avec le bon mot de passe
        auth_user = self.auth_controller.authenticate_user(
            session=self.session,
            email="alice.dupont@example.com",
            password="SuperSecret123"
        )
        self.assertIsNotNone(
            auth_user, "L'authentification doit réussir avec le bon mot de passe.")
        self.assertEqual(auth_user.first_name, "Alice")

        # Test de l'authentification échouée avec un mauvais mot de passe
        failed_user = self.auth_controller.authenticate_user(
            session=self.session,
            email="alice.dupont@example.com",
            password="WrongPassword"
        )
        self.assertIsNone(
            failed_user, "L'authentification doit échouer avec un mot de passe incorrect.")


if __name__ == '__main__':
    unittest.main()
