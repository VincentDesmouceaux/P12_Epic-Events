from app.config.database import DatabaseConfig, DatabaseConnection
from app.controllers.data_writer import DataWriter
from datetime import datetime


class DataWriterView:
    """
    Vue pour la création et la mise à jour des données dans l'application CRM.
    Encapsule l'utilisation du contrôleur DataWriter.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.writer = DataWriter(self.db_conn)

    def run(self):
        session = self.db_conn.create_session()

        # Simuler un utilisateur authentifié avec le rôle "gestion"
        current_user = {"id": 1, "role": "gestion"}

        # Créer un collaborateur
        new_user = self.writer.create_user(
            session,
            current_user,
            employee_number="EMP123",
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            password_hash="hashed_value",  # En production, hachez le mot de passe
            role_id=2  # Par exemple, l'ID du rôle "commercial"
        )

        # Mettre à jour ce collaborateur
        updated_user = self.writer.update_user(
            session,
            current_user,
            new_user.id,
            first_name="Jean-Pierre",
            email="jp.dupont@example.com"
        )

        # Créer un contrat
        new_contract = self.writer.create_contract(
            session,
            current_user,
            client_id=1,           # Exemple d'ID client
            commercial_id=new_user.id,
            total_amount=10000.0,
            remaining_amount=5000.0,
            is_signed=True
        )

        # Mettre à jour le contrat
        updated_contract = self.writer.update_contract(
            session,
            current_user,
            new_contract.id,
            remaining_amount=0.0,
            is_signed=True
        )

        # Créer un événement
        new_event = self.writer.create_event(
            session,
            current_user,
            contract_id=new_contract.id,
            support_id=3,  # Exemple d'ID pour un support
            date_start=datetime(2023, 6, 4, 13, 0),
            date_end=datetime(2023, 6, 5, 2, 0),
            location="53 Rue du Château, 41120 Candé-sur-Beuvron, France",
            attendees=75,
            notes="Wedding starts at 3PM, by the river."
        )

        # Mettre à jour l'événement
        updated_event = self.writer.update_event(
            session,
            current_user,
            new_event.id,
            attendees=80,
            notes="Updated notes for the event."
        )

        session.close()


def main():
    db_config = DatabaseConfig()
    db_conn = DatabaseConnection(db_config)
    view = DataWriterView(db_conn)
    view.run()


if __name__ == "__main__":
    main()
