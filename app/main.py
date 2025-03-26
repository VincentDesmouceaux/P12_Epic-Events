# app/main.py

from app.config.database import engine


def main():
    print("Bienvenue dans Epic Events CRM !")
    # Ici, on pourrait juste vérifier la connexion:
    conn = engine.connect()
    print("Connexion à la base réussie.")
    conn.close()


if __name__ == "__main__":
    main()
