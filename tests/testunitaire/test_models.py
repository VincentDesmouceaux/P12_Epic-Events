import unittest
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import de la Base partagée par tous les modèles
from app.models import Base
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class TestModels(unittest.TestCase):
    """
    Tests unitaires pour vérifier la création et les relations
    des modèles : User, Client, Contract et Event.
    """

    def setUp(self):
        """
        Création d'une base de données SQLite en mémoire,
        création des tables et ouverture d'une session.
        """
        # Utilisation d'une DB en mémoire pour les tests
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        # Création de toutes les tables définies dans Base.metadata
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """
        Fermeture de la session et suppression des tables.
        """
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def test_create_user(self):
        """
        Teste la création d'un utilisateur et sa récupération.
        """
        user = User(username="john_doe",
                    password_hash="hashed_password", role="commercial")
        self.session.add(user)
        self.session.commit()

        queried = self.session.query(User).filter_by(
            username="john_doe").first()
        self.assertIsNotNone(
            queried, "L'utilisateur doit être créé et récupéré.")
        self.assertEqual(queried.role, "commercial",
                         "Le rôle doit être 'commercial'.")

    def test_create_client(self):
        """
        Teste la création d'un client associé à un commercial.
        """
        # Création d'un utilisateur commercial
        commercial = User(username="commercial1",
                          password_hash="hashed", role="commercial")
        self.session.add(commercial)
        self.session.commit()

        # Création d'un client lié au commercial
        client = Client(
            full_name="Kevin Casey",
            email="kevin@startup.io",
            phone="+67812345678",
            company_name="Cool Startup LLC",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()

        queried_client = self.session.query(Client).filter_by(
            email="kevin@startup.io").first()
        self.assertIsNotNone(
            queried_client, "Le client doit être créé et récupéré.")
        # Vérification de la relation : client.commercial doit être le commercial créé
        self.assertEqual(queried_client.commercial.username, "commercial1")

    def test_create_contract(self):
        """
        Teste la création d'un contrat associé à un client et un commercial.
        """
        commercial = User(username="commercial2",
                          password_hash="hashed", role="commercial")
        self.session.add(commercial)
        self.session.commit()

        client = Client(
            full_name="Jane Doe",
            email="jane@example.com",
            company_name="Acme Corp",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()

        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=10000.0,
            remaining_amount=5000.0,
            is_signed=True
        )
        self.session.add(contract)
        self.session.commit()

        queried_contract = self.session.query(
            Contract).filter_by(client_id=client.id).first()
        self.assertIsNotNone(
            queried_contract, "Le contrat doit être créé et récupéré.")
        self.assertTrue(queried_contract.is_signed,
                        "Le contrat doit être signé.")
        self.assertEqual(queried_contract.total_amount, 10000.0)

    def test_create_event(self):
        """
        Teste la création d'un événement lié à un contrat et attribué à un support.
        """
        # Création d'un utilisateur commercial et d'un support
        commercial = User(username="commercial3",
                          password_hash="hashed", role="commercial")
        support = User(username="support1",
                       password_hash="hashed", role="support")
        self.session.add_all([commercial, support])
        self.session.commit()

        client = Client(
            full_name="John Smith",
            email="john.smith@example.com",
            company_name="Smith Inc.",
            commercial_id=commercial.id
        )
        self.session.add(client)
        self.session.commit()

        contract = Contract(
            client_id=client.id,
            commercial_id=commercial.id,
            total_amount=15000.0,
            remaining_amount=0.0,
            is_signed=True
        )
        self.session.add(contract)
        self.session.commit()

        event = Event(
            contract_id=contract.id,
            support_id=support.id,
            date_start=datetime(2023, 6, 4, 13, 0),
            date_end=datetime(2023, 6, 5, 2, 0),
            location="53 Rue du Château, Candé-sur-Beuvron, France",
            attendees=75,
            notes="Wedding starts at 3PM, by the river."
        )
        self.session.add(event)
        self.session.commit()

        queried_event = self.session.query(Event).filter_by(
            contract_id=contract.id).first()
        self.assertIsNotNone(
            queried_event, "L'événement doit être créé et récupéré.")
        self.assertEqual(queried_event.support.username, "support1",
                         "Le support associé doit être 'support1'.")
        self.assertEqual(queried_event.location,
                         "53 Rue du Château, Candé-sur-Beuvron, France")


if __name__ == '__main__':
    unittest.main()
