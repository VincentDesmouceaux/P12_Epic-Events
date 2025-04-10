# app/views/data_writer_view.py
from app.controllers.data_writer import DataWriter
from datetime import datetime
from app.views.generic_view import GenericView
from app.authentification.auth_controller import AuthController


class DataWriterView(GenericView):
    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.writer = DataWriter(self.db_conn)
        self.auth_controller = AuthController()

    def run(self):
        """
        Démonstration interactive pour un utilisateur "gestion" :
        Création d'un collaborateur, d'un contrat (en utilisant le commercial lié au client)
        et d'un événement.
        """
        session = self.db_conn.create_session()
        current_user = {"id": 1, "role": "gestion", "role_id": 3}
        self.print_header("\n[DEBUG] DataWriterView.run() - START")
        self.print_yellow("[DEBUG] current_user = " + str(current_user))

        # Création d'un collaborateur
        self.print_cyan("Création d'un collaborateur...")
        new_user = None
        try:
            new_user = self.writer.create_user(
                session,
                current_user,
                employee_number=None,
                first_name="Jean",
                last_name="Dupont",
                email="jean.dupont@example.com",
                password_hash="hashed_value",
                role_id=current_user.get("role_id", 3)
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

        # Vérification de l'existence d'un client avec id=1, sinon en créer un
        from app.models.client import Client
        client = session.query(Client).filter_by(id=1).first()
        if not client:
            self.print_yellow(
                "Client introuvable. Création d'un client de démonstration...")
            client = Client(
                full_name="Client Demo",
                email="demo@example.com",
                phone="0000000000",
                company_name="Demo Corp",
                commercial_id=new_user.id  # Pour l'exemple, on utilise new_user
            )
            session.add(client)
            session.commit()
            self.print_green(
                "Client de démonstration créé avec ID = " + str(client.id))

        # Création d'un contrat sans demande manuelle de l'ID du commercial
        new_contract = None
        try:
            new_contract = self.writer.create_contract(
                session,
                current_user,
                client_id=client.id,
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
        else:
            self.print_red("[DEBUG] new_contract n'a pas été créé.")

        # Création d'un événement
        new_event = None
        try:
            if new_contract:
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

    def create_user_cli(self, current_user, fname, lname, email, password):
        session = self.db_conn.create_session()
        try:
            hashed_password = self.auth_controller.hasher.hash(password)
            user = self.writer.create_user(
                session,
                current_user,
                employee_number=None,
                first_name=fname,
                last_name=lname,
                email=email,
                password_hash=hashed_password,
                role_id=current_user.get("role_id", 3)
            )
            self.print_green(
                "Collaborateur créé : Employee Number = " + user.employee_number)
        except Exception as e:
            self.print_red(
                "Erreur lors de la création du collaborateur: " + str(e))
            session.rollback()
        finally:
            session.close()

    def update_user_cli(self, current_user, employee_number, **updates):
        session = self.db_conn.create_session()
        try:
            updated = self.writer.update_user_by_employee_number(
                session, current_user, employee_number, **updates)
            self.print_green(
                f"Collaborateur {updated.employee_number} mis à jour.")
        except Exception as e:
            self.print_red("Erreur lors de la mise à jour: " + str(e))
            session.rollback()
        finally:
            session.close()
