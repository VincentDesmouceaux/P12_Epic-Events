"""
Contrôleur de lecture.

⚠️  Règle métier (mise à jour) :
    une fois authentifiés, les trois rôles (gestion, commercial, support)
    peuvent consulter TOUS les clients, contrats et événements.

Un commercial *peut* vouloir filtrer « ses » clients/contrats – cela se
fera côté vue ou via des paramètres facultatifs (non gérés ici pour l’instant).
"""

from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataReader:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    # ------------------------------------------------------------------ #
    #  outils internes de log
    # ------------------------------------------------------------------ #
    def _debug(self, msg, **kw):
        print(f"[DataReader][DEBUG] {msg} -> {kw}")

    def _trace(self, msg):
        print(f"[DataReader][TRACE] {msg}")

    # ------------------------------------------------------------------ #
    #  sécurité très minimale : vérifie qu’un user est bien présent
    # ------------------------------------------------------------------ #
    def _check_auth(self, current_user: dict):
        self._debug("_check_auth", current_user=current_user)
        if not current_user:
            raise PermissionError("Utilisateur non authentifié.")

    # ------------------------------------------------------------------ #
    #  clients
    # ------------------------------------------------------------------ #
    def get_all_clients(self, session, current_user):
        self._trace("get_all_clients")
        self._check_auth(current_user)

        session.expire_all()                 # toujours relire la BD
        role = current_user.get("role")

        # → accès complet quel que soit le rôle
        # (on garde ici la possibilité de filtrer par commercial si on le
        #  souhaite ultérieurement, mais ce n’est PAS imposé).
        if role == "commercial" and "force_filter" in current_user:
            return (
                session.query(Client)
                .filter(Client.commercial_id == current_user["id"])
                .all()
            )

        return session.query(Client).all()

    # ------------------------------------------------------------------ #
    #  contrats
    # ------------------------------------------------------------------ #
    def get_all_contracts(self, session, current_user):
        self._trace("get_all_contracts")
        self._check_auth(current_user)

        session.expire_all()
        role = current_user.get("role")

        if role == "commercial" and "force_filter" in current_user:
            return (
                session.query(Contract)
                .filter(Contract.commercial_id == current_user["id"])
                .all()
            )

        return session.query(Contract).all()

    # ------------------------------------------------------------------ #
    #  événements
    # ------------------------------------------------------------------ #
    def get_all_events(self, session, current_user):
        self._trace("get_all_events")
        self._check_auth(current_user)

        session.expire_all()
        role = current_user.get("role")

        if role == "commercial" and "force_filter" in current_user:
            # on récupère uniquement les événements liés aux contrats du commercial
            return (
                session.query(Event)
                .join(Contract, Event.contract_id == Contract.id)
                .filter(Contract.commercial_id == current_user["id"])
                .all()
            )

        if role == "support" and "force_filter" in current_user:
            # uniquement les événements assignés à ce technicien support
            return session.query(Event).filter(Event.support_id == current_user["id"]).all()

        return session.query(Event).all()
