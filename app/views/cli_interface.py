"""
CLIInterface – menu adapté à chaque rôle
========================================
• gestion    : tout voir / tout gérer
• commercial : lire tout, gérer clients + contrats + créer événements
• support    : lire tout, gérer événements (mise à jour / assignation)
"""

from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.login_v = LoginView(db_connection)
        self.reader_v = DataReaderView(db_connection)
        self.writer_v = DataWriterView(db_connection)
        self.current_user = None

    # ------------------------------------------------------------------ #
    #  menu principal
    # ------------------------------------------------------------------ #
    def _main_menu(self):
        self.print_header("\n======== Epic Events CLI ========")
        print(self.BLUE + "[1] Se connecter" + self.END)
        if self.current_user:
            print(self.BLUE + "[2] Lecture des données" + self.END)
            print(self.BLUE + "[3] Gestion écriture" + self.END)
        print(self.BLUE + "[0] Quitter" + self.END)

    def run(self):
        while True:
            self._main_menu()
            ch = input(self.CYAN + "Choix : " + self.END).strip()
            if ch == "1":
                self._login_menu()
            elif ch == "2" and self.current_user:
                self._read_menu()
            elif ch == "3" and self.current_user:
                self._write_menu()
            elif ch == "0":
                self.print_green("Au revoir.")
                break
            else:
                self.print_red("Option invalide.")

    # ------------------------------------------------------------------ #
    #  authentification
    # ------------------------------------------------------------------ #
    def _login_menu(self):
        self.print_header("-- Connexion --")
        mail = input(self.CYAN + "Email : " + self.END).strip()
        pwd = input(self.CYAN + "Mot de passe : " + self.END).strip()
        u = self.login_v.login_with_credentials_return_user(mail, pwd)
        if u:
            self.current_user = {
                "id": u.id,
                "role": u.role.name,
                "role_id": u.role.id,
            }
            self.print_green(f"Authentification réussie : rôle {u.role.name}")
        else:
            self.print_red("Échec de connexion.")

    # ------------------------------------------------------------------ #
    #  lecture seule
    # ------------------------------------------------------------------ #
    def _read_menu(self):
        while True:
            self.print_header("-- Lecture des données --")
            print(self.BLUE + "[1] Clients" + self.END)
            print(self.BLUE + "[2] Contrats" + self.END)
            print(self.BLUE + "[3] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            try:
                if c == "1":
                    self.reader_v.display_clients_only(self.current_user)
                elif c == "2":
                    self.reader_v.display_contracts_only(self.current_user)
                elif c == "3":
                    self.reader_v.display_events_only(self.current_user)
                elif c == "0":
                    break
                else:
                    self.print_red("Option invalide.")
            except Exception as e:
                self.print_red(str(e))

    # ------------------------------------------------------------------ #
    #  écriture / gestion   (menu ajusté selon le rôle)
    # ------------------------------------------------------------------ #
    def _write_menu(self):
        role = self.current_user["role"]
        while True:
            self.print_header("-- Gestion --")

            # -------------------------- gestion ------------------------- #
            if role == "gestion":
                print(self.BLUE + "[1] Collaborateurs" + self.END)

            # ----------- gestion & commercial : clients + contrats ------ #
            if role in ("gestion", "commercial"):
                print(self.BLUE + "[2] Clients" + self.END)
                print(self.BLUE + "[3] Contrats" + self.END)

            # ----------- gestion & support : événements ----------------- #
            if role in ("gestion", "commercial", "support"):
                print(self.BLUE + "[4] Événements" + self.END)

            print(self.BLUE + "[0] Retour" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()

            # ----------------------- collaborateurs -------------------- #
            if c == "1" and role == "gestion":
                self._menu_collaborator()

            # -------------------------- clients ------------------------- #
            elif c == "2" and role in ("gestion", "commercial"):
                self._menu_client()

            # ------------------------- contrats ------------------------- #
            elif c == "3" and role in ("gestion", "commercial"):
                self._menu_contract()

            # ------------------------ événements ------------------------ #
            elif c == "4" and role in ("gestion", "commercial", "support"):
                self._menu_event()

            elif c == "0":
                break
            else:
                self.print_red("Option invalide.")

    # ------------------------------------------------------------------ #
    #  sous-menus (appels DataWriterView)                                #
    # ------------------------------------------------------------------ #
    def _menu_collaborator(self):
        self.print_header("-- Collaborateurs --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[3] Supprimer" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        if c == "1":
            self.writer_v.create_user_cli(self.current_user)
        elif c == "2":
            self.writer_v.update_user_cli(self.current_user)
        elif c == "3":
            self.writer_v.delete_user_cli(self.current_user)

    def _menu_client(self):
        self.print_header("-- Clients --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        if c == "1":
            self.writer_v.create_client_cli(self.current_user)
        elif c == "2":
            self.writer_v.update_client_cli(self.current_user)

    def _menu_contract(self):
        self.print_header("-- Contrats --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        if c == "1":
            self.writer_v.create_contract_cli(self.current_user)
        elif c == "2":
            self.writer_v.update_contract_cli(self.current_user)

    def _menu_event(self):
        self.print_header("-- Événements --")
        role = self.current_user["role"]
        if role in ("gestion", "commercial"):
            print(self.BLUE + "[1] Créer un événement" + self.END)
        print(self.BLUE + "[2] Assigner/modifier support" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        if c == "1" and role in ("gestion", "commercial"):
            self.writer_v.create_event_cli(self.current_user)
        elif (c == "1" and role == "support") or c == "2":
            # support n’a que cette option
            self.writer_v.assign_support_cli(self.current_user)
