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
        """
        Affiche clients, contrats et événements (avec nom + contact client pour chaque événement).
        """
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
                # Récupération du client via la relation contract → client
                client = getattr(event.contract, "client", None)
                client_name = client.full_name if client else "Inconnu"
                client_contact = (
                    f"{client.email} / {client.phone}" if client else "N/A"
                )

                print(
                    f"  id={event.id}, "
                    f"contract_id={event.contract_id}, "
                    f"client_name={client_name}, "
                    f"client_contact={client_contact}, "
                    f"support_id={event.support_id}, "
                    f"date_start={event.date_start}, "
                    f"date_end={event.date_end}, "
                    f"location={event.location}, "
                    f"attendees={event.attendees}, "
                    f"notes={event.notes}"
                )
        finally:
            session.close()

    def display_clients_only(self, current_user):
        """
        Affiche la liste des clients.
        """
        session = self.db_conn.create_session()
        try:
            clients = self.reader.get_all_clients(session, current_user)
            print(f"{len(clients)} clients :")
            for client in clients:
                print("  " + self.format_entity(client))
        finally:
            session.close()

    def display_contracts_only(self, current_user):
        """
        Affiche la liste des contrats.
        """
        session = self.db_conn.create_session()
        try:
            contracts = self.reader.get_all_contracts(session, current_user)
            print(f"{len(contracts)} contrats :")
            for contract in contracts:
                print("  " + self.format_entity(contract))
        finally:
            session.close()

    def display_events_only(self, current_user):
        """
        Affiche la liste des événements, en enrichissant chaque ligne
        du nom et du contact client.
        """
        session = self.db_conn.create_session()
        try:
            events = self.reader.get_all_events(session, current_user)
            print(f"{len(events)} événements :")
            for event in events:
                client = getattr(event.contract, "client", None)
                client_name = client.full_name if client else "Inconnu"
                client_contact = (
                    f"{client.email} / {client.phone}" if client else "N/A"
                )

                print(
                    f"  id={event.id}, "
                    f"contract_id={event.contract_id}, "
                    f"client_name={client_name}, "
                    f"client_contact={client_contact}, "
                    f"support_id={event.support_id}, "
                    f"date_start={event.date_start}, "
                    f"date_end={event.date_end}, "
                    f"location={event.location}, "
                    f"attendees={event.attendees}, "
                    f"notes={event.notes}"
                )
        finally:
            session.close()
