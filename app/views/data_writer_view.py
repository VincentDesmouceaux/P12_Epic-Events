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
        Création d'un collaborateur, mise à jour, puis création
        d'un contrat et d'un événement.
        """
        session = self.db_conn.create_session()
        current_user = {"id": 1, "role": "gestion", "role_id": 3}

        # 1) Affichage du point de départ
        self.print_header("\n[DEBUG] DataWriterView.run() - START")
        self.print_yellow(f"[DEBUG] current_user = {current_user}")

        # 2) Création d'un collaborateur
        self.print_cyan("\nCréation d'un collaborateur...")
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
                role_id=current_user["role_id"]
            )
            # TRACE après création
            print(f"[DataWriterView][TRACE] new_user returned -> id={new_user.id}, "
                  f"employee_number={new_user.employee_number!r}, "
                  f"first_name={new_user.first_name!r}, "
                  f"email={new_user.email!r}")
            self.print_green(
                f"[DEBUG] new_user.employee_number = {new_user.employee_number}")
        except Exception as e:
            self.print_red(f"[DEBUG] Exception creating user: {e}")
            session.rollback()

        # 3) Mise à jour du collaborateur si créé
        if new_user:
            updates = {"first_name": "Jean-Pierre",
                       "email": "jp.dupont@example.com"}
            print(
                f"[DataWriterView][TRACE] about to call update_user with -> {updates}")
            try:
                updated_user = self.writer.update_user(
                    session,
                    current_user,
                    new_user.id,
                    **updates
                )
                # TRACE juste après la mise à jour
                print(f"[DataWriterView][TRACE] updated_user returned -> id={updated_user.id}, "
                      f"first_name={updated_user.first_name!r}, "
                      f"email={updated_user.email!r}")
                self.print_green(
                    f"[DEBUG] updated_user.first_name = {updated_user.first_name}")
                self.print_green(
                    f"[DEBUG] updated_user.email = {updated_user.email}")
            except Exception as e:
                self.print_red(f"[DEBUG] Exception updating user: {e}")
                session.rollback()

        # 4) (Le reste de la démo : création de client/contrat/événement, inchangé)
        from app.models.client import Client
        client = session.query(Client).filter_by(id=1).first()
        if not client:
            self.print_yellow(
                "Client introuvable. Création d'un client de démonstration…")
            client = Client(
                full_name="Client Demo",
                email="demo@example.com",
                phone="0000000000",
                company_name="Demo Corp",
                commercial_id=new_user.id if new_user else None
            )
            session.add(client)
            session.commit()
            self.print_green(
                f"Client de démonstration créé avec ID = {client.id}")

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
            self.print_green(f"[DEBUG] new_contract.id = {new_contract.id}")
        except Exception as e:
            self.print_red(f"[DEBUG] Exception creating contract: {e}")
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
                    f"[DEBUG] updated_contract.remaining_amount = {updated_contract.remaining_amount}")
            except Exception as e:
                self.print_red(f"[DEBUG] Exception updating contract: {e}")
                session.rollback()

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
                self.print_green(f"[DEBUG] new_event.id = {new_event.id}")
        except Exception as e:
            self.print_red(f"[DEBUG] Exception creating event: {e}")
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
                    f"[DEBUG] updated_event.attendees = {updated_event.attendees}")
                self.print_green(
                    f"[DEBUG] updated_event.notes = {updated_event.notes}")
            except Exception as e:
                self.print_red(f"[DEBUG] Exception updating event: {e}")
                session.rollback()

        session.close()
        self.print_header("[DEBUG] DataWriterView.run() - END\n")
