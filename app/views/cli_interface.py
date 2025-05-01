"""
CLIInterface – menus adaptés au rôle connecté
• gestion    : collaborateurs / contrats / événements
• commercial : clients / contrats / événements
• support    : événements uniquement
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

    # =============== MENU PRINCIPAL ===============
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
            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1":
                self._login()
            elif c == "2" and self.current_user:
                self._read_menu()
            elif c == "3" and self.current_user:
                self._write_menu()
            elif c == "0":
                self.print_green("Au revoir.")
                break
            else:
                self.print_red("Option invalide.")

    # =============== AUTH =========================
    def _login(self):
        self.print_header("-- Connexion --")
        mail = input(self.CYAN + "Email : " + self.END).strip()
        pwd = input(self.CYAN + "Mot de passe : " + self.END).strip()
        u = self.login_v.login_with_credentials_return_user(mail, pwd)
        if u:
            self.current_user = {"id": u.id, "role": u.role.name,
                                 "role_id": u.role.id}
            self.print_green(f"Connecté – rôle {u.role.name}")
        else:
            self.print_red("Échec de l’authentification.")

    # =============== LECTURE ======================
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

    # =============== ÉCRITURE / GESTION ===========
    def _write_menu(self):
        role = self.current_user["role"]
        while True:
            self.print_header("-- Gestion --")

            options = []       # (key, label, handler)

            if role == "gestion":
                options += [
                    ("1", "Collaborateurs", self._menu_collaborator),
                    ("2", "Contrats",       self._menu_contract),
                    ("3", "Événements",     self._menu_event),
                ]
            elif role == "commercial":
                options += [
                    ("1", "Clients",        self._menu_client),
                    ("2", "Contrats",       self._menu_contract),
                    ("3", "Événements",     self._menu_event),
                ]
            else:   # support
                options.append(("1", "Événements", self._menu_event))

            for key, label, _ in options:
                print(self.BLUE + f"[{key}] {label}" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            choice = input(self.CYAN + "Choix : " + self.END).strip()
            if choice == "0":
                break
            for key, _, handler in options:
                if choice == key:
                    handler()
                    break
            else:
                self.print_red("Option invalide.")

    # -------- sous-menus appelant DataWriterView --------
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

    # -------------------- ÉVÉNEMENTS --------------------
    def _menu_event(self):
        self.print_header("-- Événements --")
        print(self.BLUE + "[1] Afficher sans support" + self.END)
        print(self.BLUE + "[2] Assigner / modifier support" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)

        c = input(self.CYAN + "Choix : " + self.END).strip()
        if c == "1":
            self.writer_v.list_events_no_support(self.current_user)
        elif c == "2":
            self.writer_v.assign_support_cli(self.current_user)
