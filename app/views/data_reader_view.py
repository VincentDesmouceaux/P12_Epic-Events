# app/views/data_reader_view.py
# -*- coding: utf-8 -*-
"""
Vue **lecture seule** pour l’affichage des entités métier.

Le rôle de `DataReaderView` est purement *UI* :  
il interroge le contrôleur `DataReader`, formate chaque entité en
chaine lisible puis l’affiche dans la console à l’aide des méthodes
de coloration héritées de `GenericView`.

Fonctionnalités :

* **Clients**                     : `display_clients_only`
* **Contrats**                    : `display_contracts_only`
* **Événements**                  : `display_events_only`
* **Contrats non signés**         : `display_unsigned_contracts`
* **Contrats restant à payer**    : `display_unpaid_contracts`
"""
from __future__ import annotations

from typing import Dict, List

from app.controllers.data_reader import DataReader
from app.models.contract import Contract
from app.views.generic_view import GenericView


class DataReaderView(GenericView):
    """
    Couche « vue » pour la consultation des données.

    Parameters
    ----------
    db_connection :
        Instance de `DatabaseConnection` permettant d’ouvrir des sessions
        SQLAlchemy (cf. `app.config.database`).
    """

    # ------------------------------------------------------------------ #
    # Construction                                                       #
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self._db_conn = db_connection
        self._reader = DataReader(self._db_conn)

    # ------------------------------------------------------------------ #
    # Méthodes utilitaires                                               #
    # ------------------------------------------------------------------ #
    def _fmt(self, entity) -> str:
        """
        Transforme une entité SQLAlchemy en dictionnaire « propre ».

        Le champ *password_hash* est volontairement masqué pour éviter
        l’affichage de données sensibles.

        Parameters
        ----------
        entity :
            Instance SQLAlchemy (Client, Contract, Event, …).

        Returns
        -------
        str
            Représentation textuelle prête à être affichée.
        """
        return str(
            {
                col.name: getattr(entity, col.name)
                for col in entity.__table__.columns
                if col.name != "password_hash"
            }
        )

    # ------------------------------------------------------------------ #
    # LISTES GÉNÉRIQUES                                                  #
    # ------------------------------------------------------------------ #
    def display_clients_only(self, current_user: Dict):
        """Affiche tous les clients accessibles pour *current_user*."""
        with self._db_conn.create_session() as sess:
            for client in self._reader.get_all_clients(sess, current_user):
                print(self._fmt(client))

    def display_contracts_only(self, current_user: Dict):
        """Affiche tous les contrats accessibles pour *current_user*."""
        with self._db_conn.create_session() as sess:
            for contract in self._reader.get_all_contracts(sess, current_user):
                print(self._fmt(contract))

    def display_events_only(self, current_user: Dict):
        """Affiche tous les événements accessibles pour *current_user*."""
        with self._db_conn.create_session() as sess:
            for event in self._reader.get_all_events(sess, current_user):
                print(self._fmt(event))

    # ------------------------------------------------------------------ #
    # LISTES SPÉCIFIQUES – rôle commercial                               #
    # ------------------------------------------------------------------ #
    def _print_contract_subset(self, title: str, contracts: List[Contract]):
        """
        Affiche un sous‑ensemble de contrats précédé d’un titre.

        Parameters
        ----------
        title :
            Libellé à afficher avant la liste (ex. « Contrats non signés »).
        contracts :
            Liste d’instances `Contract` à afficher.
        """
        if not contracts:
            self.print_yellow(f"Aucun {title.lower()}.")
            return

        self.print_green(f"--- {title} ---")
        for contract in contracts:
            print(self._fmt(contract))

    def display_unsigned_contracts(self, current_user: Dict):
        """Affiche les contrats dont `is_signed` est *False*."""
        with self._db_conn.create_session() as sess:
            unsigned = [
                ctr
                for ctr in self._reader.get_all_contracts(sess, current_user)
                if not ctr.is_signed
            ]
        self._print_contract_subset("Contrats non signés", unsigned)

    def display_unpaid_contracts(self, current_user: Dict):
        """Affiche les contrats avec un `remaining_amount` > 0."""
        with self._db_conn.create_session() as sess:
            unpaid = [
                ctr
                for ctr in self._reader.get_all_contracts(sess, current_user)
                if ctr.remaining_amount > 0
            ]
        self._print_contract_subset("Contrats restant à payer", unpaid)
