# 🎉 Epic Events – CRM CLI  
_Gérez vos clients, contrats & événements depuis un simple terminal – en toute sécurité, avec journalisation Sentry._

---

## 🗂️ Sommaire
1. [Pré‑requis](#pré‑requis)  
2. [Installation pas‑à‑pas](#installation-pas-à-pas)  
3. [Configuration `.env`](#configuration-env)  
4. [Initialiser la base & données de démo](#initialiser-la-base--données-de-démo)  
5. [Lancer l’application](#lancer-lapplication)  
6. [Journalisation Sentry](#journalisation-sentry)  
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

# 2. Installer Pipenv (si absent)
pipx install pipenv          

# 3. Créer l’environnement virtuel + dépendances
pipenv install --dev         

# 4. Activer le shell virtuel
pipenv shell


## Configuration .env

# BDD
DB_ENGINE=mysql+pymysql
DB_USER=epicuser
DB_PASSWORD=some_strong_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=epic_db

# Sentry
SENTRY_DSN=https://e47a0f56bbc36b31cff199a266b3a7f2@o4509281674199040.ingest.de.sentry.io/4509281676623952
SENTRY_ENV=prod
SENTRY_TRACES=1.0        
SENTRY_PROFILE=1.0       
SENTRY_SEND_PII=true     

