from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView


class MainMenu:
    """
    Classe de vue pour le menu principal de l'application.
    Ordonne l'exécution des différentes vues (login, lecture des données, etc.).
    """

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def show(self):
        """
        Affiche le menu principal et gère la navigation.
        """
        while True:
            option = input(
                "Menu - Choisissez: 1.Login, 2.Data, 3.Quitter: ").strip()
            if option == "1":
                login_view = LoginView(self.db_connection)
                login_view.login()
            elif option == "2":
                # Ici, on simule qu'un utilisateur authentifié est récupéré.
                # Dans une application réelle, on récupérerait l'objet User authentifié.
                current_user = {"id": 1, "role": "commercial"}
                data_view = DataReaderView(self.db_connection)
                data_view.display_data(current_user)
            elif option == "3":
                break
            else:
                print("Option invalide.")
