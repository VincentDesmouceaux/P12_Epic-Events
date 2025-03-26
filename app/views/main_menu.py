from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class MainMenu:
    """
    Classe de vue pour le menu principal de l'application.
    Ordonne l'exécution des différentes vues (login, lecture, création/mise à jour).
    """

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def show(self):
        while True:
            option = input(
                "Menu - Choisissez: 1.Login, 2.Data, 3.Data Writer, 4.Quitter: ").strip()
            if option == "1":
                login_view = LoginView(self.db_connection)
                login_view.login()
            elif option == "2":
                # Dans une application réelle, l'utilisateur authentifié serait récupéré
                current_user = {"id": 1, "role": "commercial"}
                data_reader_view = DataReaderView(self.db_connection)
                data_reader_view.display_data(current_user)
            elif option == "3":
                # Option pour tester la création/mise à jour des données
                data_writer_view = DataWriterView(self.db_connection)
                data_writer_view.run()
            elif option == "4":
                break
            else:
                print("Option invalide.")
