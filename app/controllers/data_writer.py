from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataWriter:
    """
    Classe responsable de la création et de la mise à jour des données
    dans la base, en appliquant une validation basique et un contrôle des permissions.

    Seules les actions autorisées selon le rôle de l'utilisateur (présent dans current_user)
    sont exécutées.
    """

    def __init__(self, db_connection):
        """
        Initialise DataWriter avec une connexion à la base de données.
        """
        self.db_connection = db_connection

    def _check_auth(self, current_user):
        if not current_user:
            raise Exception("Utilisateur non authentifié.")

    def _check_permission(self, current_user, allowed_roles):
        """
        Vérifie si le rôle de l'utilisateur (current_user["role"]) est dans allowed_roles.
        """
        self._check_auth(current_user)
        if current_user.get("role") not in allowed_roles:
            raise Exception("Permission refusée pour cet utilisateur.")

    # --- Collaborateur (User) ---
    def create_user(self, session, current_user, employee_number, first_name, last_name, email, password_hash, role_id):
        """
        Crée un nouvel utilisateur (collaborateur). Accessible uniquement aux utilisateurs du rôle "gestion".
        """
        self._check_permission(current_user, ["gestion"])
        new_user = User(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id
        )
        session.add(new_user)
        session.commit()
        return new_user

    def update_user(self, session, current_user, user_id, **kwargs):
        """
        Met à jour un collaborateur existant (y compris son département).
        Accessible uniquement aux utilisateurs du rôle "gestion".
        """
        self._check_permission(current_user, ["gestion"])
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise Exception("Collaborateur non trouvé.")
        # Validation basique des champs mis à jour
        for field, value in kwargs.items():
            if hasattr(user, field):
                setattr(user, field, value)
        session.commit()
        return user

    # --- Client ---
    def create_client(self, session, current_user, full_name, email, phone, company_name, commercial_id):
        """
        Crée un client. Accessible aux rôles "gestion" et "commercial".
        """
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
        """
        Met à jour un client existant.
        Accessible aux rôles "gestion" et "commercial".
        """
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
    def create_contract(self, session, current_user, client_id, commercial_id, total_amount, remaining_amount, is_signed=False):
        """
        Crée un contrat associé à un client et à un commercial.
        Accessible aux rôles "gestion" et "commercial".
        """
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
        """
        Met à jour un contrat existant (tous les champs, y compris relationnels).
        Accessible aux rôles "gestion" et "commercial".
        """
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
        """
        Crée un événement associé à un contrat et attribué à un support.
        Accessible aux rôles "gestion", "commercial" et "support".
        """
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
        """
        Met à jour un événement existant (tous les champs, y compris relationnels).
        Accessible aux rôles "gestion", "commercial" et "support".
        """
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
