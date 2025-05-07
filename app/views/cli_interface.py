# app/views/cli_interface.py
# -*- coding: utf-8 -*-
"""
CLI Interface
=============

Interface texte principale de l’application **Epic Events**.  
Le menu affiché dépend du rôle du collaborateur connecté :

* **gestion**    : collaborateurs / clients / contrats / événements  
* **commercial** : clients / contrats / événements  
* **support**    : événements (mais accès *lecture* complet)

Toutes les interactions clavier sont protégées ; aucune trace « debug »
n’est affichée pour garder la sortie propre en production.
"""
from __future__ import annotations

from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    """Point d’entrée CLI ; orchestre les vues Login, Lecture et Écriture."""

    # ------------------------------------------------------------------ #
    # Construction                                                       #
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        """
        Parameters
        ----------
        db_connection :
            Objet fournissant ``create_session()`` pour accéder à la base.
        """
        super().__init__()
        self.db = db_connection
        self.login_v = LoginView(db_connection)
        self.reader_v = DataReaderView(db_connection)
        self.writer_v = DataWriterView(db_connection)
        self.current_user: dict | None = None  # stocke le user connecté

    # ------------------------------------------------------------------ #
    # Menu principal                                                     #
    # ------------------------------------------------------------------ #
    def _main_menu(self) -> None:
        """Affiche le menu racine (connexion / lecture / gestion)."""
        self.print_header("\n======== Epic Events CLI ========")
        print(self.BLUE + "[1] Se connecter" + self.END)
        if self.current_user:
            print(self.BLUE + "[2] Lecture des données" + self.END)
            print(self.BLUE + "[3] Gestion / Écriture" + self.END)
        print(self.BLUE + "[0] Quitter" + self.END)

    def run(self) -> None:
        """Boucle principale ; reste actif jusqu’à *Quitter*."""
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
    # Authentification                                                   #
    # ------------------------------------------------------------------ #
    def _login(self) -> None:
        """Demande e‑mail / mot de passe et initialise *current_user*."""
        self.print_header("-- Connexion --")
        mail = input(self.CYAN + "Email : " + self.END).strip()
        pwd = input(self.CYAN + "Mot de passe : " + self.END).strip()
        user = self.login_v.login_with_credentials_return_user(mail, pwd)
        if user:
            self.current_user = {
                "id": user.id,
                "role": user.role.name,
                "role_id": user.role.id,
            }
            self.print_green(f"Connecté – rôle {user.role.name}")
        else:
            self.print_red("Échec de l’authentification.")

    # ------------------------------------------------------------------ #
    # Lecture                                                            #
    # ------------------------------------------------------------------ #
    def _read_menu(self) -> None:
        """Sous‑menu *Lecture* : mêmes options pour tous les rôles."""
        while True:
            self.print_header("-- Lecture des données --")
            print(self.BLUE + "[1] Clients" + self.END)
            print(self.BLUE + "[2] Contrats" + self.END)
            print(self.BLUE + "[3] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            choice = input(self.CYAN + "Choix : " + self.END).strip()
            try:
                match choice:
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
            except Exception as err:      # protège contre toute levée imprévue
                self.print_red(str(err))

    # ------------------------------------------------------------------ #
    # Gestion / écriture                                                 #
    # ------------------------------------------------------------------ #
    def _write_menu(self) -> None:
        """Sous‑menu *Gestion* : options variables selon le rôle."""
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

            for key, label, _ in options:
                print(self.BLUE + f"[{key}] {label}" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            choice = input(self.CYAN + "Choix : " + self.END).strip()
            if choice == "0":
                break
            for key, _lbl, handler in options:
                if choice == key:
                    handler()
                    break
            else:
                self.print_red("Option invalide.")

    # ------------------------------------------------------------------ #
    # Sous‑menus collaborateur / client                                  #
    # ------------------------------------------------------------------ #
    def _menu_collaborator(self) -> None:
        """CRUD basique sur les collaborateurs (rôle *gestion* seulement)."""
        self.print_header("-- Collaborateurs --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[3] Supprimer" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        match choice:
            case "1":
                self.writer_v.create_user_cli(self.current_user)
            case "2":
                self.writer_v.update_user_cli(self.current_user)
            case "3":
                self.writer_v.delete_user_cli(self.current_user)

    def _menu_client(self) -> None:
        """CRUD client pour les commerciaux et la gestion."""
        self.print_header("-- Clients --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        match choice:
            case "1":
                self.writer_v.create_client_cli(self.current_user)
            case "2":
                self.writer_v.update_client_cli(self.current_user)

    # ------------------------------------------------------------------ #
    # Contrats                                                           #
    # ------------------------------------------------------------------ #
    def _menu_contract_gestion(self) -> None:
        """Contrats – actions accessibles au rôle *gestion*."""
        self.print_header("-- Contrats (gestion) --")
        print(self.BLUE + "[1] Créer" + self.END)
        print(self.BLUE + "[2] Modifier" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        match choice:
            case "1":
                self.writer_v.create_contract_cli(self.current_user)
            case "2":
                self.writer_v.update_contract_cli(self.current_user)

    def _menu_contract_commercial(self) -> None:
        """Contrats – actions côté *commercial* (modif & affichages dédiés)."""
        while True:
            self.print_header("-- Contrats (commercial) --")
            print(self.BLUE + "[1] Modifier" + self.END)
            print(self.BLUE + "[2] Affichage" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)
            choice = input(self.CYAN + "Choix : " + self.END).strip()
            match choice:
                case "1":
                    self.writer_v.update_contract_cli(self.current_user)
                case "2":
                    self._submenu_contract_display()
                case "0":
                    break
                case _:
                    self.print_red("Option invalide.")

    def _submenu_contract_display(self) -> None:
        """Affichages filtrés (non signés / restant à payer) pour commerciaux."""
        while True:
            self.print_header("-- Affichage contrats --")
            print(self.BLUE + "[1] Non signés" + self.END)
            print(self.BLUE + "[2] Restant à payer" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)
            choice = input(self.CYAN + "Choix : " + self.END).strip()
            match choice:
                case "1":
                    self.reader_v.display_unsigned_contracts(self.current_user)
                case "2":
                    self.reader_v.display_unpaid_contracts(self.current_user)
                case "0":
                    break
                case _:
                    self.print_red("Option invalide.")

    # ------------------------------------------------------------------ #
    # Événements                                                         #
    # ------------------------------------------------------------------ #
    def _menu_event_gestion(self) -> None:
        """Menu événements côté *gestion* (assignation de supports)."""
        self.print_header("-- Événements (gestion) --")
        print(self.BLUE + "[1] Afficher sans support" + self.END)
        print(self.BLUE + "[2] Assigner / modifier support" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        choice = input(self.CYAN + "Choix : " + self.END).strip()
        match choice:
            case "1":
                self.writer_v.list_events_no_support(self.current_user)
            case "2":
                self.writer_v.assign_support_cli(self.current_user)

    def _menu_event_commercial(self) -> None:
        """Création d’événements pour les contrats signés du commercial."""
        self.print_header("-- Événements (commercial) --")
        print(self.BLUE + "[1] Créer un événement" + self.END)
        print(self.BLUE + "[0] Retour" + self.END)
        if input(self.CYAN + "Choix : " + self.END).strip() == "1":
            self.writer_v.create_event_cli(self.current_user)

    def _menu_event_support(self) -> None:
        """Sous‑menu délégué à DataWriterView pour le rôle *support*."""
        self.writer_v.menu_event_support(self.current_user)
