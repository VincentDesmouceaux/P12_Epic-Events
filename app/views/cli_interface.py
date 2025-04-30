# -*- coding: utf-8 -*-
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
            self.BLUE + "[2] Lecture des donnees (clients, contrats, evenements)" + self.END)
        print(
            self.BLUE + "[3] Gestion des collaborateurs / contrats / evenements" + self.END)
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
                "id": user.id,
                "role": user.role.name,
                "role_id": getattr(user.role, "id", 3)
            }
            self.print_green(
                f"Authentification reussie. Role = {user.role.name}")
        else:
            self.print_red("Echec de l'authentification.")

    def menu_data_reader(self):
        if not self.current_user:
            self.print_red("Veuillez vous connecter d'abord.")
            return
        while True:
            self.print_header("\n-- Lecture des donnees --")
            print(self.BLUE + "[1] Lister les clients" + self.END)
            print(self.BLUE + "[2] Lister les contrats" + self.END)
            print(self.BLUE + "[3] Lister les evenements" + self.END)
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
                "\n-- Gestion des collaborateurs / contrats / evenements --")
            print(self.BLUE + "[1] Collaborateurs" + self.END)
            print(self.BLUE + "[2] Contrats" + self.END)
            print(self.BLUE + "[3] Evenements" + self.END)
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
        print(self.BLUE + "[1] Creer un contrat" + self.END)
        print(self.BLUE + "[2] Modifier un contrat" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()

        if choice == "1":
            # Creation
            try:
                client_id = int(
                    input(self.CYAN + "ID du client : " + self.END))
                total_amount = float(
                    input(self.CYAN + "Montant total : " + self.END))
                remaining_amount = float(
                    input(self.CYAN + "Montant restant : " + self.END))
            except ValueError:
                self.print_red("Valeurs invalides.")
                return
            is_signed = input(
                self.CYAN + "Contrat signe ? (O/N) : " + self.END).strip().upper() == "O"

            session = self.db_connection.create_session()
            try:
                ctr = self.writer_view.writer.create_contract(
                    session, self.current_user,
                    client_id, total_amount, remaining_amount, is_signed
                )
                self.print_green(f"Contrat cree avec ID = {ctr.id}")
            except Exception as e:
                self.print_red("Erreur creation contrat : " + str(e))
                session.rollback()
            finally:
                session.close()

        elif choice == "2":
            # Modification
            try:
                contract_id = int(
                    input(self.CYAN + "ID du contrat a modifier : " + self.END))
            except ValueError:
                self.print_red("ID contrat invalide.")
                return

            updates = {}
            # Client
            cid = input(
                self.CYAN + "Nouvel ID client (vide si aucun) : " + self.END).strip()
            if cid:
                try:
                    updates["client_id"] = int(cid)
                except ValueError:
                    self.print_red("ID client invalide.")
                    return

            # Commercial par employee_number
            emp = input(
                self.CYAN + "Employee Number du commercial (Cxxx) (vide si aucun) : " + self.END).strip()
            if emp:
                session = self.db_connection.create_session()
                from app.models.user import User
                usr = session.query(User).filter_by(
                    employee_number=emp).first()
                session.close()
                if not usr:
                    self.print_red(
                        "Aucun commercial pour cet employee_number.")
                    return
                updates["commercial_id"] = usr.id

            # Montants
            ta = input(
                self.CYAN + "Nouveau montant total (vide si aucun) : " + self.END).strip()
            if ta:
                try:
                    updates["total_amount"] = float(ta)
                except ValueError:
                    self.print_red("Montant total invalide.")
                    return

            ra = input(
                self.CYAN + "Nouveau montant restant (vide si aucun) : " + self.END).strip()
            if ra:
                try:
                    updates["remaining_amount"] = float(ra)
                except ValueError:
                    self.print_red("Montant restant invalide.")
                    return

            sig = input(
                self.CYAN + "Contrat signe ? (O/N, vide si aucun) : " + self.END).strip().upper()
            if sig == "O":
                updates["is_signed"] = True
            elif sig == "N":
                updates["is_signed"] = False

            if not updates:
                self.print_yellow("Aucune modification renseignee.")
                return

            session = self.db_connection.create_session()
            try:
                u = self.writer_view.writer.update_contract(
                    session, self.current_user, contract_id, **updates
                )
                desc = ", ".join(f"{k}={v}" for k, v in updates.items())
                self.print_green(f"Contrat #{u.id} mis a jour ({desc}).")
            except Exception as e:
                self.print_red("Erreur modification contrat : " + str(e))
                session.rollback()
            finally:
                session.close()

        elif choice == "3":
            return
        else:
            self.print_red("Option invalide.")

    def menu_event(self):
        self.print_header("\n-- Gestion des evenements --")
        print(self.BLUE + "[1] Evenements sans support" + self.END)
        print(self.BLUE + "[2] Assigner support a un evenement" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()

        if choice == "1":
            session = self.db_connection.create_session()
            try:
                from app.models.event import Event
                evs = session.query(Event).filter(
                    Event.support_id == None).all()
                if evs:
                    self.print_green("Evenements sans support :")
                    for ev in evs:
                        self.print_blue(self.reader_view.format_entity(ev))
                else:
                    self.print_yellow("Aucun evenement sans support.")
            finally:
                session.close()

        elif choice == "2":
            try:
                eid = int(
                    input(self.CYAN + "ID de l'evenement a modifier : " + self.END))
            except ValueError:
                self.print_red("ID invalide.")
                return
            emp = input(
                self.CYAN + "Employee Number du support a assigner : " + self.END).strip()
            if not emp:
                self.print_red("Employee Number invalide.")
                return

            session = self.db_connection.create_session()
            try:
                from app.models.user import User
                u = session.query(User).filter_by(employee_number=emp).first()
                if not u:
                    self.print_red("Aucun support pour cet employee_number.")
                    return
                ev = self.writer_view.writer.update_event(
                    session, self.current_user, eid, support_id=u.id
                )
                self.print_green(
                    f"Evenement #{ev.id} assigne a {u.employee_number}")
            except Exception as e:
                self.print_red("Erreur assignment support : " + str(e))
                session.rollback()
            finally:
                session.close()

        elif choice == "3":
            return
        else:
            self.print_red("Option invalide.")

    def menu_collaborator(self):
        self.print_header("\n-- Gestion des collaborateurs --")
        print(self.BLUE + "[1] Creer un collaborateur" + self.END)
        print(self.BLUE + "[2] Modifier un collaborateur" + self.END)
        print(self.BLUE + "[3] Supprimer un collaborateur" + self.END)
        print(self.BLUE + "[4] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()

        if choice == "1":
            fname = input(self.CYAN + "Prenom : " + self.END)
            lname = input(self.CYAN + "Nom : " + self.END)
            email = input(self.CYAN + "Email : " + self.END)
            pwd = input(self.CYAN + "Mot de passe : " + self.END)
            try:
                rid = int(
                    input(self.CYAN + "ID role (1=C,2=S,3=G): " + self.END))
            except ValueError:
                self.print_red("Role ID invalide.")
                return
            self.current_user["role_id"] = rid
            self.writer_view.create_user_cli(
                self.current_user, fname, lname, email, pwd)

        elif choice == "2":
            emp = input(
                self.CYAN + "Employee Number du collaborateur : " + self.END).strip()
            fname = input(
                self.CYAN + "Nouveau prenom (vide si aucun) : " + self.END)
            lname = input(
                self.CYAN + "Nouveau nom (vide si aucun) : " + self.END)
            email = input(
                self.CYAN + "Nouvel email (vide si aucun) : " + self.END)
            ups = {}
            if fname:
                ups["first_name"] = fname
            if lname:
                ups["last_name"] = lname
            if email:
                ups["email"] = email
            self.writer_view.update_user_cli(self.current_user, emp, **ups)

        elif choice == "3":
            emp = input(
                self.CYAN + "Employee Number a supprimer : " + self.END).strip()
            session = self.db_connection.create_session()
            try:
                if self.writer_view.writer.delete_user(session, self.current_user, emp):
                    self.print_green("Collaborateur supprime.")
            except Exception as e:
                self.print_red("Erreur suppression : " + str(e))
                session.rollback()
            finally:
                session.close()

        elif choice == "4":
            return


if __name__ == "__main__":
    from app.config.database import DatabaseConfig, DatabaseConnection
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    CLIInterface(conn).run()
