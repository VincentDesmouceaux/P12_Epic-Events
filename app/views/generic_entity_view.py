# app/views/generic_entity_view.py

class GenericEntityView:
    """
    Classe de base pour formater l'affichage d'une entité SQLAlchemy.
    La méthode format_entity parcourt les colonnes et retourne une chaîne de la forme "col=val, col2=val2, ...".
    """

    def format_entity(self, entity):
        try:
            columns = entity.__table__.columns.keys()
        except AttributeError:
            return str(entity)
        values = {}
        for col in columns:
            try:
                values[col] = getattr(entity, col)
            except Exception:
                values[col] = "Inaccessible"
        return ", ".join(f"{col}={value}" for col, value in values.items())
