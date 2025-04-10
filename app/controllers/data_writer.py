# app/controllers/data_writer.py
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from sqlalchemy.exc import IntegrityError


class DataWriter:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _check_auth(self, current_user):
        if not current_user:
            raise Exception("Utilisateur non authentifié.")

    def _check_permission(self, current_user, allowed_roles):
        self._check_auth(current_user)
        if current_user.get("role") not in allowed_roles:
            raise Exception("Permission refusée pour cet utilisateur.")

    def _get_prefix_for_role(self, role_id):
        if role_id == 1:
            return "C"
        elif role_id == 2:
            return "S"
        elif role_id == 3:
            return "G"
        else:
            return "X"

    def _generate_employee_number(self, session, role_id):
        prefix = self._get_prefix_for_role(role_id)
        max_num = 0
        results = session.query(User.employee_number).filter(
            User.role_id == role_id).all()
        for (emp_num,) in results:
            if emp_num and emp_num.startswith(prefix):
                try:
                    num = int(emp_num[len(prefix):])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    continue
        return f"{prefix}{max_num + 1:03d}"

    # --- Collaborateur ---
    def create_user(self, session, current_user, employee_number, first_name, last_name, email, password_hash, role_id):
        self._check_permission(current_user, ["gestion"])
        if not employee_number:
            employee_number = self._generate_employee_number(session, role_id)
        new_user = User(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id
        )
        session.add(new_user)
        try:
            session.commit()
        except IntegrityError as e:
            session.rollback()
            # On retourne l'utilisateur existant si l'email existe déjà
            existing = session.query(User).filter_by(email=email).first()
            if existing:
                return existing
            raise Exception(
                f"Erreur lors de la création de l'utilisateur : {e}")
        return new_user

    def update_user(self, session, current_user, user_id, **kwargs):
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise Exception("Collaborateur non trouvé.")
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        session.commit()
        return user

    def update_user_by_employee_number(self, session, current_user, employee_number, **kwargs):
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise Exception(
                "Collaborateur non trouvé avec cet employee_number.")
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        session.commit()
        return user

    def delete_user(self, session, current_user, employee_number):
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise Exception(
                "Collaborateur non trouvé avec cet employee_number.")
        session.delete(user)
        session.commit()
        return True

    # --- Client ---
    def create_client(self, session, current_user, full_name, email, phone, company_name, commercial_id):
        self._check_permission(current_user, ["gestion", "commercial"])
        new_client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            commercial_id=commercial_id
        )
        session.add(new_client)
        session.commit()
        return new_client

    def update_client(self, session, current_user, client_id, **kwargs):
        self._check_permission(current_user, ["gestion", "commercial"])
        client = session.query(Client).filter_by(id=client_id).first()
        if not client:
            raise Exception("Client non trouvé.")
        for field, value in kwargs.items():
            if hasattr(client, field):
                setattr(client, field, value)
        session.commit()
        return client

    # --- Contrat ---
    def create_contract(self, session, current_user, client_id, total_amount, remaining_amount, is_signed=False):
        """
        Crée un contrat en récupérant l'ID du client et en utilisant automatiquement
        l'ID du commercial associé au client. Accessible aux rôles "gestion" et "commercial".
        """
        self._check_permission(current_user, ["gestion", "commercial"])
        from app.models.client import Client
        client = session.query(Client).filter_by(id=client_id).first()
        if not client:
            raise Exception("Client introuvable.")
        new_contract = Contract(
            client_id=client.id,
            commercial_id=client.commercial_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            is_signed=is_signed
        )
        session.add(new_contract)
        session.commit()
        return new_contract

    def update_contract(self, session, current_user, contract_id, **kwargs):
        self._check_permission(current_user, ["gestion", "commercial"])
        contract = session.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            raise Exception("Contrat non trouvé.")
        for field, value in kwargs.items():
            if hasattr(contract, field):
                setattr(contract, field, value)
        session.commit()
        return contract

    # --- Événement ---
    def create_event(self, session, current_user, contract_id, support_id, date_start, date_end, location, attendees, notes):
        self._check_permission(
            current_user, ["gestion", "commercial", "support"])
        new_event = Event(
            contract_id=contract_id,
            support_id=support_id,
            date_start=date_start,
            date_end=date_end,
            location=location,
            attendees=attendees,
            notes=notes
        )
        session.add(new_event)
        session.commit()
        return new_event

    def update_event(self, session, current_user, event_id, **kwargs):
        self._check_permission(
            current_user, ["gestion", "commercial", "support"])
        event = session.query(Event).filter_by(id=event_id).first()
        if not event:
            raise Exception("Événement non trouvé.")
        for field, value in kwargs.items():
            if hasattr(event, field):
                setattr(event, field, value)
        session.commit()
        return event


class DataReader:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _check_auth(self, current_user):
        if not current_user:
            raise Exception("Utilisateur non authentifié.")
        return True

    def get_all_clients(self, session, current_user):
        self._check_auth(current_user)
        from app.models.client import Client
        return session.query(Client).all()

    def get_all_contracts(self, session, current_user):
        self._check_auth(current_user)
        from app.models.contract import Contract
        return session.query(Contract).all()

    def get_all_events(self, session, current_user):
        self._check_auth(current_user)
        from app.models.event import Event
        if current_user["role"] == "support":
            return session.query(Event).filter(Event.support_id == current_user["id"]).all()
        return session.query(Event).all()
