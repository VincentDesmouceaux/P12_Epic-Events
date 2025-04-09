# main.py
from app.config.database import DatabaseConfig, DatabaseConnection
from app.views.cli_interface import CLIInterface


class EpicEventsCRM:
    """
    Classe principale CLI Epic Events.
    """

    def __init__(self):
        self.db_config = DatabaseConfig()
        self.db_connection = DatabaseConnection(self.db_config)

    def run(self):
        # Lance notre nouveau CLIInterface
        interface = CLIInterface(self.db_connection)
        interface.run()


def main():
    app = EpicEventsCRM()
    app.run()


if __name__ == "__main__":
    main()
