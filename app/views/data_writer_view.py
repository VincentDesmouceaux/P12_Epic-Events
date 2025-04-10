# app/views/data_writer_view.py
from app.controllers.data_writer import DataWriter
from datetime import datetime
from app.views.generic_view import GenericView
from app.authentification.auth_controller import AuthController


class DataWriterView(GenericView):
    """
    Vue pour la gestion (création, mise à jour, suppression) des données (collaborateurs, contrats, événements).
    """

    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()

    def run(self):
        session = self.db_conn.create_session()
        current_user = {"id": 1, "role": "gestion"}

        self.print_header("\n[DEBUG] DataWriterView.run() - START")
        self.print_yellow("[DEBUG] current_user = " + str(current_user))

        try:
            # Pour "gestion", on ne fournit pas de numéro d'employé pour que celui-ci soit auto-généré
            new_user = self.writer.create_user(
                session,
                current_user,
                first_name="Jean",
                last_name="Dupont",
                email="jean.dupont@example.com",
                # En production, ce sera le hash d'un mot de passe saisi
                password_hash="hashed_value",
                role_id=2,
                employee_number=None
            )
            self.print_green("[DEBUG] new_user = " + str(new_user))
            if new_user:
                self.print_green(
                    "[DEBUG] new_user.employee_number = " + new_user.employee_number)
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
                client_id=1,
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
                support_id=3,
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

    def create_user_cli(self, current_user, fname, lname, email, password, role_id):
        """
        Crée un collaborateur. Le numéro d'employé est auto-généré pour la gestion.
        Le mot de passe est saisi en clair et haché automatiquement.
        """
        session = self.db_conn.create_session()
        try:
            hashed_password = self.auth_controller.hasher.hash(password)
            user = self.writer.create_user(
                session,
                current_user,
                first_name=fname,
                last_name=lname,
                email=email,
                password_hash=hashed_password,
                role_id=role_id,
                employee_number=None  # Auto-généré
            )
            self.print_green(
                f"Collaborateur créé : Employee Number = {user.employee_number}")
        except Exception as e:
            self.print_red(f"Erreur lors de la création du collaborateur: {e}")
            session.rollback()
        finally:
            session.close()

    def update_user_cli(self, current_user, employee_number, **updates):
        """
        Met à jour un collaborateur identifié par son employee_number.
        """
        session = self.db_conn.create_session()
        try:
            updated = self.writer.update_user_by_employee_number(
                session,
                current_user,
                employee_number,
                **updates
            )
            self.print_green(
                f"Collaborateur {updated.employee_number} mis à jour.")
        except Exception as e:
            self.print_red(
                f"Erreur lors de la mise à jour du collaborateur: {e}")
            session.rollback()
        finally:
            session.close()

    def delete_user_cli(self, current_user, employee_number):
        """
        Supprime un collaborateur identifié par son employee_number.
        """
        session = self.db_conn.create_session()
        try:
            self.writer.delete_user(session, current_user, employee_number)
            self.print_green(f"Collaborateur {employee_number} supprimé.")
        except Exception as e:
            self.print_red(
                f"Erreur lors de la suppression du collaborateur: {e}")
            session.rollback()
        finally:
            session.close()

    def create_contract_cli(self, current_user, client_id, commercial_id, total_amount, remaining_amount, is_signed):
        session = self.db_conn.create_session()
        try:
            contract = self.writer.create_contract(
                session,
                current_user,
                client_id,
                commercial_id,
                total_amount,
                remaining_amount,
                is_signed
            )
            self.print_green(f"Contrat créé : ID = {contract.id}")
        except Exception as e:
            self.print_red(f"Erreur lors de la création du contrat: {e}")
            session.rollback()
        finally:
            session.close()

    def update_contract_cli(self, current_user, contract_id, **updates):
        session = self.db_conn.create_session()
        try:
            contract = self.writer.update_contract(
                session,
                current_user,
                contract_id,
                **updates
            )
            self.print_green(f"Contrat {contract.id} mis à jour.")
        except Exception as e:
            self.print_red(f"Erreur lors de la mise à jour du contrat: {e}")
            session.rollback()
        finally:
            session.close()

    def update_event_cli(self, current_user, event_id, **updates):
        session = self.db_conn.create_session()
        try:
            event = self.writer.update_event(
                session,
                current_user,
                event_id,
                **updates
            )
            self.print_green(f"Événement {event.id} mis à jour.")
        except Exception as e:
            self.print_red(
                f"Erreur lors de la mise à jour de l'événement: {e}")
            session.rollback()
        finally:
            session.close()
