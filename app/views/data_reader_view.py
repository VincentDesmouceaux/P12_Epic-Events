# app/views/data_reader_view.py

from app.controllers.data_reader import DataReader
from app.views.generic_view import GenericView


class DataReaderView(GenericView):
    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    def display_clients_only(self, current_user):
        print(
            f"[DataReaderView][TRACE] -> display_clients_only current_user={current_user}")
        session = self.db_conn.create_session()
        try:
            lst = self.reader.get_all_clients(session, current_user)
            for c in lst:
                print(self.format_entity(c))
        finally:
            session.close()

    def display_contracts_only(self, current_user):
        print(
            f"[DataReaderView][TRACE] -> display_contracts_only current_user={current_user}")
        session = self.db_conn.create_session()
        try:
            lst = self.reader.get_all_contracts(session, current_user)
            for ctr in lst:
                print(self.format_entity(ctr))
        finally:
            session.close()

    def display_events_only(self, current_user):
        print(
            f"[DataReaderView][TRACE] -> display_events_only current_user={current_user}")
        session = self.db_conn.create_session()
        try:
            lst = self.reader.get_all_events(session, current_user)
            for ev in lst:
                print(self.format_entity(ev))
        finally:
            session.close()
