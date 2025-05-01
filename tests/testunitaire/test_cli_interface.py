# -*- coding: utf-8 -*-
"""
CLI Interface
=============
• gestion     : collaborateurs / clients / contrats / événements
• commercial  : clients / contrats / événements
• support     : événements
• robustesse  : Ctrl-C ou Ctrl-D → sortie propre, jamais de trace-back
"""
from __future__ import annotations

import sys

from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.login_v = LoginView(db_connection)
        self.reader_v = DataReaderView(db_connection)
        self.writer_v = DataWriterView(db_connection)
        self.current_user: dict | None = None

    # ------------------------------------------------------------------ #
    #  Saisie protégée
    # ------------------------------------------------------------------ #
    def _safe_input(self, prompt: str) -> str:
        """
        Enveloppe autour de input()
        • Ctrl-C  ➜ au-revoir + exit 0
        • Ctrl-D  ➜ au-revoir + exit 0
        """
        try:
            return input(self.CYAN + prompt + self.END)
        except (KeyboardInterrupt, EOFError):
            print()                     # retour à la ligne avant le message
            self.print_yellow("Arrêt demandé — au revoir.")
            sys.exit(0)

    # ------------------------------------------------------------------ #
    #  Boucle principale
    # ------------------------------------------------------------------ #
    def run(self):
        """
        Point d’entrée.  
        Un try/except global protège au cas où un ancien appel non migré
        vers _safe_input subsisterait dans une branche non testée.
        """
        try:
            while True:
                self._display_main_menu()
                choice = self._safe_input("Votre choix : ").strip()
                if choice == "1":
                    self._menu_login()
                elif choice == "2" and self.current_user:
                    self._menu_read()
                elif choice == "3" and self.current_user:
                    self._menu_write()
                elif choice in ("0", "4"):
                    self.print_green("Au revoir.")
                    break
                else:
                    self.print_red("Option invalide.")
        except (KeyboardInterrupt, EOFError):
            print()
            self.print_yellow("Arrêt demandé — au revoir.")
            sys.exit(0)

    # ------------------------------------------------------------------ #
    #  MENUS
    # ------------------------------------------------------------------ #
    def _display_main_menu(self):
        self.print_header("\n=== Epic Events CLI ===")
        print(self.BLUE + "[1] Se connecter" + self.END)
        if self.current_user:
            print(self.BLUE + "[2] Lire données" + self.END)
            print(self.BLUE + "[3] Gérer" + self.END)
        print(self.BLUE + "[0] Quitter" + self.END)

    # ------------------- Authentification ------------------- #
    def _menu_login(self):
        self.print_header("\n-- Connexion --")
        email = self._safe_input("Email : ").strip()
        pwd = self._safe_input("Mot de passe : ").strip()
        user = self.login_v.login_with_credentials_return_user(email, pwd)
        if user:
            self.current_user = {
                "id": user.id,
                "role": user.role.name,
                "role_id": user.role.id
            }
            self.print_green(f"Connecté en tant que {user.role.name}.")
        else:
            self.print_red("Échec de l'authentification.")

    # --------------------- Lecture -------------------------- #
    def _menu_read(self):
        role = self.current_user["role"]
        while True:
            self.print_header("\n-- Lecture des données --")
            if role in ("gestion", "commercial"):
                print(self.BLUE + "[1] Clients" + self.END)
                print(self.BLUE + "[2] Contrats" + self.END)
            if role in ("gestion", "commercial", "support"):
                print(self.BLUE + "[3] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            c = self._safe_input("Choix : ").strip()
            if c == "1" and role in ("gestion", "commercial"):
                self.reader_v.display_clients_only(self.current_user)
            elif c == "2" and role in ("gestion", "commercial"):
                self.reader_v.display_contracts_only(self.current_user)
            elif c == "3" and role in ("gestion", "commercial", "support"):
                self.reader_v.display_events_only(self.current_user)
            elif c in ("0", "4"):
                break
            else:
                self.print_red("Option invalide.")

    # ------------------- Gestion / écriture ---------------- #
    def _menu_write(self):
        role = self.current_user["role"]
        while True:
            self.print_header("\n-- Gestion --")
            if role == "gestion":
                print(self.BLUE + "[1] Collaborateurs" + self.END)
            if role in ("gestion", "commercial"):
                print(self.BLUE + "[2] Clients" + self.END)
                print(self.BLUE + "[3] Contrats" + self.END)
            if role in ("gestion", "support"):
                print(self.BLUE + "[4] Événements" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)

            c = self._safe_input("Choix : ").strip()
            if c == "1" and role == "gestion":
                self.writer_v.menu_collaborator(self.current_user)
            elif c == "2" and role in ("gestion", "commercial"):
                self.writer_v.menu_client(self.current_user)
            elif c == "3" and role in ("gestion", "commercial"):
                self.writer_v.menu_contract(self.current_user)
            elif c == "4" and role in ("gestion", "support"):
                self.writer_v.menu_event(self.current_user)
            elif c in ("0", "5"):
                break
            else:
                self.print_red("Option invalide.")
