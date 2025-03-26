from app.authentification.auth_controller import AuthController


class LoginView:
    """
    Classe de vue pour la connexion de l'utilisateur.
    Gère l'authentification via AuthController.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.auth_controller = AuthController()

    def login(self):
        session = self.db_conn.create_session()
        email = input("Entrez votre email : ")
        password = input("Entrez votre mot de passe : ")
        user = self.auth_controller.authenticate_user(session, email, password)
        if user:
            token = self.auth_controller.generate_token(user)
            print("Authentification réussie.")
            print("Votre jeton JWT est :", token)
        else:
            print("Échec de l'authentification.")
        session.close()


def main():
    # Permet l'exécution autonome pour tester la vue de login
    from app.config.database import DatabaseConfig, DatabaseConnection
    db_config = DatabaseConfig()
    db_conn = DatabaseConnection(db_config)
    view = LoginView(db_conn)
    view.login()


if __name__ == "__main__":
    main()
