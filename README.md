# 🎉 Epic Events – CRM CLI  
_Gérez vos clients, contrats & événements depuis un simple terminal – en toute sécurité, avec journalisation Sentry._

---

## 🗂️ Sommaire
1. [Pré‑requis](#pré‑requis)  
2. [Installation pas‑à‑pas](#installation-pas-à-pas)  
3. [Configuration `.env`](#configuration-env)  
4. [Initialiser la base & données de démo](#initialiser-la-base--données-de-démo)  
5. [Lancer l’application](#lancer-lapplication)  
6. [Vérifier l’intégration Sentry](#journalisation-sentry)  
7. [🎯 Tests, couverture & qualité](#tests-couverture--qualité)  
8. [🗺️ Schéma SQL (ERD)](#schéma-sql-erd)  
9. [🤝 Contribuer](#contribuer)

---

## Pré‑requis
| Outil | Version mini | Pourquoi ? |
|-------|--------------|------------|
| **Python** | `3.12` | langage principal |
| **MySQL / MariaDB** | `5.7+` | base de données (prod & tests d’intégration) |
| **Git** | – | cloner le dépôt |


---

## Installation pas‑à‑pas


# 1. Cloner le dépôt
git clone https://github.com/VincentDesmouceaux/P12_Epic-Events.git

cd P12_Epic-Events

# 2. Préparer les variables d’environnement
cp .env.example .env          

 puis ouvrez .env et remplissez vos vraies valeurs

# 3. Installer Pipenv (si absent)
pipx install pipenv          

# 4. Créer l’environnement virtuel + dépendances
pipenv install    

# 5. Activer le shell virtuel
pipenv shell


## Configuration .env

# BDD
DB_ENGINE=mysql+pymysql

DB_USER=epicuser

DB_PASSWORD=

DB_HOST=localhost

DB_PORT=3306

DB_NAME=epic_db

# Sentry
SENTRY_DSN=<votre_dsn_sentry>

SENTRY_ENV=prod

SENTRY_TRACES=1.0     

SENTRY_PROFILE=1.0    

SENTRY_SEND_PII=true

# JWT / Auth

JWT_SECRET=

JWT_ALGORITHM=

JWT_EXPIRATION_MINUTES=

## Initialiser la base & données de démo

mysql -u root -p

mysql> DROP DATABASE IF EXISTS epic_db;

mysql> DROP USER IF EXISTS 'epicuser'@'localhost';

mysql> CREATE DATABASE epic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

mysql> SHOW VARIABLES LIKE 'validate_password.policy';

mysql> SET GLOBAL validate_password.policy = 0;

mysql> SET GLOBAL validate_password.length = 8;

mysql> CREATE USER 'epicuser'@'%' IDENTIFIED BY 'some_strong_password';

mysql> GRANT ALL PRIVILEGES ON epic_db.* TO 'epicuser'@'%';

mysql> FLUSH PRIVILEGES;

mysql> EXIT;

## Lancer l’application

python3 -m main (cela aura pour effet d'initialiser les données de seed_db.py)

Utiliser les informations se trouvant dans les données d'exemple du fichier seed_db.py pour tester l'application.

## Vérifier l’intégration Sentry

| Test | Variable d’environnement | Commande à exécuter | Résultat attendu dans Sentry |
|------|-------------------------|---------------------|------------------------------|
| Ping (simple message) | `SENTRY_TEST=ping` | `SENTRY_TEST=ping python -m main` | Nouveau _event_ de type **message** intitulé “Sentry ping …” (niveau **info**) |
| Exception volontaire | `SENTRY_TEST=1` | `SENTRY_TEST=1 python -m main` | Un _event_ **error** “ZeroDivisionError: division by zero” |

> ⚠️ Les variables d’environnement doivent être placées **avant** la commande Python (elles ne sont valables que pour cette exécution).

## 🎯 Tests, couverture & qualité

python3 -m unittest discover -s tests

flake8

pipenv run coverage run -m unittest discover -s tests

pipenv run coverage html

## 🗺️ Schéma SQL (ERD)


    ROLE ||--o{ USER : "1‑n"
    USER ||--o{ CLIENT : "1‑n  (commercial_id)"
    USER ||--o{ CONTRACT : "1‑n  (commercial_id)"
    USER ||--o{ EVENT : "1‑n  (support_id)"

    CLIENT ||--o{ CONTRACT : "1‑n"
    CONTRACT ||--|{ EVENT : "1‑1"

    ROLE {
        int     id          PK
        varchar name        UNIQUE
        varchar description
    }

    USER {
        int     id              PK
        varchar employee_number UNIQUE
        varchar first_name
        varchar last_name
        varchar email           UNIQUE
        varchar password_hash
        int     role_id   FK→ROLE.id
    }

    CLIENT {
        int     id          PK
        varchar full_name
        varchar email
        varchar phone
        varchar company_name
        datetime date_created
        datetime date_last_contact
        int     commercial_id  FK→USER.id
    }

    CONTRACT {
        int      id           PK
        float    total_amount
        float    remaining_amount
        datetime date_created
        bool     is_signed
        int      client_id     FK→CLIENT.id
        int      commercial_id FK→USER.id
    }

    EVENT {
        int      id           PK
        datetime date_start
        datetime date_end
        varchar  location
        int      attendees
        text     notes
        int      contract_id  FK→CONTRACT.id
        int      support_id   FK→USER.id (nullable)
    }

## 🤝 Contribuer

1. **Fork** puis créez une branche (`feat/ma-feature`)

2. Installez les dépendances : pipenv install --dev

3. Codez !💚

4. Open Pull‑Request ✨

*Happy coding & have an **Epic** day ! 🚀*