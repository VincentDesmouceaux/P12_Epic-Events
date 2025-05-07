# -*- coding: utf-8 -*-
"""
CLIInterface – navigation adaptée au rôle connecté
• gestion    : collaborateurs / clients / contrats / événements
• commercial : clients / contrats / événements
• support    : événements (écriture) — MAIS lecture COMPLETE :
               tous les collaborateurs voient Clients, Contrats, Événements
"""
from __future__ import annotations

from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.login_v = LoginView(db_connection)
        self.reader_v = DataReaderView(db_connection)
        self.writer_v = DataWriterView(db_connection)
        self.current_user: dict | None = None

    # ------------------------------------------------------------------ #
    #  MENU PRINCIPAL
    # ------------------------------------------------------------------ #
    def _main_menu(self) -> None:
        self.print_header("\n======== Epic Events CLI ========")
        print(self.BLUE + "[1] Se connecter" + self.END)
        if self.current_user:
            print(self.BLUE + "[2] Lecture des données" + self.END)
            print(self.BLUE + "[3] Gestion / Écriture" + self.END)
        print(self.BLUE + "[0] Quitter" + self.END)

    def run(self) -> None:
        while True:
            self._main_menu()
            choice = input(self.CYAN + "Choix : " + self.END).strip()
            match choice:
                case "1":
                    self._login()
                case "2" if self.current_user:
                    self._read_menu()
                case "3" if self.current_user:
                    self._write_menu()
                case "0":
                    self.print_green("Au revoir.")
                    break
                case _:
                    self.print_red("Option invalide.")

    # ------------------------------------------------------------------ #
    #  AUTHENTIFICATION
    # ------------------------------------------------------------------ #
    def _login(self) -> None:
        self.print_header("-- Connexion --")
        mail = input(self.CYAN + "Email : " + self.END).strip()
        pwd = input(self.CYAN + "Mot de passe : " + self.END).strip()
        user = self.login_v.login_with_credentials_return_user(mail, pwd)
        if user:
            self.current_user = {"id": user.id,
                                 "role": user.role.name,
                                 "role_id": user.role.id}
            self.print_green(f"Connecté – rôle {user.role.name}")
        else:
            self.print_red("Échec de l’authentification.")

    # ------------------------------------------------------------------ #
    #  LECTURE (des données) — mêmes choix pour tous les rôles
    # ------------------------------------------------------------------ #
    def _read_menu(self) -> None:
        while True:
            self.print_header("-- Lecture des données --")
            print(self.BLUE + "[1] Clients" + self.END)
            print(self.BLUE + "[2] Contrats" + self.END)
            print(self.BLUE + "[3] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            c = input(self.CYAN + "Choix : " + self.END).strip()
            try:
                match c:
                    case "1":
                        self.reader_v.display_clients_only(self.current_user)
                    case "2":
                        self.reader_v.display_contracts_only(self.current_user)
                    case "3":
                        self.reader_v.display_events_only(self.current_user)
                    case "0":
                        break
                    case _:
                        self.print_red("Option invalide.")
            except Exception as exc:                       # pragma: no cover
                self.print_red(str(exc))

    # ------------------------------------------------------------------ #
    #  GESTION / ÉCRITURE
    # ------------------------------------------------------------------ #
    def _write_menu(self) -> None:
        role = self.current_user["role"]
        while True:
            self.print_header("-- Gestion --")
            options: list[tuple[str, str, callable]] = []

            if role == "gestion":
                options += [
                    ("1", "Collaborateurs", self._menu_collaborator),
                    ("2", "Contrats",       self._menu_contract_gestion),
                    ("3", "Événements",     self._menu_event_gestion),
                ]
            elif role == "commercial":
                options += [
                    ("1", "Clients",        self._menu_client),
                    ("2", "Contrats",       self._menu_contract_commercial),
                    ("3", "Événements",     self._menu_event_commercial),
                ]
            else:  # support
                options.append(("1", "Événements", self._menu_event_support))

            for k, label, _ in options:
                print(self.BLUE + f"[{k}] {label}" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            choice = input(self.CYAN + "Choix : " + self.END).strip()
            if choice == "0":
                break
            for k, _lbl, handler in options:
                if choice == k:
                    handler()
                    break
            else:
                self.print_red("Option invalide.")

    # ------------------------------------------------------------------ #
    #  ======= SOUS‑MENUS COMMUNS =======                                #
    # ------------------------------------------------------------------ #
    def _menu_collaborator(self) -> None:
        self.print_header("-- Collaborateurs --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[3] Supprimer" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        match c:
            case "1":
                self.writer_v.create_user_cli(self.current_user)
            case "2":
                self.writer_v.update_user_cli(self.current_user)
            case "3":
                self.writer_v.delete_user_cli(self.current_user)

    def _menu_client(self) -> None:
        self.print_header("-- Clients --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        match c:
            case "1":
                self.writer_v.create_client_cli(self.current_user)
            case "2":
                self.writer_v.update_client_cli(self.current_user)

    # ------------------- CONTRATS (gestion) --------------------------- #
    def _menu_contract_gestion(self) -> None:
        self.print_header("-- Contrats (gestion) --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        match c:
            case "1":
                self.writer_v.create_contract_cli(self.current_user)
            case "2":
                self.writer_v.update_contract_cli(self.current_user)

    # ------------------- CONTRATS (commercial) ------------------------ #
    def _menu_contract_commercial(self) -> None:
        while True:
            self.print_header("-- Contrats (commercial) --")
            print(self.BLUE + "[1] Modifier" + self.END)
            print(self.BLUE + "[2] Affichage" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            match c:
                case "1":
                    self.writer_v.update_contract_cli(self.current_user)
                case "2":
                    self._submenu_contract_display()
                case "0":
                    break
                case _:
                    self.print_red("Option invalide.")

    def _submenu_contract_display(self) -> None:
        while True:
            self.print_header("-- Affichage contrats --")
            print(self.BLUE + "[1] Non signés" + self.END)
            print(self.BLUE + "[2] Restant à payer" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)
            c = input(self.CYAN + "Choix : " + self.END).strip()
            match c:
                case "1":
                    self.reader_v.display_unsigned_contracts(self.current_user)
                case "2":
                    self.reader_v.display_unpaid_contracts(self.current_user)
                case "0":
                    break
                case _:
                    self.print_red("Option invalide.")

    # ------------------- ÉVÉNEMENTS ---------------------------------- #
    def _menu_event_gestion(self) -> None:
        self.print_header("-- Événements (gestion) --")
        print(self.BLUE + "[1] Afficher sans support" + self.END)
        print(self.BLUE + "[2] Assigner / modifier support" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        match c:
            case "1":
                self.writer_v.list_events_no_support(self.current_user)
            case "2":
                self.writer_v.assign_support_cli(self.current_user)

    def _menu_event_commercial(self) -> None:
        self.print_header("-- Événements (commercial) --")
        print(self.BLUE + "[1] Créer un événement" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        c = input(self.CYAN + "Choix : " + self.END).strip()
        if c == "1":
            self.writer_v.create_event_cli(self.current_user)

    def _menu_event_support(self) -> None:
        """Sous‑menu spécialisé hébergé dans DataWriter (rôle support)."""
        self.writer_v.menu_event_support(self.current_user)
