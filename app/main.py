from app.config.database import DatabaseConfig, DatabaseConnection


class EpicEventsCRM:
    """
    Classe principale qui gère l'application CLI Epic Events.
    Elle utilise la config et la connexion DB pour fonctionner.
    """

    def __init__(self):
        # 1. Configuration (lit .env si présent, MySQL par défaut)
        self.db_config = DatabaseConfig()

        # 2. Connexion DB
        self.db_connection = DatabaseConnection(self.db_config)

    def run(self):
        """
        Méthode principale pour lancer l'application CLI.
        """
        print("Bienvenue dans Epic Events CRM ! (MySQL)")

        # Vérifier la connexion en se connectant une fois à la base
        with self.db_connection.engine.connect() as conn:
            print("Connexion à la base réussie.")

        # Ici, vous pourrez ajouter la logique du programme :
        # - création des tables
        # - menu CLI
        # - etc.
        # Ex: Base.metadata.create_all(bind=self.db_connection.engine)


def main():
    # Instancie la classe principale
    app = EpicEventsCRM()
    # Lance l'application
    app.run()


if __name__ == "__main__":
    main()
