# app/views/generic_entity_view.py
# -*- coding: utf-8 -*-
"""
Vue utilitaire ─ formatage d’un objet SQLAlchemy pour l’affichage CLI.

Le but est d’obtenir rapidement une représentation lisible d’une entité :
    >>> view = GenericEntityView()
    >>> print(view.format_entity(user))
    id=1, email=john@doe.io, role_id=3
"""


class GenericEntityView:
    """Fournit un unique helper : :pymeth:`format_entity`."""

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def format_entity(self, entity):
        """
        Convertit une instance SQLAlchemy en chaîne « clé=val, … ».

        *Si* l’objet ne possède pas d’attribut ``__table__`` (ce n’est donc
        pas une entité SQLAlchemy), sa représentation ``str`` brute est
        renvoyée à la place.

        Parameters
        ----------
        entity : Any
            Instance d’un modèle ou tout autre objet.

        Returns
        -------
        str
            Représentation prête à l’impression.
        """
        try:
            columns = entity.__table__.columns.keys()
        except AttributeError:
            # objet lambda : on se rabat sur str(x)
            return str(entity)

        values = {}
        for col in columns:
            try:
                values[col] = getattr(entity, col)
            except Exception:            # pragma: no cover — champ inaccessible
                values[col] = "Inaccessible"

        return ", ".join(f"{col}={value}" for col, value in values.items())
