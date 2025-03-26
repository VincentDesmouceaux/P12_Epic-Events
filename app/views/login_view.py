from app.config.database import DatabaseConfig, DatabaseConnection
from app.authentification.auth_controller import AuthController


class LoginView:
    """
    Classe de vue pour la connexion de l'utilisateur.
    Gère l'initialisation de la configuration, la connexion à la BDD
    et l'authentification via AuthController.
    """

    def __init__(self):
        # Initialisation de la configuration et de la connexion
        self.db_config = DatabaseConfig()
        self.db_conn = DatabaseConnection(self.db_config)
        self.auth_controller = AuthController()

    def login(self):
        # Créer une session de base de données
        session = self.db_conn.create_session()

        # Simuler une saisie utilisateur
        email = input("Entrez votre email : ")
        password = input("Entrez votre mot de passe : ")

        user = self.auth_controller.authenticate_user(session, email, password)
        if user:
            token = self.auth_controller.generate_token(user)
            print("Authentification réussie.")
            print("Votre jeton JWT est :", token)
            # Le jeton peut être stocké ou utilisé pour autoriser d'autres actions
        else:
            print("Échec de l'authentification.")

        session.close()


def main():
    view = LoginView()
    view.login()


if __name__ == "__main__":
    main()
