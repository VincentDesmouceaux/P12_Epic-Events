"""
Vue CLI (écriture) – DataWriterView
-----------------------------------
• rôle **gestion**   : tout (collaborateurs, clients, contrats, événements)
• rôle **commercial**: clients + contrats + création d’événements
• rôle **support**   : mise à jour des événements qui leur sont attribués
"""

from datetime import datetime

from app.views.generic_view import GenericView
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController
from app.models.user import User           # utilisé par assign_support_cli


class DataWriterView(GenericView):
    # ------------------------------------------------------------------ #
    #  construction
    # ------------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.writer = DataWriter(self.db)
        self.auth = AuthController()        # pour le hash de mot-de-passe

    # ------------------------------------------------------------------ #
    #  helpers I/O
    # ------------------------------------------------------------------ #
    def _ask(self, label, cast=str, allow_empty=False):
        while True:
            val = input(self.CYAN + label + self.END).strip()
            if not val and allow_empty:
                return None
            if not val:
                self.print_red("Valeur obligatoire.")
                continue
            try:
                return cast(val) if cast else val
            except ValueError:
                self.print_red("Format invalide.")

    @staticmethod
    def _fmt(entity):
        cols = {
            col.name: getattr(entity, col.name)
            for col in entity.__table__.columns
            if col.name != "password_hash"
        }
        return str(cols)

    # ------------------------------------------------------------------ #
    #  ----------------------- Collaborateurs -------------------------  #
    # ------------------------------------------------------------------ #
    def create_user_cli(self, current_user):
        fname = self._ask("Prénom : ")
        lname = self._ask("Nom : ")
        email = self._ask("Email : ")
        pwd = self._ask("Mot de passe : ")
        role_id = self._ask("ID rôle (1=C,2=S,3=G) : ", int)

        sess = self.db.create_session()
        try:
            u = self.writer.create_user(
                sess,
                current_user,
                employee_number=None,
                first_name=fname,
                last_name=lname,
                email=email,
                password_hash=self.auth.hasher.hash(pwd),
                role_id=role_id
            )
            sess.commit()
            self.print_green("✅ Collaborateur créé : " + self._fmt(u))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def update_user_cli(self, current_user):
        emp = self._ask("Employee Number : ")
        field = self._ask(
            "Champ (first_name, last_name, email, password) : ").lower()
        value = self._ask("Nouvelle valeur : ")

        if field == "password":
            value = self.auth.hasher.hash(value)

        sess = self.db.create_session()
        try:
            u = self.writer.update_user_by_employee_number(
                sess, current_user, emp, **{field: value})
            sess.commit()
            self.print_green("✅ Modification : " + self._fmt(u))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def delete_user_cli(self, current_user):
        emp = self._ask("Employee Number à supprimer : ")
        sess = self.db.create_session()
        try:
            self.writer.delete_user(sess, current_user, emp)
            sess.commit()
            self.print_green("✅ Collaborateur supprimé.")
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    # ------------------------------------------------------------------ #
    #  ---------------------------- Clients ---------------------------  #
    # ------------------------------------------------------------------ #
    def create_client_cli(self, current_user):
        fname = self._ask("Nom complet : ")
        email = self._ask("Email : ")
        phone = self._ask("Téléphone : ", allow_empty=True)
        comp = self._ask("Société : ", allow_empty=True)

        sess = self.db.create_session()
        try:
            c = self.writer.create_client(
                sess, current_user,
                full_name=fname,
                email=email,
                phone=phone,
                company_name=comp,
                commercial_id=None        # attribué auto si commercial
            )
            sess.commit()
            self.print_green("✅ Client créé : " + self._fmt(c))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def update_client_cli(self, current_user):
        cid = self._ask("ID client : ", int)
        new_name = self._ask("Nouveau nom complet (vide si aucun) : ",
                             allow_empty=True)
        new_email = self._ask("Nouvel email (vide si aucun) : ",
                              allow_empty=True)
        phone = self._ask("Téléphone (vide si aucun) : ", allow_empty=True)
        comp = self._ask("Société (vide si aucune) : ", allow_empty=True)

        updates = {}
        if new_name:
            updates["full_name"] = new_name
        if new_email:
            updates["email"] = new_email
        if phone is not None:
            updates["phone"] = phone
        if comp is not None:
            updates["company_name"] = comp
        if not updates:
            self.print_yellow("Aucune modification.")
            return

        sess = self.db.create_session()
        try:
            c = self.writer.update_client(sess, current_user, cid, **updates)
            sess.commit()
            self.print_green("✅ Client modifié : " + self._fmt(c))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    # ------------------------------------------------------------------ #
    #  --------------------------- Contrats ---------------------------  #
    # ------------------------------------------------------------------ #
    def create_contract_cli(self, current_user):
        cid = self._ask("ID client : ", int)
        tot = self._ask("Montant total : ", float)
        rem = self._ask("Montant restant : ", float)
        signed = self._ask("Signé ? (o/n) : ").lower() == "o"

        sess = self.db.create_session()
        try:
            ctr = self.writer.create_contract(
                sess, current_user,
                client_id=cid,
                total_amount=tot,
                remaining_amount=rem,
                is_signed=signed
            )
            sess.commit()
            self.print_green("✅ Contrat créé : " + self._fmt(ctr))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def update_contract_cli(self, current_user):
        ctr_id = self._ask("ID contrat : ", int)
        rem = self._ask("Nouveau restant (vide si aucun) : ",
                        float, allow_empty=True)
        signed = self._ask("Signé ? (o/n/vide) : ",
                           allow_empty=True).lower()
        updates = {}
        if rem is not None:
            updates["remaining_amount"] = rem
        if signed == "o":
            updates["is_signed"] = True
        elif signed == "n":
            updates["is_signed"] = False
        if not updates:
            self.print_yellow("Aucune modification.")
            return

        sess = self.db.create_session()
        try:
            ctr = self.writer.update_contract(
                sess, current_user, ctr_id, **updates)
            sess.commit()
            self.print_green("✅ Contrat modifié : " + self._fmt(ctr))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    # ------------------------------------------------------------------ #
    #  --------------------------- Événements -------------------------  #
    # ------------------------------------------------------------------ #
    def create_event_cli(self, current_user):
        ctr_id = self._ask("ID contrat : ", int)
        date = datetime.utcnow()            # simple pour la démo
        loc = self._ask("Lieu : ", allow_empty=True)
        att = self._ask("Participants (int) : ", int)
        notes = self._ask("Notes : ", allow_empty=True)

        sess = self.db.create_session()
        try:
            ev = self.writer.create_event(
                sess, current_user,
                contract_id=ctr_id,
                support_id=None,
                date_start=date,
                date_end=None,
                location=loc,
                attendees=att,
                notes=notes
            )
            sess.commit()
            self.print_green("✅ Événement créé : " + self._fmt(ev))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def assign_support_cli(self, current_user, event_id=None, support_emp=None):
        """
        • utilisée directement par le CLI principal
        • ré-utilisable dans les tests (appel programmatique)
        """
        if event_id is None:
            event_id = self._ask("ID événement : ", int)
        if support_emp is None:
            support_emp = self._ask("Employee Number du support : ")

        sess = self.db.create_session()
        try:
            sup = (
                sess.query(User)
                .filter_by(employee_number=support_emp, role_id=2)
                .first()
            )
            if not sup:
                raise Exception("Support introuvable ou rôle incorrect.")

            ev = self.writer.update_event(
                sess, current_user, event_id, support_id=sup.id)
            sess.commit()
            self.print_green("✅ Support assigné : " + self._fmt(ev))
            return ev
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
            raise
        finally:
            sess.close()
