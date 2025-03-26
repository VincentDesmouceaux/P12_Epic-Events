# app/controllers/data_reader.py

from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


class DataReader:
    """
    Classe responsable de la lecture des données depuis la base,
    en s'assurant que l'utilisateur est authentifié.
    """

    def __init__(self, db_connection):
        """
        Initialise le DataReader avec une connexion à la base.
        """
        self.db_connection = db_connection

    def get_all_clients(self, session, current_user):
        """
        Retourne la liste de tous les clients si l'utilisateur est authentifié.
        """
        if not current_user:
            raise Exception("Utilisateur non authentifié.")
        # Ici, on pourrait ajouter des filtres basés sur des permissions spécifiques.
        return session.query(Client).all()

    def get_all_contracts(self, session, current_user):
        """
        Retourne la liste de tous les contrats si l'utilisateur est authentifié.
        """
        if not current_user:
            raise Exception("Utilisateur non authentifié.")
        return session.query(Contract).all()

    def get_all_events(self, session, current_user):
        """
        Retourne la liste de tous les événements si l'utilisateur est authentifié.
        """
        if not current_user:
            raise Exception("Utilisateur non authentifié.")
        return session.query(Event).all()
