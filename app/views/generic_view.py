# app/views/generic_view.py
# -*- coding: utf-8 -*-
"""
Vue générique — fournit de petites méthodes d’affichage coloré.

Tous les écrans CLI héritent de cette classe afin d’afficher des
intitulés cohérents dans le terminal.
"""


class GenericView:
    """Méthodes : :pymeth:`print_header`, :pymeth:`print_blue`, etc."""

    # ----------------------------------------------------------------- #
    # Construction
    # ----------------------------------------------------------------- #
    def __init__(self):
        """Initialise la palette ANSI utilisée par les méthodes *print_*."""
        self.HEADER = '\033[95m'
        self.BLUE = '\033[94m'
        self.CYAN = '\033[96m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
        self.END = '\033[0m'

    # ----------------------------------------------------------------- #
    # Helpers d’affichage
    # ----------------------------------------------------------------- #
    def print_header(self, text: str) -> None:
        """Affiche *text* en gras + violet."""
        print(f"{self.BOLD}{self.HEADER}{text}{self.END}")

    def print_blue(self, text: str) -> None:
        """Affiche *text* en bleu."""
        print(f"{self.BLUE}{text}{self.END}")

    def print_cyan(self, text: str) -> None:
        """Affiche *text* en cyan."""
        print(f"{self.CYAN}{text}{self.END}")

    def print_green(self, text: str) -> None:
        """Affiche *text* en vert."""
        print(f"{self.GREEN}{text}{self.END}")

    def print_yellow(self, text: str) -> None:
        """Affiche *text* en jaune."""
        print(f"{self.YELLOW}{text}{self.END}")

    def print_red(self, text: str) -> None:
        """Affiche *text* en rouge."""
        print(f"{self.RED}{text}{self.END}")
