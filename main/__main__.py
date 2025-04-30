# main/__main__.py

from .init_db import init_db
from .seed_db import seed_db
from app.config.database import DatabaseConfig, DatabaseConnection
from app.views.cli_interface import CLIInterface


def main():
    print("→ Initialisation de la base de données…")
    init_db()

    print("\n→ Chargement des données d'exemple…")
    seed_db()

    print("\n→ Lancement de l'interface CLI Epic Events\n")
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    CLIInterface(conn).run()


if __name__ == "__main__":
    main()
