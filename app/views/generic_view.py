# app/views/generic_view.py
class GenericView:
    """
    Classe générique de vue pour l'affichage coloré dans le terminal.
    Fournit des méthodes d'affichage formaté.
    """

    def __init__(self):
        self.HEADER = '\033[95m'
        self.BLUE = '\033[94m'
        self.CYAN = '\033[96m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
        self.END = '\033[0m'

    def print_header(self, text):
        print(f"{self.BOLD}{self.HEADER}{text}{self.END}")

    def print_blue(self, text):
        print(f"{self.BLUE}{text}{self.END}")

    def print_cyan(self, text):
        print(f"{self.CYAN}{text}{self.END}")

    def print_green(self, text):
        print(f"{self.GREEN}{text}{self.END}")

    def print_yellow(self, text):
        print(f"{self.YELLOW}{text}{self.END}")

    def print_red(self, text):
        print(f"{self.RED}{text}{self.END}")
