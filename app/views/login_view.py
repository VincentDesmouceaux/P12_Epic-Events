# app/views/login_view.py

from app.authentification.auth_controller import AuthController


class LoginView:
    """
    Vue pour la connexion de l'utilisateur.
    Gère l'authentification via AuthController.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.auth_controller = AuthController()

    def login(self):
        """
        Version 'interactive' : on fait input() pour demander l'email et le mot de passe.
        """
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

    def login_with_credentials(self, email, password):
        """
        Version 'non interactive' : on passe directement email/password en paramètres.
        """
        session = self.db_conn.create_session()
        user = self.auth_controller.authenticate_user(session, email, password)
        if user:
            token = self.auth_controller.generate_token(user)
            print("Authentification réussie.")
            print("Votre jeton JWT est :", token)
        else:
            print("Échec de l'authentification.")
        session.close()

        # app/views/login_view.py

    def login_with_credentials_return_user(self, email, password):
        """
        Retourne un objet user si succès, None sinon
        (pas d'affichage, c'est le test qui gère).
        """
        session = self.db_conn.create_session()
        user = self.auth_controller.authenticate_user(session, email, password)
        session.close()
        return user
