"""
Vue “lecture seule” : affiche les listes de clients, contrats et événements.

Tous les rôles connectés (gestion, commercial, support) peuvent consulter
l’ensemble des entités ; on délègue la récupération à `DataReader`.
"""

from app.controllers.data_reader import DataReader
from app.views.generic_view import GenericView


class DataReaderView(GenericView):
    """Interface CLI pour la lecture des données."""

    # ------------------------------------------------------------------ #
    #  construction
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    # ------------------------------------------------------------------ #
    #  helper d’affichage (manquait auparavant)
    # ------------------------------------------------------------------ #
    @staticmethod
    def _format_entity(entity) -> str:
        """
        Transforme n’importe quel objet SQLAlchemy en chaîne lisible :
        on récupère chaque colonne primitive (pas les relations) et on
        retourne un petit dict JSON-style sans le `password_hash`.
        """
        asdict = {}
        for col in entity.__table__.columns:
            if col.name == "password_hash":          # on n’affiche jamais ça
                continue
            asdict[col.name] = getattr(entity, col.name)
        return str(asdict)

    # ------------------------------------------------------------------ #
    #  affichage des listes
    # ------------------------------------------------------------------ #
    def display_clients_only(self, current_user: dict):
        print(
            f"[DataReaderView][TRACE] -> display_clients_only current_user={current_user}")
        session = self.db_conn.create_session()
        try:
            for cli in self.reader.get_all_clients(session, current_user):
                print(self._format_entity(cli))
        finally:
            session.close()

    def display_contracts_only(self, current_user: dict):
        print(
            f"[DataReaderView][TRACE] -> display_contracts_only current_user={current_user}")
        session = self.db_conn.create_session()
        try:
            for ctr in self.reader.get_all_contracts(session, current_user):
                print(self._format_entity(ctr))
        finally:
            session.close()

    def display_events_only(self, current_user: dict):
        print(
            f"[DataReaderView][TRACE] -> display_events_only current_user={current_user}")
        session = self.db_conn.create_session()
        try:
            for ev in self.reader.get_all_events(session, current_user):
                print(self._format_entity(ev))
        finally:
            session.close()
