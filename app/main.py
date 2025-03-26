from app.config.database import DatabaseConfig, DatabaseConnection
from app.views.main_menu import MainMenu


class EpicEventsCRM:
    """
    Classe principale qui gère l'application CLI Epic Events.
    Elle utilise la configuration et la connexion à la BDD pour fonctionner.
    """

    def __init__(self):
        # 1. Chargement de la configuration (via .env, MySQL par défaut)
        self.db_config = DatabaseConfig()
        # 2. Création de la connexion à la base de données
        self.db_connection = DatabaseConnection(self.db_config)

    def run(self):
        """
        Lance le menu principal de l'application en appelant les vues appropriées.
        Aucun affichage direct n'est fait ici, la vue MainMenu s'en charge.
        """
        menu = MainMenu(self.db_connection)
        menu.show()


def main():
    app = EpicEventsCRM()
    app.run()


if __name__ == "__main__":
    main()
