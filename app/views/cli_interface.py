# app/views/cli_interface.py

from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    """
    Interface CLI interactive regroupant LoginView, DataReaderView et DataWriterView.
    Hérite de GenericView pour l'affichage en couleur.
    """

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.login_view = LoginView(db_connection)
        self.reader_view = DataReaderView(db_connection)
        self.writer_view = DataWriterView(db_connection)
        self.current_user = None

    def display_main_menu(self):
        self.print_header("\n======== Epic Events CLI ========")
        print(self.BLUE + "[1] Se connecter (login)" + self.END)
        print(self.BLUE +
              "[2] Lecture des données (clients, contrats, events)" + self.END)
        print(self.BLUE + "[3] Création / mise à jour (DataWriter)" + self.END)
        print(self.BLUE + "[4] Quitter" + self.END)

    def run(self):
        while True:
            self.display_main_menu()
            choice = input(self.CYAN + "Choix : " + self.END).strip()
            if choice == "1":
                self.menu_login()
            elif choice == "2":
                self.menu_data_reader()
            elif choice == "3":
                self.menu_data_writer()
            elif choice == "4":
                self.print_green("Au revoir.")
                break
            else:
                self.print_red("Option invalide.")

    def menu_login(self):
        self.print_header("\n-- Connexion --")
        email = input(self.CYAN + "Email : " + self.END)
        password = input(self.CYAN + "Mot de passe : " + self.END)
        user = self.login_view.login_with_credentials_return_user(
            email, password)
        if user:
            self.current_user = {"id": user.id, "role": user.role.name}
            self.print_green(
                f"Authentification réussie. Rôle = {user.role.name}")
        else:
            self.print_red("Échec de l'authentification.")

    def menu_data_reader(self):
        if not self.current_user:
            self.print_red("Veuillez vous connecter d'abord.")
            return
        while True:
            self.print_header("\n-- Lecture des données --")
            print(self.BLUE + "[1] Lister les clients" + self.END)
            print(self.BLUE + "[2] Lister les contrats" + self.END)
            print(self.BLUE + "[3] Lister les événements" + self.END)
            print(self.BLUE + "[4] Retour menu principal" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1":
                self.reader_view.display_clients_only(self.current_user)
            elif c == "2":
                self.reader_view.display_contracts_only(self.current_user)
            elif c == "3":
                self.reader_view.display_events_only(self.current_user)
            elif c == "4":
                break
            else:
                self.print_red("Option invalide.")

    def menu_data_writer(self):
        if not self.current_user:
            self.print_red("Veuillez vous connecter d'abord.")
            return
        while True:
            self.print_header("\n-- Création / Mise à jour --")
            print(self.BLUE + "[1] Créer un user (collaborateur)" + self.END)
            print(self.BLUE + "[2] Mettre à jour un user" + self.END)
            print(
                self.BLUE + "[3] (Autres actions : créer client, contrat, etc.)" + self.END)
            print(self.BLUE + "[4] Retour menu principal" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1":
                self.menu_create_user()
            elif c == "2":
                self.menu_update_user()
            elif c == "3":
                self.print_yellow(
                    "Non implémenté dans l'exemple, mais même principe.")
            elif c == "4":
                break
            else:
                self.print_red("Option invalide.")

    def menu_create_user(self):
        if self.current_user["role"] != "gestion":
            self.print_red("Seul un utilisateur 'gestion' peut créer un user.")
            return
        self.print_header("\n-- Création d'un collaborateur --")
        empnum = input(self.CYAN + "Numéro employé : " + self.END)
        fname = input(self.CYAN + "Prénom : " + self.END)
        lname = input(self.CYAN + "Nom : " + self.END)
        email = input(self.CYAN + "Email : " + self.END)
        pwd_hash = input(self.CYAN + "Hash du mot de passe : " + self.END)
        role_id_str = input(
            self.CYAN + "ID du rôle (ex. 2 = commercial) : " + self.END)
        try:
            role_id = int(role_id_str)
        except ValueError:
            self.print_red("Role ID invalide.")
            return
        self.writer_view.create_user_cli(
            current_user=self.current_user,
            empnum=empnum,
            fname=fname,
            lname=lname,
            email=email,
            password_hash=pwd_hash,
            role_id=role_id
        )

    def menu_update_user(self):
        if self.current_user["role"] != "gestion":
            self.print_red("Seul 'gestion' peut update un user.")
            return
        self.print_header("\n-- Mise à jour d'un collaborateur --")
        user_id_str = input(self.CYAN + "ID du user à modifier : " + self.END)
        try:
            user_id = int(user_id_str)
        except ValueError:
            self.print_red("User ID invalide.")
            return
        fname = input(
            self.CYAN + "Nouveau prénom (laisser vide si inchangé) : " + self.END)
        lname = input(
            self.CYAN + "Nouveau nom (laisser vide si inchangé) : " + self.END)
        email = input(
            self.CYAN + "Nouvel email (laisser vide si inchangé) : " + self.END)
        updates = {}
        if fname.strip():
            updates["first_name"] = fname
        if lname.strip():
            updates["last_name"] = lname
        if email.strip():
            updates["email"] = email
        self.writer_view.update_user_cli(self.current_user, user_id, **updates)
