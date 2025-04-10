# app/controllers/data_writer.py
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from sqlalchemy import func


class DataWriter:
    """
    Contrôleur pour la création, la mise à jour et la suppression des données.
    """

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _check_auth(self, current_user):
        if not current_user:
            raise Exception("Utilisateur non authentifié.")

    def _check_permission(self, current_user, allowed_roles):
        self._check_auth(current_user)
        if current_user.get("role") not in allowed_roles:
            raise Exception("Permission refusée pour cet utilisateur.")

    def get_next_employee_number(self, session, role_initial):
        """
        Retourne le prochain numéro d'employé pour une initiale donnée.
        Ex : pour "G", si le dernier est "G001", retourne "G002".
        """
        prefix = role_initial.upper()
        max_num = session.query(func.max(func.substr(User.employee_number, len(prefix)+1, 3)))\
            .filter(User.employee_number.like(f"{prefix}%")).scalar()
        if max_num is None:
            next_num = 1
        else:
            try:
                next_num = int(max_num) + 1
            except ValueError:
                next_num = 1
        return f"{prefix}{next_num:03d}"

    def create_user(self, session, current_user, first_name, last_name, email, password_hash, role_id, employee_number=None):
        """
        Crée un collaborateur. Pour le rôle 'gestion', le numéro d'employé est généré automatiquement.
        """
        self._check_permission(current_user, ["gestion"])
        if employee_number is None:
            # Pour la gestion, on utilise l'initiale "G"
            employee_number = self.get_next_employee_number(session, "G")
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
            return new_user
        except Exception as e:
            session.rollback()
            raise Exception(
                "Erreur lors de la création de l'utilisateur: " + str(e))

    def update_user(self, session, current_user, user_id, **kwargs):
        """
        Met à jour un collaborateur identifié par son ID.
        """
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
        """
        Met à jour un collaborateur identifié par son employee_number.
        """
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise Exception("Collaborateur non trouvé par employee_number.")
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        session.commit()
        return user

    def delete_user(self, session, current_user, employee_number):
        """
        Supprime un collaborateur identifié par son employee_number.
        """
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise Exception("Collaborateur non trouvé.")
        session.delete(user)
        session.commit()
        return True

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

    def create_contract(self, session, current_user, client_id, commercial_id, total_amount, remaining_amount, is_signed=False):
        self._check_permission(current_user, ["gestion", "commercial"])
        new_contract = Contract(
            client_id=client_id,
            commercial_id=commercial_id,
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
