# app/views/cli_interface.py
from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
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
            self.current_user = {
                "id": user.id, "role": user.role.name, "role_id": getattr(user.role, "id", 3)}
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
            self.print_header(
                "\n-- Gestion des collaborateurs / contrats / événements --")
            print(
                self.BLUE + "[1] Créer / Modifier / Supprimer un collaborateur" + self.END)
            print(self.BLUE + "[2] Créer / Modifier un contrat" + self.END)
            print(
                self.BLUE + "[3] Consulter / Modifier un événement (assigner support)" + self.END)
            print(self.BLUE + "[4] Retour menu principal" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            if c == "1":
                self.menu_collaborator()
            elif c == "2":
                self.menu_contract()
            elif c == "3":
                self.menu_event()
            elif c == "4":
                break
            else:
                self.print_red("Option invalide.")

    def menu_contract(self):
        self.print_header("\n-- Gestion des contrats --")
        print(self.BLUE + "[1] Créer un contrat" + self.END)
        print(self.BLUE + "[2] Modifier un contrat" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        if choice == "1":
            client_id_str = input(self.CYAN + "ID du client : " + self.END)
            try:
                client_id = int(client_id_str)
            except:
                self.print_red("ID client invalide.")
                return
            total_amount_str = input(self.CYAN + "Montant total : " + self.END)
            remaining_amount_str = input(
                self.CYAN + "Montant restant : " + self.END)
            try:
                total_amount = float(total_amount_str)
                remaining_amount = float(remaining_amount_str)
            except:
                self.print_red("Montants invalides.")
                return
            signed_str = input(
                self.CYAN + "Contrat signé ? (O/N) : " + self.END).strip().upper()
            is_signed = True if signed_str == "O" else False
            session = self.db_connection.create_session()
            try:
                contract = self.writer_view.writer.create_contract(
                    session,
                    self.current_user,
                    client_id,
                    total_amount,
                    remaining_amount,
                    is_signed
                )
                self.print_green("Contrat créé avec ID = " + str(contract.id))
            except Exception as e:
                self.print_red(
                    "Erreur lors de la création du contrat : " + str(e))
                session.rollback()
            finally:
                session.close()
        elif choice == "2":
            contract_id_str = input(
                self.CYAN + "ID du contrat à modifier : " + self.END)
            try:
                contract_id = int(contract_id_str)
            except:
                self.print_red("ID contrat invalide.")
                return
            total_amount_str = input(
                self.CYAN + "Nouveau montant total : " + self.END)
            remaining_amount_str = input(
                self.CYAN + "Nouveau montant restant : " + self.END)
            signed_str = input(
                self.CYAN + "Contrat signé ? (O/N) : " + self.END).strip().upper()
            try:
                total_amount = float(total_amount_str)
                remaining_amount = float(remaining_amount_str)
            except:
                self.print_red("Montants invalides.")
                return
            is_signed = True if signed_str == "O" else False
            session = self.db_connection.create_session()
            try:
                updated_contract = self.writer_view.writer.update_contract(
                    session,
                    self.current_user,
                    contract_id,
                    total_amount=total_amount,
                    remaining_amount=remaining_amount,
                    is_signed=is_signed
                )
                self.print_green("Contrat mis à jour, montant total = " + str(updated_contract.total_amount) +
                                 ", montant restant = " + str(updated_contract.remaining_amount))
            except Exception as e:
                self.print_red(
                    "Erreur lors de la modification du contrat : " + str(e))
                session.rollback()
            finally:
                session.close()
        elif choice == "3":
            return
        else:
            self.print_red("Option invalide.")

    def menu_event(self):
        self.print_header("\n-- Gestion des événements --")
        print(self.BLUE +
              "[1] Consulter les événements sans support" + self.END)
        print(self.BLUE +
              "[2] Modifier un événement pour assigner un support" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        if choice == "1":
            session = self.db_connection.create_session()
            try:
                from app.models.event import Event
                events = session.query(Event).filter(
                    Event.support_id == None).all()
                if events:
                    self.print_green("Événements sans support:")
                    for event in events:
                        self.print_blue(self.reader_view.format_entity(event))
                else:
                    self.print_yellow("Aucun événement sans support.")
            except Exception as e:
                self.print_red("Erreur lors de la consultation : " + str(e))
            finally:
                session.close()
        elif choice == "2":
            event_id_str = input(
                self.CYAN + "ID de l'événement à modifier : " + self.END)
            try:
                event_id = int(event_id_str)
            except:
                self.print_red("ID invalide.")
                return
            # Demander l'employee_number du collaborateur support
            emp_number = input(
                self.CYAN + "Employee Number du collaborateur support à assigner : " + self.END).strip()
            if not emp_number:
                self.print_red("Employee Number invalide.")
                return
            session = self.db_connection.create_session()
            try:
                from app.models.user import User
                support_user = session.query(User).filter_by(
                    employee_number=emp_number).first()
                if not support_user:
                    self.print_red(
                        "Aucun collaborateur trouvé avec cet employee_number.")
                    session.close()
                    return
                updated_event = self.writer_view.writer.update_event(
                    session,
                    self.current_user,
                    event_id,
                    support_id=support_user.id
                )
                self.print_green(
                    "Événement mis à jour, support assigné = " + support_user.employee_number)
            except Exception as e:
                self.print_red(
                    "Erreur lors de la modification de l'événement : " + str(e))
                session.rollback()
            finally:
                session.close()
        elif choice == "3":
            return
        else:
            self.print_red("Option invalide.")

    def menu_collaborator(self):
        self.print_header("\n-- Gestion des collaborateurs --")
        print(self.BLUE + "[1] Créer un collaborateur" + self.END)
        print(self.BLUE + "[2] Modifier un collaborateur" + self.END)
        print(self.BLUE + "[3] Supprimer un collaborateur" + self.END)
        print(self.BLUE + "[4] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        if choice == "1":
            fname = input(self.CYAN + "Prénom : " + self.END)
            lname = input(self.CYAN + "Nom : " + self.END)
            email = input(self.CYAN + "Email : " + self.END)
            password = input(self.CYAN + "Mot de passe : " + self.END)
            role_id_str = input(
                self.CYAN + "ID du rôle (1=commercial, 2=support, 3=gestion) : " + self.END)
            try:
                role_id = int(role_id_str)
            except ValueError:
                self.print_red("Role ID invalide.")
                return
            self.current_user["role_id"] = role_id
            self.writer_view.create_user_cli(
                self.current_user, fname, lname, email, password)
        elif choice == "2":
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
            self.writer_view.update_user_cli(
                self.current_user, emp_num, **updates)
        elif choice == "3":
            emp_num = input(
                self.CYAN + "Employee Number du collaborateur à supprimer : " + self.END)
            session = self.db_connection.create_session()
            try:
                result = self.writer_view.writer.delete_user(
                    session, self.current_user, emp_num)
                if result:
                    self.print_green("Collaborateur supprimé avec succès.")
            except Exception as e:
                self.print_red("Erreur lors de la suppression : " + str(e))
                session.rollback()
            finally:
                session.close()
        elif choice == "4":
            return


if __name__ == "__main__":
    from app.config.database import DatabaseConfig, DatabaseConnection
    db_config = DatabaseConfig()
    db_connection = DatabaseConnection(db_config)
    cli = CLIInterface(db_connection)
    cli.run()
