# app/views/login_view.py

from app.authentification.auth_controller import AuthController
from app.views.generic_view import GenericView


class LoginView(GenericView):
    """
    Vue pour la connexion de l'utilisateur.
    Gère l'authentification via AuthController.
    """

    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.auth_controller = AuthController()

    def login(self):
        """
        Version interactive : on demande à l'utilisateur son email et son mot de passe.
        """
        session = self.db_conn.create_session()
        email = input(self.print_cyan("Entrez votre email : ") or "")
        password = input(self.print_cyan("Entrez votre mot de passe : ") or "")
        user = self.auth_controller.authenticate_user(session, email, password)
        if user:
            token = self.auth_controller.generate_token(user)
            self.print_green("Authentification réussie.")
            self.print_green("Votre jeton JWT est : " + token)
        else:
            self.print_red("Échec de l'authentification.")
        session.close()

    def login_with_credentials(self, email, password):
        """
        Version non interactive : utilisation d'email et mot de passe passés en paramètres.
        """
        session = self.db_conn.create_session()
        user = self.auth_controller.authenticate_user(session, email, password)
        if user:
            token = self.auth_controller.generate_token(user)
            self.print_green("Authentification réussie.")
            self.print_green("Votre jeton JWT est : " + token)
        else:
            self.print_red("Échec de l'authentification.")
        session.close()

    def login_with_credentials_return_user(self, email, password):
        """
        Retourne l'objet user si authentification réussie, sinon None.
        (Sans affichage, pour les tests.)
        """
        session = self.db_conn.create_session()
        user = self.auth_controller.authenticate_user(session, email, password)
        session.close()
        return user
