# app/views/data_writer_view.py

from app.controllers.data_writer import DataWriter
from datetime import datetime
from app.views.generic_view import GenericView


class DataWriterView(GenericView):
    """
    Vue pour la création et la mise à jour des données dans l'application CRM.
    Encapsule l'utilisation du contrôleur DataWriter.
    """

    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.writer = DataWriter(self.db_conn)

    def run(self):
        """
        Version interactive : simule les opérations (création et mise à jour) d'un collaborateur,
        d'un contrat et d'un événement par un utilisateur "gestion".
        """
        session = self.db_conn.create_session()
        current_user = {"id": 1, "role": "gestion"}

        self.print_header("\n[DEBUG] DataWriterView.run() - START")
        self.print_yellow("[DEBUG] current_user = " + str(current_user))

        try:
            new_user = self.writer.create_user(
                session,
                current_user,
                employee_number="EMP123",
                first_name="Jean",
                last_name="Dupont",
                email="jean.dupont@example.com",
                password_hash="hashed_value",  # En production, ce doit être un mot de passe haché
                role_id=2
            )
            self.print_green("[DEBUG] new_user = " + str(new_user))
            if new_user:
                self.print_green("[DEBUG] new_user.id = " + str(new_user.id))
        except Exception as e:
            self.print_red("[DEBUG] Exception creating user: " + str(e))
            session.rollback()

        if new_user:
            try:
                updated_user = self.writer.update_user(
                    session,
                    current_user,
                    new_user.id,
                    first_name="Jean-Pierre",
                    email="jp.dupont@example.com"
                )
                self.print_green(
                    "[DEBUG] updated_user.first_name = " + updated_user.first_name)
                self.print_green(
                    "[DEBUG] updated_user.email = " + updated_user.email)
            except Exception as e:
                self.print_red("[DEBUG] Exception updating user: " + str(e))
                session.rollback()

        try:
            new_contract = self.writer.create_contract(
                session,
                current_user,
                client_id=1,  # Exemple d'ID client
                commercial_id=new_user.id,
                total_amount=10000.0,
                remaining_amount=5000.0,
                is_signed=True
            )
            self.print_green("[DEBUG] new_contract.id = " +
                             (str(new_contract.id) if new_contract else "None"))
        except Exception as e:
            self.print_red("[DEBUG] Exception creating contract: " + str(e))
            session.rollback()

        if new_contract:
            try:
                updated_contract = self.writer.update_contract(
                    session,
                    current_user,
                    new_contract.id,
                    remaining_amount=0.0,
                    is_signed=True
                )
                self.print_green(
                    "[DEBUG] updated_contract.remaining_amount = " + str(updated_contract.remaining_amount))
            except Exception as e:
                self.print_red(
                    "[DEBUG] Exception updating contract: " + str(e))
                session.rollback()

        try:
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
            self.print_green("[DEBUG] new_event.id = " +
                             (str(new_event.id) if new_event else "None"))
        except Exception as e:
            self.print_red("[DEBUG] Exception creating event: " + str(e))
            session.rollback()

        if new_event:
            try:
                updated_event = self.writer.update_event(
                    session,
                    current_user,
                    new_event.id,
                    attendees=80,
                    notes="Updated notes for the event."
                )
                self.print_green(
                    "[DEBUG] updated_event.attendees = " + str(updated_event.attendees))
                self.print_green(
                    "[DEBUG] updated_event.notes = " + updated_event.notes)
            except Exception as e:
                self.print_red("[DEBUG] Exception updating event: " + str(e))
                session.rollback()

        session.close()
        self.print_header("[DEBUG] DataWriterView.run() - END\n")

    def create_user_cli(self, current_user, empnum, fname, lname, email, password_hash, role_id):
        session = self.db_conn.create_session()
        try:
            user = self.writer.create_user(
                session,
                current_user,
                employee_number=empnum,
                first_name=fname,
                last_name=lname,
                email=email,
                password_hash=password_hash,
                role_id=role_id
            )
            self.print_green(
                f"Utilisateur créé : ID={user.id if user else 'None'}")
        except Exception as e:
            self.print_red(f"Erreur: {e}")
            session.rollback()
        finally:
            session.close()

    def update_user_cli(self, current_user, user_id, **updates):
        session = self.db_conn.create_session()
        try:
            updated = self.writer.update_user(
                session,
                current_user,
                user_id,
                **updates
            )
            self.print_green(f"Utilisateur {updated.id} mis à jour.")
        except Exception as e:
            self.print_red(f"Erreur: {e}")
            session.rollback()
        finally:
            session.close()
