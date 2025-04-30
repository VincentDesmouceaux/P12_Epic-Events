# app/controllers/data_reader.py

from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataReader:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def _debug(self, msg, **kwargs):
        print(f"[DataReader][DEBUG] {msg} -> {kwargs}")

    def _trace(self, msg):
        print(f"[DataReader][TRACE] {msg}")

    def _check_auth(self, current_user):
        self._debug("_check_auth", current_user=current_user)
        if not current_user:
            raise Exception("Utilisateur non authentifié.")

    def get_all_clients(self, session, current_user):
        print("\n--- get_all_clients START ---")
        print(f"current_user: {current_user}")
        self._check_auth(current_user)

        session.expire_all()
        print("session.expire_all() appelé")

        # --- Avant filtrage ---
        all_clients = session.query(Client).all()
        print(
            f"Total clients en base (avant filtrage) = {len(all_clients)}, ids = {[c.id for c in all_clients]}"
        )

        role = current_user.get("role")
        print(f"Rôle détecté = '{role}'")

        if role == "commercial":
            print("→ Branche COMMERCIAL")
            lst = session.query(Client).filter_by(
                commercial_id=current_user["id"]
            ).all()
            print(
                f" commercial sees {len(lst)} clients, ids = {[c.id for c in lst]}"
            )
            print("--- get_all_clients END ---\n")
            return lst

        if role == "support":
            print("→ Branche SUPPORT (accès interdit aux clients)")
            raise PermissionError("Accès refusé aux clients pour le support")

        # gestion et autres
        print("→ Branche GESTION (retourne tous les clients)")
        lst = all_clients
        print(f" gestion sees {len(lst)} clients, ids = {[c.id for c in lst]}")
        print("--- get_all_clients END ---\n")
        return lst

    def get_all_contracts(self, session, current_user):
        print("\n--- get_all_contracts START ---")
        print(f"current_user: {current_user}")
        self._check_auth(current_user)

        session.expire_all()
        print("session.expire_all() appelé")

        # --- Avant filtrage ---
        all_contracts = session.query(Contract).all()
        print(
            f"Total contracts en base (avant filtrage) = {len(all_contracts)}, ids = {[c.id for c in all_contracts]}"
        )

        role = current_user.get("role")
        print(f"Rôle détecté = '{role}'")

        if role == "commercial":
            print("→ Branche COMMERCIAL")
            lst = session.query(Contract).filter_by(
                commercial_id=current_user["id"]
            ).all()
            print(
                f" commercial sees {len(lst)} contracts, ids = {[c.id for c in lst]}"
            )
            print("--- get_all_contracts END ---\n")
            return lst

        if role == "support":
            print("→ Branche SUPPORT (accès interdit aux contrats)")
            raise PermissionError("Accès refusé aux contrats pour le support")

        # gestion et autres
        print("→ Branche GESTION (retourne tous les contrats)")
        lst = all_contracts
        print(
            f" gestion sees {len(lst)} contracts, ids = {[c.id for c in lst]}")
        print("--- get_all_contracts END ---\n")
        return lst

    def get_all_events(self, session, current_user):
        print("\n--- get_all_events START ---")
        print(f"current_user: {current_user}")
        self._check_auth(current_user)

        session.expire_all()
        print("session.expire_all() appelé")

        # --- Avant filtrage ---
        all_events = session.query(Event).all()
        print(
            f"Total events en base (avant filtrage) = {len(all_events)}, ids = {[e.id for e in all_events]}"
        )

        role = current_user.get("role")
        print(f"Rôle détecté = '{role}'")

        if role == "support":
            print("→ Branche SUPPORT")
            lst = session.query(Event).filter_by(
                support_id=current_user["id"]
            ).all()
            print(
                f" support sees {len(lst)} events, ids = {[e.id for e in lst]}")
            print("--- get_all_events END ---\n")
            return lst

        if role == "commercial":
            print("→ Branche COMMERCIAL (join Contract)")
            lst = (
                session.query(Event)
                .join(Contract, Event.contract_id == Contract.id)
                .filter(Contract.commercial_id == current_user["id"])
                .all()
            )
            print(
                f" commercial sees {len(lst)} events, ids = {[e.id for e in lst]}")
            print("--- get_all_events END ---\n")
            return lst

        # gestion et autres
        print("→ Branche GESTION (retourne tous les événements)")
        lst = all_events
        print(f" gestion sees {len(lst)} events, ids = {[e.id for e in lst]}")
        print("--- get_all_events END ---\n")
        return lst
