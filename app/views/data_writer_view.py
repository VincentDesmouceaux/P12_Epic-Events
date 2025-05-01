"""
Vue CLI (écriture) – DataWriterView
-----------------------------------
• Gestion   : collaborateurs / clients / contrats / événements
• Commercial: clients / contrats              (lecture seule pour events +
             assignation support uniquement)
• Support   : assignation / mise à jour des événements
⚠︎  AUCUNE création d’événement depuis l’interface ; on ne gère ici
    que l’affichage « sans support » et l’assignation.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from app.views.generic_view import GenericView
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController
from app.models.user import User
from app.models.event import Event


class DataWriterView(GenericView):
    # ------------------------------------------------------------ #
    #  construction
    # ------------------------------------------------------------ #
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.writer = DataWriter(self.db)
        self.auth = AuthController()            # hash des mots de passe

    # ------------------------------------------------------------ #
    #  helpers I/O
    # ------------------------------------------------------------ #
    def _ask(self, prompt: str, cast=str,
             allow_empty: bool = False) -> Optional[Any]:
        while True:
            val = input(self.CYAN + prompt + self.END).strip()
            if val == "" and allow_empty:
                return None
            if val == "":
                self.print_red("Valeur obligatoire.")
                continue
            try:
                return cast(val) if cast else val
            except ValueError:
                self.print_red("Format invalide.")

    def _fmt(self, entity) -> str:
        return str({
            col.name: getattr(entity, col.name)
            for col in entity.__table__.columns
            if col.name != "password_hash"
        })

    # ============================================================ #
    #  ======================= COLLABORATEURS ===================== #
    # ============================================================ #
    def create_user_cli(self, current_user: Dict[str, Any]):
        fname = self._ask("Prénom : ")
        lname = self._ask("Nom : ")
        email = self._ask("Email : ")
        pwd = self._ask("Mot de passe : ")
        role_id = self._ask("Rôle (1=C, 2=S, 3=G) : ", int)

        sess = self.db.create_session()
        try:
            usr = self.writer.create_user(
                sess, current_user,
                employee_number=None,
                first_name=fname, last_name=lname,
                email=email,
                password_hash=self.auth.hasher.hash(pwd),
                role_id=role_id
            )
            sess.commit()
            self.print_green("✅ Créé : " + self._fmt(usr))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def update_user_cli(self, current_user: Dict[str, Any]):
        emp_num = self._ask("Employee Number : ")
        sess = self.db.create_session()
        usr = sess.query(User).filter_by(employee_number=emp_num).first()
        sess.close()
        if not usr:
            self.print_red("Collaborateur introuvable.")
            return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        role_id = self._ask(f"Rôle actuel {usr.role_id} (1=C,2=S,3=G) : ",
                            int, allow_empty=True)
        fname = self._ask(f"Prénom ({usr.first_name}) : ",
                          allow_empty=True)
        lname = self._ask(f"Nom ({usr.last_name}) : ",
                          allow_empty=True)
        email = self._ask(f"Email ({usr.email}) : ",
                          allow_empty=True)
        pwd = self._ask("Nouveau mot de passe : ",
                        allow_empty=True)

        updates = {}
        if role_id is not None:
            updates["role_id"] = role_id
        if fname:
            updates["first_name"] = fname
        if lname:
            updates["last_name"] = lname
        if email:
            updates["email"] = email
        if pwd:
            updates["password_hash"] = self.auth.hasher.hash(pwd)

        if not updates:
            self.print_yellow("Aucune modification effectuée.")
            return

        sess = self.db.create_session()
        try:
            usr_upd = self.writer.update_user_by_employee_number(
                sess, current_user, emp_num, **updates)
            sess.commit()
            self.print_green("✅ Modification : " + self._fmt(usr_upd))
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

    # ============================================================ #
    #  ========================= CLIENTS ========================== #
    # ============================================================ #
    def create_client_cli(self, current_user):
        fname = self._ask("Nom complet : ")
        email = self._ask("Email : ")
        phone = self._ask("Téléphone : ", allow_empty=True)
        comp = self._ask("Société : ", allow_empty=True)

        sess = self.db.create_session()
        try:
            cli = self.writer.create_client(
                sess, current_user,
                full_name=fname, email=email, phone=phone,
                company_name=comp, commercial_id=None
            )
            sess.commit()
            self.print_green("✅ Client créé : " + self._fmt(cli))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    def update_client_cli(self, current_user):
        cid = self._ask("ID client : ", int)
        new_name = self._ask("Nouveau nom complet : ", allow_empty=True)
        new_email = self._ask("Nouvel email : ", allow_empty=True)
        phone = self._ask("Téléphone : ", allow_empty=True)
        comp = self._ask("Société : ", allow_empty=True)

        updates = {k: v for k, v in
                   [("full_name", new_name), ("email", new_email),
                    ("phone", phone), ("company_name", comp)]
                   if v not in (None, "")}

        if not updates:
            self.print_yellow("Aucune modification.")
            return

        sess = self.db.create_session()
        try:
            cli = self.writer.update_client(sess, current_user, cid, **updates)
            sess.commit()
            self.print_green("✅ Client modifié : " + self._fmt(cli))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()

    # ============================================================ #
    #  ========================= CONTRATS ========================= #
    # ============================================================ #
    def create_contract_cli(self, current_user):
        cid = self._ask("ID client : ", int)
        tot = self._ask("Montant total : ", float)
        rem = self._ask("Montant restant : ", float)
        signed = self._ask("Signé ? (o/n) : ").lower() == "o"

        sess = self.db.create_session()
        try:
            ctr = self.writer.create_contract(
                sess, current_user,
                client_id=cid, total_amount=tot,
                remaining_amount=rem, is_signed=signed
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

        self.print_yellow("→ Laisser vide pour ne pas modifier le champ.")
        n_client = self._ask("Nouveau ID client : ", int, allow_empty=True)
        n_com_emp = self._ask(
            "Employee Number commercial : ", allow_empty=True)
        n_total = self._ask("Nouveau montant total : ",
                            float, allow_empty=True)
        n_rem = self._ask("Nouveau montant restant : ",
                          float, allow_empty=True)
        n_signed = self._ask("Signé ? (o/n/vide) : ",
                             allow_empty=True).lower()

        updates: Dict[str, Any] = {}
        if n_client is not None:
            updates["client_id"] = n_client
        if n_total is not None:
            updates["total_amount"] = n_total
        if n_rem is not None:
            updates["remaining_amount"] = n_rem
        if n_signed == "o":
            updates["is_signed"] = True
        elif n_signed == "n":
            updates["is_signed"] = False

        # conversion commercial employee_number → commercial_id
        if n_com_emp:
            sess_tmp = self.db.create_session()
            com_user = sess_tmp.query(User).filter_by(
                employee_number=n_com_emp, role_id=1).first()
            sess_tmp.close()
            if not com_user:
                self.print_red("Commercial introuvable.")
                return
            updates["commercial_id"] = com_user.id

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

    # ============================================================ #
    #  ========================= ÉVÉNEMENTS ======================= #
    # ============================================================ #
    def list_events_no_support(self, current_user):
        sess = self.db.create_session()
        try:
            evs = sess.query(Event).filter_by(support_id=None).all()
            if not evs:
                self.print_yellow("Aucun événement sans support.")
                return
            self.print_green("--- Événements sans support ---")
            for ev in evs:
                print(self._fmt(ev))
        finally:
            sess.close()

    def assign_support_cli(self, current_user,
                           event_id: Optional[int] = None,
                           support_emp: Optional[str] = None):
        if event_id is None:
            event_id = self._ask("ID événement : ", int)
        if support_emp is None:
            support_emp = self._ask("Employee Number du support : ")

        sess = self.db.create_session()
        try:
            sup = sess.query(User).filter_by(
                employee_number=support_emp, role_id=2).first()
            if not sup:
                self.print_red("Support introuvable ou rôle incorrect.")
                return

            ev = self.writer.update_event(
                sess, current_user, event_id, support_id=sup.id)
            sess.commit()
            self.print_green("✅ Support assigné : " + self._fmt(ev))
        except Exception as e:
            sess.rollback()
            self.print_red(f"❌ {e}")
        finally:
            sess.close()
