# app/controllers/data_writer.py

from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event
from sqlalchemy.exc import IntegrityError


class DataWriter:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _debug(self, msg, **kwargs):
        print(f"[DataWriter][DEBUG] {msg} -> {kwargs}")

    def _check_auth(self, current_user):
        self._debug("_check_auth", current_user=current_user)
        if not current_user:
            raise Exception("Utilisateur non authentifié.")

    def _check_permission(self, current_user, allowed_roles):
        self._debug("_check_permission", user_role=current_user.get(
            "role"), allowed=allowed_roles)
        self._check_auth(current_user)
        if current_user.get("role") not in allowed_roles:
            raise Exception(
                f"Permission refusée pour {current_user.get('role')} (attendu {allowed_roles}).")

    def _get_prefix_for_role(self, role_id):
        return {1: "C", 2: "S", 3: "G"}.get(role_id, "X")

    def _generate_employee_number(self, session, role_id):
        prefix = self._get_prefix_for_role(role_id)
        max_num = 0
        for (emp_num,) in session.query(User.employee_number).filter(User.role_id == role_id).all():
            if emp_num.startswith(prefix):
                try:
                    num = int(emp_num[len(prefix):])
                    max_num = max(max_num, num)
                except ValueError:
                    continue
        new_emp = f"{prefix}{max_num+1:03d}"
        self._debug("_generate_employee_number",
                    role_id=role_id, new_emp=new_emp)
        return new_emp

    # --- Collaborateur ---
    def create_user(self, session, current_user,
                    employee_number, first_name, last_name, email, password_hash, role_id):
        self._debug("create_user appelé", current_user=current_user,
                    employee_number=employee_number, first_name=first_name,
                    last_name=last_name, email=email, role_id=role_id)
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
            self._debug("create_user IntegrityError", error=str(e))
            existing = session.query(User).filter_by(email=email).first()
            if existing:
                return existing
            raise
        self._debug("Utilisateur créé", id=new_user.id,
                    employee_number=new_user.employee_number)
        return new_user

    def update_user(self, session, current_user, user_id, **kwargs):
        self._debug("update_user appelé", current_user=current_user,
                    user_id=user_id, updates=kwargs)
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).get(user_id)
        if not user:
            raise Exception("Collaborateur non trouvé.")
        for f, v in kwargs.items():
            setattr(user, f, v)
        session.commit()
        self._debug("Collaborateur mis à jour", id=user.id, updates=kwargs)
        return user

    def update_user_by_employee_number(self, session, current_user, employee_number, **kwargs):
        self._debug("update_user_by_employee_number appelé",
                    current_user=current_user, employee_number=employee_number, updates=kwargs)
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise Exception("Collaborateur non trouvé.")
        for field, value in kwargs.items():
            setattr(user, field, value)
        session.commit()
        self._debug("Collaborateur mis à jour", id=user.id, updates=kwargs)
        return user

    def delete_user(self, session, current_user, employee_number):
        self._debug("delete_user appelé", current_user=current_user,
                    employee_number=employee_number)
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(
            employee_number=employee_number).first()
        if not user:
            raise Exception("Collaborateur non trouvé.")
        session.delete(user)
        session.commit()
        self._debug("Collaborateur supprimé", employee_number=employee_number)
        return True

    # --- Client ---
    def create_client(self, session, current_user,
                      full_name, email, phone, company_name, commercial_id):
        print(
            f"[DataWriter][TRACE] -> create_client current_user={current_user}, commercial_id param={commercial_id}")
        self._debug("create_client appelé", current_user=current_user,
                    full_name=full_name, comercial_id=commercial_id)
        self._check_permission(current_user, ["gestion", "commercial"])

        # Si un commercial crée, on utilise son propre ID
        if current_user["role"] == "commercial":
            commercial_id = current_user["id"]
        print(
            f"[DataWriter][TRACE]    effective commercial_id = {commercial_id}")

        new_client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            commercial_id=commercial_id
        )
        session.add(new_client)
        session.commit()
        print(
            f"[DataWriter][TRACE]    client created id={new_client.id}, commercial_id={new_client.commercial_id}")
        self._debug("Client créé", id=new_client.id,
                    commercial_id=new_client.commercial_id)
        return new_client

    def update_client(self, session, current_user, client_id, **kwargs):
        self._debug("update_client appelé", current_user=current_user,
                    client_id=client_id, updates=kwargs)
        self._check_permission(current_user, ["gestion", "commercial"])
        client = session.query(Client).get(client_id)
        if not client:
            raise Exception("Client non trouvé.")
        if current_user["role"] == "commercial" and client.commercial_id != current_user["id"]:
            raise Exception(
                "Vous ne pouvez pas modifier un client qui n'est pas le vôtre.")
        for f, v in kwargs.items():
            setattr(client, f, v)
        session.commit()
        self._debug("Client mis à jour", id=client.id, updates=kwargs)
        return client

    # --- Contrat ---
    def create_contract(self, session, current_user,
                        client_id, total_amount, remaining_amount, is_signed=False):
        self._debug("create_contract appelé", current_user=current_user,
                    client_id=client_id, total=total_amount, remaining=remaining_amount)
        self._check_permission(current_user, ["gestion", "commercial"])
        client = session.query(Client).get(client_id)
        if not client:
            raise Exception("Client introuvable.")
        if current_user["role"] == "commercial" and client.commercial_id != current_user["id"]:
            raise Exception(
                "Vous ne pouvez pas créer un contrat pour ce client.")
        contract = Contract(
            client_id=client.id,
            commercial_id=client.commercial_id,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            is_signed=is_signed
        )
        session.add(contract)
        session.commit()
        self._debug("Contrat créé", id=contract.id,
                    commercial_id=contract.commercial_id)
        return contract

    def update_contract(self, session, current_user, contract_id, **kwargs):
        self._debug("update_contract appelé", current_user=current_user,
                    contract_id=contract_id, updates=kwargs)
        self._check_permission(current_user, ["gestion", "commercial"])
        contract = session.query(Contract).get(contract_id)
        if not contract:
            raise Exception("Contrat non trouvé.")
        if current_user["role"] == "commercial" and contract.commercial_id != current_user["id"]:
            raise Exception("Vous ne pouvez pas modifier ce contrat.")
        for f, v in kwargs.items():
            setattr(contract, f, v)
        session.commit()
        self._debug("Contrat mis à jour", id=contract.id, updates=kwargs)
        return contract

    # --- Événement ---
    def create_event(self, session, current_user,
                     contract_id, support_id, date_start=None, date_end=None, location=None, attendees=None, notes=None):
        print(
            f"[DataWriter][TRACE] -> create_event current_user={current_user}, contract_id={contract_id}, support_id={support_id}")
        self._debug("create_event appelé", current_user=current_user,
                    contract_id=contract_id, support_id=support_id)
        self._check_permission(
            current_user, ["gestion", "commercial", "support"])
        contract = session.query(Contract).get(contract_id)
        if not contract:
            raise Exception("Contrat non trouvé.")
        if current_user["role"] == "commercial":
            if contract.commercial_id != current_user["id"]:
                raise Exception(
                    "Vous ne pouvez pas créer un événement sur un contrat qui n'est pas le vôtre.")
            if not contract.is_signed:
                raise Exception(
                    "Vous ne pouvez pas créer un événement sur un contrat non signé.")
        if current_user["role"] == "support":
            # un support ne crée pas d'événement
            raise Exception("Permission refusée pour support.")
        event = Event(
            contract_id=contract_id,
            support_id=support_id,
            date_start=date_start,
            date_end=date_end,
            location=location,
            attendees=attendees,
            notes=notes
        )
        session.add(event)
        session.commit()
        print(f"[DataWriter][TRACE]    event created id={event.id}")
        self._debug("Événement créé", id=event.id)
        return event

    def update_event(self, session, current_user, event_id, **kwargs):
        self._debug("update_event appelé", current_user=current_user,
                    event_id=event_id, updates=kwargs)
        self._check_permission(
            current_user, ["gestion", "commercial", "support"])
        event = session.query(Event).get(event_id)
        if not event:
            raise Exception("Événement non trouvé.")
        if current_user["role"] == "commercial":
            ctr = session.query(Contract).get(event.contract_id)
            if ctr.commercial_id != current_user["id"]:
                raise Exception("Vous ne pouvez pas modifier cet événement.")
        if current_user["role"] == "support":
            if event.support_id != current_user["id"]:
                raise Exception(
                    "Vous ne pouvez pas modifier un événement qui ne vous est pas assigné.")
        for f, v in kwargs.items():
            setattr(event, f, v)
        session.commit()
        self._debug("Événement mis à jour", id=event.id, updates=kwargs)
        return event
