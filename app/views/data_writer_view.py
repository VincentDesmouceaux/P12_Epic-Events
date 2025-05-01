"""
Vue CLI – DataWriterView (écriture)
-----------------------------------
• Gestion     : collaborateurs / clients / contrats / événements
• Commercial  : clients / mise à jour de leurs contrats /
                création d’événements sur leurs contrats signés /
                assignation support
• Support     : assignation / mise à jour des événements
"""
from __future__ import annotations

from datetime import datetime, date, time
from typing import Any, Dict, Optional

from app.views.generic_view import GenericView
from app.controllers.data_writer import DataWriter
from app.authentification.auth_controller import AuthController
from app.models.user import User
from app.models.client import Client
from app.models.contract import Contract
from app.models.event import Event


# ==================================================================== #
#  CLASSE PRINCIPALE                                                   #
# ==================================================================== #
class DataWriterView(GenericView):
    # ---------------------------------------------------------------- #
    #  Construction
    # ---------------------------------------------------------------- #
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.writer = DataWriter(db_connection)
        self.auth = AuthController()

    # ---------------------------------------------------------------- #
    #  Helpers I/O
    # ---------------------------------------------------------------- #
    def _ask(self, prompt: str, cast=str,
             allow_empty: bool = False) -> Optional[Any]:
        """Petite fonction d’entrée avec cast + gestion du vide."""
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
        """Retourne un dict lisible d’un objet SQLAlchemy (sans hash pwd)."""
        return str({
            c.name: getattr(entity, c.name)
            for c in entity.__table__.columns
            if c.name != "password_hash"
        })

    # ================================================================= #
    #  ========================= COLLABORATEURS ======================= #
    # ================================================================= #
    def create_user_cli(self, current_user: Dict[str, Any]):
        fname = self._ask("Prénom : ")
        lname = self._ask("Nom : ")
        email = self._ask("Email : ")
        pwd = self._ask("Mot de passe : ")
        role_id = self._ask("Rôle (1=C, 2=S, 3=G) : ", int)

        with self.db.create_session() as s:
            try:
                usr = self.writer.create_user(
                    s, current_user,
                    employee_number=None,
                    first_name=fname, last_name=lname,
                    email=email,
                    password_hash=self.auth.hasher.hash(pwd),
                    role_id=role_id
                )
                s.commit()
                self.print_green("✅ Créé : " + self._fmt(usr))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def update_user_cli(self, current_user: Dict[str, Any]):
        emp_num = self._ask("Employee Number : ")
        with self.db.create_session() as s_chk:
            usr = s_chk.query(User).filter_by(employee_number=emp_num).first()
        if not usr:
            self.print_red("Collaborateur introuvable.")
            return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        role_id = self._ask(f"Rôle actuel {usr.role_id} (1=C,2=S,3=G) : ",
                            int, allow_empty=True)
        fname = self._ask(f"Prénom ({usr.first_name}) : ", allow_empty=True)
        lname = self._ask(f"Nom ({usr.last_name}) : ", allow_empty=True)
        email = self._ask(f"Email ({usr.email}) : ", allow_empty=True)
        pwd = self._ask("Nouveau mot de passe : ", allow_empty=True)

        upd: Dict[str, Any] = {}
        if role_id is not None:
            upd["role_id"] = role_id
        if fname:
            upd["first_name"] = fname
        if lname:
            upd["last_name"] = lname
        if email:
            upd["email"] = email
        if pwd:
            upd["password_hash"] = self.auth.hasher.hash(pwd)

        if not upd:
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                usr_mod = self.writer.update_user_by_employee_number(
                    s, current_user, emp_num, **upd)
                s.commit()
                self.print_green("✅ Modification : " + self._fmt(usr_mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def delete_user_cli(self, current_user: Dict[str, Any]):
        emp = self._ask("Employee Number à supprimer : ")
        with self.db.create_session() as s:
            try:
                self.writer.delete_user(s, current_user, emp)
                s.commit()
                self.print_green("✅ Collaborateur supprimé.")
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  ============================ CLIENTS =========================== #
    # ================================================================= #
    def create_client_cli(self, current_user: Dict[str, Any]):
        fn = self._ask("Nom complet : ")
        mail = self._ask("Email       : ")
        tel = self._ask("Téléphone   : ", allow_empty=True)
        comp = self._ask("Société     : ", allow_empty=True)

        with self.db.create_session() as s:
            try:
                cli = self.writer.create_client(
                    s, current_user,
                    full_name=fn, email=mail, phone=tel,
                    company_name=comp, commercial_id=None
                )
                s.commit()
                self.print_green("✅ Client créé : " + self._fmt(cli))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def update_client_cli(self, current_user: Dict[str, Any]):
        cid = self._ask("ID client : ", int)
        with self.db.create_session() as chk:
            cli = chk.get(Client, cid)
        if not cli:
            self.print_red("Client introuvable.")
            return
        if current_user["role"] == "commercial" and cli.commercial_id != current_user["id"]:
            self.print_red("Vous n’êtes pas responsable de ce client.")
            return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        new_fn = self._ask("Nom complet : ", allow_empty=True)
        new_em = self._ask("Email      : ", allow_empty=True)
        new_tel = self._ask("Téléphone  : ", allow_empty=True)
        new_comp = self._ask("Société    : ", allow_empty=True)

        upd = {k: v for k, v in
               [("full_name", new_fn), ("email", new_em),
                ("phone", new_tel), ("company_name", new_comp)]
               if v not in (None, "")}
        if not upd:
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                cli_mod = self.writer.update_client(
                    s, current_user, cid, **upd)
                s.commit()
                self.print_green("✅ Client modifié : " + self._fmt(cli_mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  ============================ CONTRATS ========================== #
    # ================================================================= #
    def create_contract_cli(self, current_user: Dict[str, Any]):
        if current_user["role"] == "commercial":
            self.print_red("Les commerciaux ne peuvent pas créer de contrat.")
            return

        cid = self._ask("ID client : ", int)
        tot = self._ask("Montant total : ", float)
        rem = self._ask("Montant restant : ", float)
        signed = self._ask("Signé ? (o/n) : ").lower() == "o"

        with self.db.create_session() as s:
            try:
                ctr = self.writer.create_contract(
                    s, current_user, cid, tot, rem, signed)
                s.commit()
                self.print_green("✅ Contrat créé : " + self._fmt(ctr))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def update_contract_cli(self, current_user: Dict[str, Any]):
        ctr_id = self._ask("ID contrat : ", int)

        if current_user["role"] == "commercial":
            with self.db.create_session() as chk:
                ctr = chk.get(Contract, ctr_id)
            if not ctr:
                self.print_red("Contrat introuvable.")
                return
            if ctr.commercial_id != current_user["id"]:
                self.print_red("Vous n’êtes pas responsable de ce contrat.")
                return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        n_cli = self._ask("Nouveau ID client : ", int, allow_empty=True)
        n_tot = self._ask("Montant total       : ", float, allow_empty=True)
        n_rem = self._ask("Montant restant     : ", float, allow_empty=True)

        signed_raw = self._ask("Signé ? (o/n/vide) : ", allow_empty=True)
        n_signed: Optional[bool] = None
        if signed_raw:
            if signed_raw.lower() in {"o", "oui", "y"}:
                n_signed = True
            elif signed_raw.lower() in {"n", "non"}:
                n_signed = False
            else:
                self.print_red("Réponse ‘signé’ invalide.")
                return

        upd: Dict[str, Any] = {}
        if n_cli is not None:
            upd["client_id"] = n_cli
        if n_tot is not None:
            upd["total_amount"] = n_tot
        if n_rem is not None:
            upd["remaining_amount"] = n_rem
        if n_signed is not None:
            upd["is_signed"] = n_signed

        if current_user["role"] != "commercial":
            com_emp = self._ask(
                "Employee Number commercial : ", allow_empty=True)
            if com_emp:
                with self.db.create_session() as tmp:
                    com = tmp.query(User).filter_by(
                        employee_number=com_emp, role_id=1).first()
                if not com:
                    self.print_red("Commercial introuvable.")
                    return
                upd["commercial_id"] = com.id

        if not upd:
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                ctr_mod = self.writer.update_contract(
                    s, current_user, ctr_id, **upd)
                s.commit()
                self.print_green("✅ Contrat modifié : " + self._fmt(ctr_mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  ========================== ÉVÉNEMENTS ========================== #
    # ================================================================= #
    def create_event_cli(self, current_user: Dict[str, Any]):
        """
        Création d’un événement – commercial uniquement
        Support obligatoire - le matricule est insensible à la casse.
        """
        if current_user["role"] != "commercial":
            self.print_red("Seul le commercial peut créer un événement.")
            return

        ctr_id = self._ask("ID contrat : ", int)
        with self.db.create_session() as chk:
            ctr = chk.get(Contract, ctr_id)
        if not ctr:
            self.print_red("Contrat introuvable.")
            return
        if ctr.commercial_id != current_user["id"]:
            self.print_red("Vous ne gérez pas ce contrat.")
            return
        if not ctr.is_signed:
            self.print_red("Le contrat n'est pas signé.")
            return

        # Support
        sup_emp = self._ask("Employee Number support : ").strip().upper()
        with self.db.create_session() as s_sup:
            sup = s_sup.query(User).filter_by(employee_number=sup_emp).first()
        if not sup or sup.role_id != 2:
            self.print_red("Support introuvable ou rôle incorrect.")
            return
        sup_id = sup.id

        # Dates
        start_raw = self._ask("Date début YYYY-MM-DD (vide = aujourd’hui) : ",
                              allow_empty=True)
        if start_raw:
            try:
                start_dt = datetime.strptime(start_raw, "%Y-%m-%d")
            except ValueError:
                self.print_red("Format attendu : YYYY-MM-DD.")
                return
        else:
            start_dt = datetime.combine(date.today(), time.min)

        end_raw = self._ask("Date fin   YYYY-MM-DD : ")
        try:
            end_dt = datetime.strptime(end_raw, "%Y-%m-%d")
        except ValueError:
            self.print_red("Format attendu : YYYY-MM-DD.")
            return

        if end_dt < start_dt:
            self.print_red(
                "La date de fin doit être postérieure à la date début.")
            return

        loc = self._ask("Lieu (vide)           : ", allow_empty=True)
        att = self._ask("Participants (vide)   : ", int, allow_empty=True)
        notes = self._ask("Notes (vide)          : ", allow_empty=True)

        with self.db.create_session() as s:
            try:
                ev = self.writer.create_event(
                    s, current_user,
                    contract_id=ctr_id,
                    support_id=sup_id,
                    date_start=start_dt,
                    date_end=end_dt,
                    location=loc,
                    attendees=att,
                    notes=notes
                )
                s.commit()
                self.print_green("✅ Événement créé : " + self._fmt(ev))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def list_events_no_support(self, current_user: Dict[str, Any]):
        with self.db.create_session() as s:
            evs = s.query(Event).filter_by(support_id=None).all()
            if not evs:
                self.print_yellow("Aucun événement sans support.")
                return
            self.print_green("--- Événements sans support ---")
            for ev in evs:
                print(self._fmt(ev))

    def assign_support_cli(self,
                           current_user: Dict[str, Any],
                           event_id: Optional[int] = None,
                           support_emp: Optional[str] = None):
        if event_id is None:
            event_id = self._ask("ID événement : ", int)
        if support_emp is None:
            support_emp = self._ask("Employee Number du support : ")

        support_emp = support_emp.strip().upper()

        with self.db.create_session() as s:
            sup = s.query(User).filter_by(employee_number=support_emp).first()
            if not sup:
                self.print_red("Support introuvable.")
                return
            if sup.role_id != 2:
                self.print_red("L’utilisateur trouvé n’a pas le rôle support.")
                return

            try:
                ev = self.writer.update_event(
                    s, current_user, event_id, support_id=sup.id)
                s.commit()
                self.print_green("✅ Support assigné : " + self._fmt(ev))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")
