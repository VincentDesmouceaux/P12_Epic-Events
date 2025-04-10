# app/views/login_view.py
from app.authentification.auth_controller import AuthController
from app.views.generic_view import GenericView


class LoginView(GenericView):
    """
    Vue pour la connexion de l'utilisateur.
    """

    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.auth_controller = AuthController()

    def login(self):
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
        session = self.db_conn.create_session()
        user = self.auth_controller.authenticate_user(session, email, password)
        session.close()
        return user
