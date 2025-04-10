# app/views/cli_interface.py

from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface:
    """
    Interface CLI réutilisant LoginView, DataReaderView et DataWriterView.
    """

    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.login_view = LoginView(db_connection)
        self.reader_view = DataReaderView(db_connection)
        self.writer_view = DataWriterView(db_connection)
        self.current_user = None

    def run(self):
        while True:
            print("\n======== Epic Events CLI ========")
            print("[1] Se connecter (login)")
            print("[2] Lecture des données (clients, contrats, events)")
            print("[3] Création / mise à jour (DataWriter)")
            print("[4] Quitter")
            choice = input("Choix : ").strip()
            if choice == "1":
                self.menu_login()
            elif choice == "2":
                self.menu_data_reader()
            elif choice == "3":
                self.menu_data_writer()
            elif choice == "4":
                print("Au revoir.")
                break
            else:
                print("Option invalide.")

    def menu_login(self):
        email = input("Email : ")
        password = input("Mot de passe : ")
        user = self.login_view.login_with_credentials_return_user(
            email, password)
        if user:
            self.current_user = {"id": user.id, "role": user.role.name}
            print(f"Authentification réussie. Rôle={user.role.name}")
        else:
            print("Échec de l'authentification.")

    def menu_data_reader(self):
        if not self.current_user:
            print("Veuillez vous connecter d'abord.")
            return
        while True:
            print("\n-- Lecture des données --")
            print("[1] Lister les clients")
            print("[2] Lister les contrats")
            print("[3] Lister les événements")
            print("[4] Retour menu principal")
            c = input("Choix : ").strip()
            if c == "1":
                self.reader_view.display_clients_only(self.current_user)
            elif c == "2":
                self.reader_view.display_contracts_only(self.current_user)
            elif c == "3":
                self.reader_view.display_events_only(self.current_user)
            elif c == "4":
                break
            else:
                print("Option invalide.")

    def menu_data_writer(self):
        if not self.current_user:
            print("Veuillez vous connecter d'abord.")
            return
        while True:
            print("\n-- Création / Mise à jour --")
            print("[1] Créer un user (collaborateur)")
            print("[2] Mettre à jour un user")
            print("[3] (Autres actions : créer client, contrat, etc.)")
            print("[4] Retour menu principal")
            c = input("Choix : ").strip()
            if c == "1":
                self.menu_create_user()
            elif c == "2":
                self.menu_update_user()
            elif c == "3":
                print("Non implémenté dans l'exemple, mais même principe.")
            elif c == "4":
                break
            else:
                print("Option invalide.")

    def menu_create_user(self):
        if self.current_user["role"] != "gestion":
            print("Seul un utilisateur 'gestion' peut créer un user.")
            return
        empnum = input("Numéro employé : ")
        fname = input("Prénom : ")
        lname = input("Nom : ")
        email = input("Email : ")
        pwd_hash = input("Hash du mot de passe (ou 'hashed_value') : ")
        role_id_str = input("ID du rôle (ex. 2=commercial) : ")
        try:
            role_id = int(role_id_str)
        except ValueError:
            print("Role ID invalide.")
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
            print("Seul 'gestion' peut update un user.")
            return
        user_id_str = input("ID du user à modifier : ")
        try:
            user_id = int(user_id_str)
        except ValueError:
            print("User ID invalide.")
            return
        fname = input("Nouveau prénom (laisser vide si inchangé) : ")
        lname = input("Nouveau nom (laisser vide si inchangé) : ")
        email = input("Nouvel email (laisser vide si inchangé) : ")
        updates = {}
        if fname.strip():
            updates["first_name"] = fname
        if lname.strip():
            updates["last_name"] = lname
        if email.strip():
            updates["email"] = email
        self.writer_view.update_user_cli(self.current_user, user_id, **updates)
