"""
Vue « lecture seule » – DataReaderView
--------------------------------------
Tous les collaborateurs peuvent consulter les listes ; aucun filtre
n’est appliqué ici. Deux aides d’affichage supplémentaires sont
exposées pour la CLI “commercial” :

    • display_unsigned_contracts()  – contrats non signés
    • display_unpaid_contracts()    – contrats avec reste à payer
"""
from __future__ import annotations
from typing import Dict, List

from app.controllers.data_reader import DataReader
from app.views.generic_view import GenericView
from app.models.contract import Contract


class DataReaderView(GenericView):
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db_conn = db_connection
        self.reader = DataReader(self.db_conn)

    # ------------------------------------------------------------------ #
    #  Méthodes utilitaires (aucun décorateur)
    # ------------------------------------------------------------------ #
    def _fmt(self, entity) -> str:
        """Renvoie un dict lisible – on masque password_hash s’il existe."""
        return str({
            col.name: getattr(entity, col.name)
            for col in entity.__table__.columns
            if col.name != "password_hash"
        })

    # ------------------------------------------------------------------ #
    #  LISTES GÉNÉRIQUES
    # ------------------------------------------------------------------ #
    def display_clients_only(self, current_user: Dict):
        print(f"[DataReaderView][TRACE] display_clients_only {current_user}")
        with self.db_conn.create_session() as sess:
            for cli in self.reader.get_all_clients(sess, current_user):
                print(self._fmt(cli))

    def display_contracts_only(self, current_user: Dict):
        print(f"[DataReaderView][TRACE] display_contracts_only {current_user}")
        with self.db_conn.create_session() as sess:
            for ctr in self.reader.get_all_contracts(sess, current_user):
                print(self._fmt(ctr))

    def display_events_only(self, current_user: Dict):
        print(f"[DataReaderView][TRACE] display_events_only {current_user}")
        with self.db_conn.create_session() as sess:
            for ev in self.reader.get_all_events(sess, current_user):
                print(self._fmt(ev))

    # ------------------------------------------------------------------ #
    #  LISTES SPÉCIFIQUES (sous‑menu “Affichage” du commercial)
    # ------------------------------------------------------------------ #
    def _print_contract_subset(self, title: str, contracts: List[Contract]):
        if not contracts:
            self.print_yellow(f"Aucun {title.lower()}.")
            return
        self.print_green(f"--- {title} ---")
        for ctr in contracts:
            print(self._fmt(ctr))

    def display_unsigned_contracts(self, current_user: Dict):
        """Contrats dont *is_signed* est *False*."""
        with self.db_conn.create_session() as sess:
            ctrs = [
                c for c in self.reader.get_all_contracts(sess, current_user)
                if not c.is_signed
            ]
        self._print_contract_subset("Contrats non signés", ctrs)

    def display_unpaid_contracts(self, current_user: Dict):
        """Contrats avec un *remaining_amount* positif."""
        with self.db_conn.create_session() as sess:
            ctrs = [
                c for c in self.reader.get_all_contracts(sess, current_user)
                if c.remaining_amount > 0
            ]
        self._print_contract_subset("Contrats restant à payer", ctrs)
