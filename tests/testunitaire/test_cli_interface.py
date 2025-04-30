# -*- coding: utf-8 -*-
from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.login_view = LoginView(self.db)
        self.reader = DataReaderView(self.db)
        self.writer = DataWriterView(self.db)
        self.current_user = None

    def display_main_menu(self):
        self.print_header("\n=== Epic Events CLI ===")
        print(self.BLUE + "[1] Se connecter" + self.END)
        if self.current_user:
            print(self.BLUE + "[2] Lire données" + self.END)
            print(self.BLUE + "[3] Gérer" + self.END)
        print(self.BLUE + "[0] Quitter" + self.END)

    def run(self):
        while True:
            self.display_main_menu()
            choix = input(self.CYAN + "Votre choix : " + self.END).strip()
            if choix == "1":
                self.menu_login()
            elif choix == "2" and self.current_user:
                self.menu_read()
            elif choix == "3" and self.current_user:
                self.menu_write()
            elif choix in ("0", "4"):
                self.print_green("Au revoir.")
                break
            else:
                self.print_red("Option invalide.")

    def menu_login(self):
        self.print_header("\n-- Connexion --")
        email = input(self.CYAN + "Email : " + self.END)
        pwd = input(self.CYAN + "Mot de passe : " + self.END)
        user = self.login_view.login_with_credentials_return_user(email, pwd)
        if user:
            self.current_user = {
                "id": user.id,
                "role": user.role.name,
                "role_id": user.role.id
            }
            self.print_green(f"Connecté en tant que {user.role.name}.")
        else:
            self.print_red("Échec de l'authentification.")

    def menu_read(self):
        role = self.current_user["role"]
        while True:
            self.print_header("\n-- Lecture des données --")
            if role in ("gestion", "commercial"):
                print(self.BLUE + "[1] Clients" + self.END)
                print(self.BLUE + "[2] Contrats" + self.END)
            if role in ("gestion", "commercial", "support"):
                print(self.BLUE + "[3] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1" and role in ("gestion", "commercial"):
                self.reader.display_clients_only(self.current_user)
            elif c == "2" and role in ("gestion", "commercial"):
                self.reader.display_contracts_only(self.current_user)
            elif c == "3" and role in ("gestion", "commercial", "support"):
                self.reader.display_events_only(self.current_user)
            elif c in ("0", "4"):
                break
            else:
                self.print_red("Option invalide.")

    def menu_write(self):
        role = self.current_user["role"]
        while True:
            self.print_header("\n-- Gestion --")
            if role == "gestion":
                print(self.BLUE + "[1] Collaborateurs" + self.END)
            if role in ("gestion", "commercial"):
                print(self.BLUE + "[2] Clients" + self.END)
                print(self.BLUE + "[3] Contrats" + self.END)
            if role in ("gestion", "support"):
                print(self.BLUE + "[4] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1" and role == "gestion":
                self.writer.menu_collaborator(self.current_user)
            elif c == "2" and role in ("gestion", "commercial"):
                self.writer.menu_client(self.current_user)
            elif c == "3" and role in ("gestion", "commercial"):
                self.writer.menu_contract(self.current_user)
            elif c == "4" and role in ("gestion", "support"):
                self.writer.menu_event(self.current_user)
            elif c in ("0", "5"):
                break
            else:
                self.print_red("Option invalide.")
