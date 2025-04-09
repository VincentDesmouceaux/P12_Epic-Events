# app/views/data_reader_view.py

from app.controllers.data_reader import DataReader


class DataReaderView:
    """
    Vue pour l'affichage des données de l'application CRM.
    Utilise DataReader pour récupérer et afficher les données.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    def display_data_full(self, current_user):
        """
        Méthode existante (interactive) : liste clients, contrats, events ensemble.
        """
        session = self.db_conn.create_session()
        try:
            clients = self.reader.get_all_clients(session, current_user)
            contracts = self.reader.get_all_contracts(session, current_user)
            events = self.reader.get_all_events(session, current_user)
            print("Nombre de clients :", len(clients))
            print("Nombre de contrats :", len(contracts))
            print("Nombre d'événements :", len(events))
        finally:
            session.close()

    def display_clients_only(self, current_user):
        """
        Liste uniquement les clients, sans input().
        """
        session = self.db_conn.create_session()
        try:
            clients = self.reader.get_all_clients(session, current_user)
            print(f"{len(clients)} clients :")
            for c in clients:
                print(f"  ID={c.id}, FullName={c.full_name}, Email={c.email}")
        finally:
            session.close()

    def display_contracts_only(self, current_user):
        session = self.db_conn.create_session()
        try:
            contracts = self.reader.get_all_contracts(session, current_user)
            print(f"{len(contracts)} contrats :")
            for ctr in contracts:
                status = "Signé" if ctr.is_signed else "Non signé"
                print(
                    f"  ID={ctr.id}, total={ctr.total_amount}, remaining={ctr.remaining_amount}, {status}")
        finally:
            session.close()

    def display_events_only(self, current_user):
        session = self.db_conn.create_session()
        try:
            events = self.reader.get_all_events(session, current_user)
            print(f"{len(events)} événements :")
            for e in events:
                print(
                    f"  ID={e.id}, Contrat={e.contract_id}, Support={e.support_id}, Attendees={e.attendees}")
        finally:
            session.close()
