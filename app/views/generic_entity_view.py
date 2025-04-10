# app/views/generic_entity_view.py

class GenericEntityView:
    """
    Classe de base pour formater l'affichage d'une entité SQLAlchemy.
    La méthode format_entity parcourt les colonnes définies dans la table
    et retourne une chaîne de la forme "col1=val1, col2=val2, ..." pour l'entité.
    """

    def format_entity(self, entity):
        try:
            # On récupère la liste des colonnes définies dans le modèle SQLAlchemy
            columns = entity.__table__.columns.keys()
        except AttributeError:
            # Si l'entité ne possède pas __table__, on retourne simplement sa représentation
            return str(entity)
        # Construire un dictionnaire des valeurs pour chaque colonne
        values = {}
        for col in columns:
            try:
                values[col] = getattr(entity, col)
            except Exception:
                values[col] = "Inaccessible"
        # Retourner une chaîne formatée
        return ", ".join(f"{col}={value}" for col, value in values.items())
