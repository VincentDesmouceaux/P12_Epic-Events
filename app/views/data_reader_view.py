"""
Vue « lecture seule » : affiche les listes de clients, contrats et événements.

Une fois connecté, **tout collaborateur** (gestion, commercial, support)
peut consulter l’ensemble des entités.  
Le filtrage éventuel (ex : “mes contrats uniquement”) relèvera
de la vue ou de paramètres facultatifs.
"""
from app.controllers.data_reader import DataReader
from app.views.generic_view import GenericView


class DataReaderView(GenericView):
    """Interface CLI pour la consultation des données."""

    # ------------------------------------------------------------------ #
    #  construction
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    # ------------------------------------------------------------------ #
    #  helper d’affichage
    # ------------------------------------------------------------------ #
    @staticmethod
    def _format_entity(entity) -> str:
        """
        Transforme un objet SQLAlchemy en texte lisible (no password_hash).
        """
        out = {
            col.name: getattr(entity, col.name)
            for col in entity.__table__.columns
            if col.name != "password_hash"
        }
        return str(out)

    # ------------------------------------------------------------------ #
    #  affichage des listes
    # ------------------------------------------------------------------ #
    def display_clients_only(self, current_user: dict):
        print(f"[DataReaderView][TRACE] display_clients_only {current_user}")
        sess = self.db_conn.create_session()
        try:
            for cli in self.reader.get_all_clients(sess, current_user):
                print(self._format_entity(cli))
        finally:
            sess.close()

    def display_contracts_only(self, current_user: dict):
        print(f"[DataReaderView][TRACE] display_contracts_only {current_user}")
        sess = self.db_conn.create_session()
        try:
            for ctr in self.reader.get_all_contracts(sess, current_user):
                print(self._format_entity(ctr))
        finally:
            sess.close()

    def display_events_only(self, current_user: dict):
        print(f"[DataReaderView][TRACE] display_events_only {current_user}")
        sess = self.db_conn.create_session()
        try:
            for ev in self.reader.get_all_events(sess, current_user):
                print(self._format_entity(ev))
        finally:
            sess.close()
