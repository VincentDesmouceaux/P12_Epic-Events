# app/views/cli_interface.py
from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    """
    Interface CLI interactive regroupant LoginView, DataReaderView et DataWriterView.
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
        print(
            self.BLUE + "[2] Lecture des données (clients, contrats, événements)" + self.END)
        print(
            self.BLUE + "[3] Gestion des collaborateurs / contrats / événements" + self.END)
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
            print(self.BLUE + "[4] Retour" + self.END)
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
            self.print_header(
                "\n-- Gestion des collaborateurs / contrats / événements --")
            print(self.BLUE + "[1] Gérer les collaborateurs" + self.END)
            print(self.BLUE + "[2] Gérer les contrats" + self.END)
            print(self.BLUE + "[3] Gérer les événements" + self.END)
            print(self.BLUE + "[4] Retour" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1":
                self.menu_manage_users()
            elif c == "2":
                self.menu_manage_contracts()
            elif c == "3":
                self.menu_manage_events()
            elif c == "4":
                break
            else:
                self.print_red("Option invalide.")

    def menu_manage_users(self):
        self.print_header("\n-- Gestion des collaborateurs --")
        print(self.BLUE + "[1] Créer un collaborateur" + self.END)
        print(self.BLUE +
              "[2] Modifier un collaborateur (par employee_number)" + self.END)
        print(
            self.BLUE + "[3] Supprimer un collaborateur (par employee_number)" + self.END)
        print(self.BLUE + "[4] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        if choice == "1":
            self.menu_create_user()
        elif choice == "2":
            self.menu_update_user()
        elif choice == "3":
            self.menu_delete_user()
        elif choice == "4":
            return
        else:
            self.print_red("Option invalide.")

    def menu_create_user(self):
        if self.current_user["role"] != "gestion":
            self.print_red(
                "Seul un utilisateur 'gestion' peut créer un collaborateur.")
            return
        self.print_header("\n-- Création d'un collaborateur --")
        # Le numéro d'employé est généré automatiquement
        fname = input(self.CYAN + "Prénom : " + self.END)
        lname = input(self.CYAN + "Nom : " + self.END)
        email = input(self.CYAN + "Email : " + self.END)
        password = input(self.CYAN + "Mot de passe : " + self.END)
        role_id_str = input(
            self.CYAN + "ID du rôle (ex. 3 pour gestion) : " + self.END)
        try:
            role_id = int(role_id_str)
        except ValueError:
            self.print_red("Role ID invalide.")
            return
        self.writer_view.create_user_cli(
            current_user=self.current_user,
            fname=fname,
            lname=lname,
            email=email,
            password=password,
            role_id=role_id
        )

    def menu_update_user(self):
        if self.current_user["role"] != "gestion":
            self.print_red("Seul 'gestion' peut modifier un collaborateur.")
            return
        self.print_header("\n-- Modification d'un collaborateur --")
        emp_num = input(
            self.CYAN + "Employee Number du collaborateur à modifier : " + self.END)
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
        self.writer_view.update_user_cli(self.current_user, emp_num, **updates)

    def menu_delete_user(self):
        if self.current_user["role"] != "gestion":
            self.print_red("Seul 'gestion' peut supprimer un collaborateur.")
            return
        self.print_header("\n-- Suppression d'un collaborateur --")
        emp_num = input(
            self.CYAN + "Employee Number du collaborateur à supprimer : " + self.END)
        self.writer_view.delete_user_cli(self.current_user, emp_num)

    def menu_manage_contracts(self):
        self.print_header("\n-- Gestion des contrats --")
        print(self.BLUE + "[1] Créer un contrat" + self.END)
        print(self.BLUE + "[2] Modifier un contrat" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        if choice == "1":
            self.menu_create_contract()
        elif choice == "2":
            self.menu_update_contract()
        elif choice == "3":
            return
        else:
            self.print_red("Option invalide.")

    def menu_create_contract(self):
        self.print_header("\n-- Création d'un contrat --")
        client_id_str = input(self.CYAN + "ID du client : " + self.END)
        try:
            client_id = int(client_id_str)
        except ValueError:
            self.print_red("Client ID invalide.")
            return
        commercial_id_str = input(self.CYAN + "ID du commercial : " + self.END)
        try:
            commercial_id = int(commercial_id_str)
        except ValueError:
            self.print_red("Commercial ID invalide.")
            return
        total_amount_str = input(self.CYAN + "Montant total : " + self.END)
        try:
            total_amount = float(total_amount_str)
        except ValueError:
            self.print_red("Montant invalide.")
            return
        remaining_amount_str = input(
            self.CYAN + "Montant restant : " + self.END)
        try:
            remaining_amount = float(remaining_amount_str)
        except ValueError:
            self.print_red("Montant restant invalide.")
            return
        is_signed_str = input(
            self.CYAN + "Contrat signé ? (oui/non) : " + self.END).strip().lower()
        is_signed = True if is_signed_str in (
            "oui", "o", "yes", "y") else False
        self.writer_view.create_contract_cli(
            self.current_user, client_id, commercial_id, total_amount, remaining_amount, is_signed)

    def menu_update_contract(self):
        self.print_header("\n-- Modification d'un contrat --")
        contract_id_str = input(
            self.CYAN + "ID du contrat à modifier : " + self.END)
        try:
            contract_id = int(contract_id_str)
        except ValueError:
            self.print_red("Contract ID invalide.")
            return
        remaining_amount_str = input(
            self.CYAN + "Nouveau montant restant : " + self.END)
        try:
            remaining_amount = float(remaining_amount_str)
        except ValueError:
            self.print_red("Montant restant invalide.")
            return
        is_signed_str = input(
            self.CYAN + "Contrat signé ? (oui/non) : " + self.END).strip().lower()
        is_signed = True if is_signed_str in (
            "oui", "o", "yes", "y") else False
        self.writer_view.update_contract_cli(
            self.current_user, contract_id, remaining_amount=remaining_amount, is_signed=is_signed)

    def menu_manage_events(self):
        self.print_header("\n-- Gestion des événements --")
        print(self.BLUE + "[1] Consulter les événements" + self.END)
        print(self.BLUE +
              "[2] Modifier un événement pour assigner un support" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        if choice == "1":
            self.reader_view.display_events_only(self.current_user)
        elif choice == "2":
            self.menu_update_event_for_support()
        elif choice == "3":
            return
        else:
            self.print_red("Option invalide.")

    def menu_update_event_for_support(self):
        self.print_header("\n-- Modification d'un événement --")
        event_id_str = input(self.CYAN + "ID de l'événement : " + self.END)
        try:
            event_id = int(event_id_str)
        except ValueError:
            self.print_red("Event ID invalide.")
            return
        support_id_str = input(
            self.CYAN + "ID du collaborateur support à assigner : " + self.END)
        try:
            support_id = int(support_id_str)
        except ValueError:
            self.print_red("Support ID invalide.")
            return
        self.writer_view.update_event_cli(
            self.current_user, event_id, support_id=support_id)
