from app.controllers.data_reader import DataReader


class DataReaderView:
    """
    Vue de lecture des données de l'application CRM.
    Utilise DataReader pour récupérer les données.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    def display_data(self, current_user):
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


def main():
    # Permet l'exécution autonome pour tester la vue DataReader
    from app.config.database import DatabaseConfig, DatabaseConnection
    db_config = DatabaseConfig()
    db_conn = DatabaseConnection(db_config)
    # Simuler un utilisateur authentifié
    current_user = {"id": 1, "role": "commercial"}
    view = DataReaderView(db_conn)
    view.display_data(current_user)


if __name__ == "__main__":
    main()
