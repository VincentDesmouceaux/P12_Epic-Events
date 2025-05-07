# app/views/login_view.py
# -*- coding: utf-8 -*-
"""
Vue *Login* : gère l’authentification utilisateur en ligne de commande.

Trois variantes sont proposées :

* :pymeth:`login` : interactive (prompts `input`).
* :pymeth:`login_with_credentials` : appelle la même logique mais
  grâce à des paramètres passés en arguments — utile pour les scripts.
* :pymeth:`login_with_credentials_return_user` : identique à la
  précédente mais renvoie directement l’objet ``User`` (employé pour
  les tests unitaires).
"""

from app.authentification.auth_controller import AuthController
from app.views.generic_view import GenericView


class LoginView(GenericView):
    """Affiche les prompts et délègue la logique à :class:`AuthController`."""

    # ----------------------------------------------------------------- #
    # Construction
    # ----------------------------------------------------------------- #
    def __init__(self, db_connection):
        """
        Parameters
        ----------
        db_connection :
            Objet de connexion disposant d’une méthode
            ``create_session()`` (voir *DatabaseConnection*).
        """
        super().__init__()
        self.db_conn = db_connection
        self.auth_controller = AuthController()

    # ----------------------------------------------------------------- #
    # Modes d’utilisation
    # ----------------------------------------------------------------- #
    def login(self) -> None:
        """
        Mode interactif : questionne l’utilisateur puis affiche le résultat.

        * Succès : le JWT est imprimé.
        * Échec : message d’erreur en rouge.

        Notes
        -----
        Les prompts utilisent :pymeth:`print_cyan` pour rester lisibles.
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

    def login_with_credentials(self, email: str, password: str) -> None:
        """
        Authentifie sans interaction et affiche le résultat (même logique que
        :pymeth:`login`).

        Parameters
        ----------
        email : str
            Adresse de connexion.
        password : str
            Mot de passe en clair.
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

    def login_with_credentials_return_user(self, email: str, password: str):
        """
        Variante silencieuse : renvoie l’objet ``User`` ou *None*.

        Cette méthode est pratique dans les tests automatisés afin de
        récupérer directement l’instance pour des vérifications
        supplémentaires.

        Returns
        -------
        app.models.user.User | None
        """
        session = self.db_conn.create_session()
        user = self.auth_controller.authenticate_user(session, email, password)
        session.close()
        return user
