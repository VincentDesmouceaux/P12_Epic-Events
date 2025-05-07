# app/views/cli_interface.py
"""Interface en ligne de commande (CLI) d’Epic Events.

Fonctionnalités principales
---------------------------
* Authentification d’un collaborateur.
* Lecture des données (clients, contrats, événements) – accès adapté au rôle.
* Écriture / gestion des entités pour les rôles autorisés.
* Sortie propre en cas de Ctrl‑C ou Ctrl‑D.

Trois rôles :
    • gestion     → accès complet + administration des collaborateurs  
    • commercial  → gestion de « ses » clients / contrats / événements  
    • support     → mise à jour des événements assignés
"""
from __future__ import annotations

import sys
from typing import Dict, Optional

from app.views.generic_view import GenericView
from app.views.login_view import LoginView
from app.views.data_reader_view import DataReaderView
from app.views.data_writer_view import DataWriterView


class CLIInterface(GenericView):
    """Boucle principale de l’application en mode terminal."""

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        """Enregistre la connexion BD et instancie les vues enfants."""
        super().__init__()
        self.db = db_connection
        self.login_v = LoginView(db_connection)
        self.reader_v = DataReaderView(db_connection)
        self.writer_v = DataWriterView(db_connection)
        self.current_user: Optional[Dict] = None

    # ------------------------------------------------------------------ #
    # Entrée protégée
    # ------------------------------------------------------------------ #
    def _safe_input(self, prompt: str) -> str:
        """Capture Ctrl‑C / Ctrl‑D pour quitter proprement le programme."""
        try:
            return input(self.CYAN + prompt + self.END)
        except (KeyboardInterrupt, EOFError):
            print()  # retour à la ligne
            self.print_yellow("Arrêt demandé — au revoir.")
            sys.exit(0)

    # ------------------------------------------------------------------ #
    # Boucle principale
    # ------------------------------------------------------------------ #
    def run(self) -> None:
        """Démarre la boucle de menus CLI."""
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
    # Menus – affichage principal
    # ------------------------------------------------------------------ #
    def _display_main_menu(self) -> None:
        """Affiche le menu principal (connexion, lecture, gestion, quitter)."""
        self.print_header("\n=== Epic Events CLI ===")
        print(self.BLUE + "[1] Se connecter" + self.END)
        if self.current_user:
            print(self.BLUE + "[2] Lire données" + self.END)
            print(self.BLUE + "[3] Gérer" + self.END)
        print(self.BLUE + "[0] Quitter" + self.END)

    # ------------------------------------------------------------------ #
    # Sous‑menus
    # ------------------------------------------------------------------ #
    def _menu_login(self) -> None:
        """Formulaire de connexion simple (email + mot de passe)."""
        email = self._safe_input("Email : ").strip()
        pwd = self._safe_input("Mot de passe : ").strip()
        user = self.login_v.login_with_credentials_return_user(email, pwd)
        if user:
            self.current_user = {
                "id": user.id,
                "role": user.role.name,
                "role_id": user.role.id,
            }
            self.print_green(f"Connecté en tant que {user.role.name}.")
        else:
            self.print_red("Échec de l'authentification.")

    def _menu_read(self) -> None:
        """Menu de lecture seul – disponible pour tout rôle connecté."""
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

    def _menu_write(self) -> None:
        """Menu Gestion / écriture – options selon le rôle connecté."""
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
