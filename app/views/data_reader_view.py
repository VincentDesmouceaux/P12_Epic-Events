# app/views/data_reader_view.py
from app.controllers.data_reader import DataReader
from app.views.generic_entity_view import GenericEntityView


class DataReaderView(GenericEntityView):
    """
    Vue pour l'affichage des données.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    def display_data_full(self, current_user):
        session = self.db_conn.create_session()
        try:
            clients = self.reader.get_all_clients(session, current_user)
            contracts = self.reader.get_all_contracts(session, current_user)
            events = self.reader.get_all_events(session, current_user)
            print("=== Clients ===")
            for client in clients:
                print("  " + self.format_entity(client))
            print("\n=== Contrats ===")
            for contract in contracts:
                print("  " + self.format_entity(contract))
            print("\n=== Événements ===")
            for event in events:
                print("  " + self.format_entity(event))
        finally:
            session.close()

    def display_clients_only(self, current_user):
        session = self.db_conn.create_session()
        try:
            clients = self.reader.get_all_clients(session, current_user)
            print(f"{len(clients)} clients :")
            for client in clients:
                print("  " + self.format_entity(client))
        finally:
            session.close()

    def display_contracts_only(self, current_user):
        session = self.db_conn.create_session()
        try:
            contracts = self.reader.get_all_contracts(session, current_user)
            print(f"{len(contracts)} contrats :")
            for contract in contracts:
                print("  " + self.format_entity(contract))
        finally:
            session.close()

    def display_events_only(self, current_user):
        session = self.db_conn.create_session()
        try:
            events = self.reader.get_all_events(session, current_user)
            print(f"{len(events)} événements :")
            for event in events:
                print("  " + self.format_entity(event))
        finally:
            session.close()
