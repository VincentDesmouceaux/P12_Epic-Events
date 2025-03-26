from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataReader:
    """
    Classe responsable de la lecture des données depuis la base,
    en s'assurant que l'utilisateur est authentifié et (optionnellement)
    autorisé à accéder aux informations.

    Les méthodes de lecture appliquent un filtrage selon le rôle de l'utilisateur :
      - Tous les collaborateurs peuvent accéder à tous les clients et contrats.
      - Pour les événements, si l'utilisateur a le rôle "support", il ne voit que les événements qui lui sont attribués.
    """

    def __init__(self, db_connection):
        """
        Initialise le DataReader avec la connexion à la base.
        """
        self.db_connection = db_connection

    def _check_auth(self, current_user):
        if not current_user:
            raise Exception("Utilisateur non authentifié.")
        # Ici, vous pouvez ajouter d'autres vérifications de permission
        return True

    def get_all_clients(self, session, current_user):
        """
        Retourne la liste de tous les clients.
        Tous les utilisateurs authentifiés ont accès à cette information.
        """
        self._check_auth(current_user)
        return session.query(Client).all()

    def get_all_contracts(self, session, current_user):
        """
        Retourne la liste de tous les contrats.
        Tous les utilisateurs authentifiés ont accès à cette information.
        """
        self._check_auth(current_user)
        return session.query(Contract).all()

    def get_all_events(self, session, current_user):
        """
        Retourne la liste de tous les événements.
        Si l'utilisateur est de type "support", retourne uniquement les événements qui lui sont attribués.
        Pour les autres rôles, retourne tous les événements.
        """
        self._check_auth(current_user)
        if current_user["role"] == "support":
            return session.query(Event).filter(Event.support_id == current_user["id"]).all()
        return session.query(Event).all()
