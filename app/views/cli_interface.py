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
        print(self.BLUE + "[2] Lecture des données" + self.END)
        print(self.BLUE + "[3] Gestion écriture" + self.END)
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
        email = input(self.CYAN + "Email : " + self.END).strip()
        password = input(self.CYAN + "Mot de passe : " + self.END).strip()
        user = self.login_view.login_with_credentials_return_user(
            email, password)
        if user:
            # On stocke à la fois le rôle en string et son ID numérique
            self.current_user = {
                "id": user.id,
                "role": user.role.name,
                "role_id": user.role.id
            }
            self.print_green(
                f"Authentification réussie. Rôle = {user.role.name}")
        else:
            self.print_red("Échec de l’authentification.")

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
                try:
                    self.reader_view.display_clients_only(self.current_user)
                except Exception as e:
                    self.print_red(str(e))
            elif c == "2":
                try:
                    self.reader_view.display_contracts_only(self.current_user)
                except Exception as e:
                    self.print_red(str(e))
            elif c == "3":
                try:
                    self.reader_view.display_events_only(self.current_user)
                except Exception as e:
                    self.print_red(str(e))
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
            print(self.BLUE + "[1] Collaborateurs" + self.END)
            print(self.BLUE + "[2] Contrats" + self.END)
            print(self.BLUE + "[3] Événements" + self.END)
            print(self.BLUE + "[4] Retour" + self.END)
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

    def menu_collaborator(self):
        self.print_header("\n-- Gestion des collaborateurs --")
        print(self.BLUE + "[1] Créer un collaborateur" + self.END)
        print(self.BLUE + "[2] Modifier un collaborateur" + self.END)
        print(self.BLUE + "[3] Supprimer un collaborateur" + self.END)
        print(self.BLUE + "[4] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()

        if choice == "1":
            fname = input(self.CYAN + "Prénom : " + self.END).strip()
            lname = input(self.CYAN + "Nom : " + self.END).strip()
            email = input(self.CYAN + "Email : " + self.END).strip()
            pwd = input(self.CYAN + "Mot de passe : " + self.END).strip()
            try:
                rid = int(
                    input(self.CYAN + "ID rôle (1=C,2=S,3=G) : " + self.END))
            except ValueError:
                self.print_red("Role ID invalide.")
                return
            try:
                self.writer_view.create_user_cli(
                    self.current_user,
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    password=pwd,
                    role_id=rid
                )
            except Exception as e:
                self.print_red(str(e))

        elif choice == "2":
            emp_num = input(
                self.CYAN + "Employee Number : " + self.END).strip()
            fname = input(
                self.CYAN + "Nouveau prénom (vide si aucun) : " + self.END).strip()
            lname = input(
                self.CYAN + "Nouveau nom (vide si aucun) : " + self.END).strip()
            email = input(
                self.CYAN + "Nouvel email (vide si aucun) : " + self.END).strip()
            updates = {}
            if fname:
                updates["first_name"] = fname
            if lname:
                updates["last_name"] = lname
            if email:
                updates["email"] = email
            if not updates:
                self.print_yellow("Aucune modification renseignée.")
                return
            try:
                self.writer_view.update_user_cli(
                    self.current_user, emp_num, **updates
                )
            except Exception as e:
                self.print_red(str(e))

        elif choice == "3":
            emp_num = input(
                self.CYAN + "Employee Number à supprimer : " + self.END).strip()
            try:
                self.writer_view.delete_user_cli(self.current_user, emp_num)
                self.print_green("Collaborateur supprimé.")
            except Exception as e:
                self.print_red(str(e))

        elif choice == "4":
            return
        else:
            self.print_red("Option invalide.")

    def menu_contract(self):
        self.print_header("\n-- Gestion des contrats --")
        print(self.BLUE + "[1] Créer un contrat" + self.END)
        print(self.BLUE + "[2] Modifier un contrat" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()

        if choice == "1":
            try:
                client_id = int(input(self.CYAN + "ID client : " + self.END))
                total = float(input(self.CYAN + "Montant total : " + self.END))
                remaining = float(
                    input(self.CYAN + "Montant restant : " + self.END))
            except ValueError:
                self.print_red("Valeurs invalides.")
                return
            signed = input(self.CYAN + "Signé ? (O/N) : " +
                           self.END).strip().upper() == "O"
            session = self.db_connection.create_session()
            try:
                ctr = self.writer_view.writer.create_contract(
                    session, self.current_user,
                    client_id, total, remaining, signed
                )
                self.print_green(f"Contrat créé (ID = {ctr.id}).")
            except Exception as e:
                self.print_red(str(e))
                session.rollback()
            finally:
                session.close()

        elif choice == "2":
            try:
                cid = int(input(self.CYAN + "ID contrat : " + self.END))
            except ValueError:
                self.print_red("ID invalide.")
                return
            updates = {}
            new_client = input(
                self.CYAN + "Nouvel ID client (vide si aucun) : " + self.END).strip()
            if new_client:
                try:
                    updates["client_id"] = int(new_client)
                except ValueError:
                    self.print_red("ID client invalide.")
                    return
            empn = input(
                self.CYAN + "Employee Number commercial (vide si aucun) : " + self.END).strip()
            if empn:
                # DataWriterView traduira en commercial_id
                updates["commercial_emp"] = empn
            total = input(
                self.CYAN + "Nouveau montant total (vide si aucun) : " + self.END).strip()
            if total:
                try:
                    updates["total_amount"] = float(total)
                except ValueError:
                    self.print_red("Montant invalide.")
                    return
            rem = input(
                self.CYAN + "Nouveau montant restant (vide si aucun) : " + self.END).strip()
            if rem:
                try:
                    updates["remaining_amount"] = float(rem)
                except ValueError:
                    self.print_red("Montant invalide.")
                    return
            sig = input(
                self.CYAN + "Signé ? (O/N, vide si aucun) : " + self.END).strip().upper()
            if sig == "O":
                updates["is_signed"] = True
            elif sig == "N":
                updates["is_signed"] = False

            if not updates:
                self.print_yellow("Aucune modification renseignée.")
                return

            session = self.db_connection.create_session()
            try:
                upd = self.writer_view.update_contract_cli(
                    self.current_user, cid, **updates
                )
                self.print_green(f"Contrat #{upd.id} mis à jour.")
            except Exception as e:
                self.print_red(str(e))
                session.rollback()
            finally:
                session.close()

        else:
            # choix "3" ou autre => retour
            return

    def menu_event(self):
        self.print_header("\n-- Gestion des événements --")
        print(self.BLUE + "[1] Événements sans support" + self.END)
        print(self.BLUE + "[2] Assigner un support" + self.END)
        print(self.BLUE + "[3] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()

        if choice == "1":
            session = self.db_connection.create_session()
            try:
                evs = session.query(__import__('app.models.event').models.event.Event).filter_by(
                    support_id=None).all()
                if evs:
                    self.print_green("Événements sans support :")
                    for e in evs:
                        self.print_blue(self.reader_view.format_entity(e))
                else:
                    self.print_yellow("Aucun événement sans support.")
            finally:
                session.close()

        elif choice == "2":
            try:
                eid = int(input(self.CYAN + "ID événement : " + self.END))
            except ValueError:
                self.print_red("ID invalide.")
                return
            empn = input(
                self.CYAN + "Employee Number du support : " + self.END).strip()
            session = self.db_connection.create_session()
            try:
                ev = self.writer_view.assign_support_cli(
                    self.current_user, eid, empn
                )
                self.print_green(f"Événement #{ev.id} assigné à {empn}.")
            except Exception as e:
                self.print_red(str(e))
                session.rollback()
            finally:
                session.close()

        else:
            # choix "3" ou invalide => retour
            return


if __name__ == "__main__":
    from app.config.database import DatabaseConfig, DatabaseConnection
    cfg = DatabaseConfig()
    conn = DatabaseConnection(cfg)
    CLIInterface(conn).run()
