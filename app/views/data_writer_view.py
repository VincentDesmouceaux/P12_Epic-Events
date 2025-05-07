# -*- coding: utf-8 -*-
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

import re
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
    #  Outils de validation dédiés
    # ---------------------------------------------------------------- #
    _REG_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
    _REG_PHONE = re.compile(r"^\+?\d{6,20}$")
    _REG_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def _ask_email(self, prompt: str,
                   allow_empty: bool = False) -> Optional[str]:
        while True:
            mail = self._ask(prompt, str, allow_empty)
            if mail in (None, "") and allow_empty:
                return None
            if self._REG_EMAIL.match(mail):
                return mail
            self.print_red("Format e‑mail invalide (ex. toto@mail.com).")

    def _ask_phone(self, prompt: str,
                   allow_empty: bool = False) -> Optional[str]:
        while True:
            tel = self._ask(prompt, str, allow_empty)
            if tel in (None, "") and allow_empty:
                return None
            if self._REG_PHONE.match(tel):
                return tel
            self.print_red("Numéro invalide (6‑20 chiffres, ‘+’ optionnel).")

    def _ask_positive_float(self, prompt: str,
                            allow_empty: bool = False) -> Optional[float]:
        while True:
            val = self._ask(prompt, float, allow_empty)
            if val is None and allow_empty:
                return None
            if val is not None and val >= 0:
                return val
            self.print_red("Nombre positif requis.")

    def _ask_positive_int(self, prompt: str,
                          allow_empty: bool = False) -> Optional[int]:
        while True:
            val = self._ask(prompt, int, allow_empty)
            if val is None and allow_empty:
                return None
            if val is not None and val >= 0:
                return val
            self.print_red("Entier positif requis.")

    def _ask_date(self, prompt: str,
                  allow_empty: bool = False) -> Optional[datetime]:
        while True:
            raw = self._ask(prompt, str, allow_empty)
            if raw in (None, "") and allow_empty:
                return None
            if self._REG_DATE.match(raw):
                try:
                    return datetime.strptime(raw, "%Y-%m-%d")
                except ValueError:
                    pass
            self.print_red("Format YYYY‑MM‑DD requis.")

    # ---------------------------------------------------------------- #
    #  Helper générique
    # ---------------------------------------------------------------- #
    def _ask(self, prompt: str, cast=str,
             allow_empty: bool = False) -> Optional[Any]:
        while True:
            # ---------- PARE‑FEU UNICODE ----------------------------- #
            try:
                raw = input(self.CYAN + prompt + self.END).strip()
            except (KeyboardInterrupt, EOFError):
                print()
                self.print_yellow("Saisie interrompue – au revoir.")
                raise SystemExit(0)
            except UnicodeDecodeError:
                # bug rarissime : on redemande la saisie proprement
                self.print_red("Erreur d’encodage – recommencez.")
                continue
            # --------------------------------------------------------- #
            if raw == "" and allow_empty:
                return None
            if raw == "":
                self.print_red("Valeur obligatoire.")
                continue
            if not callable(cast):        # sécurité supplémentaire
                cast = str
            try:
                return cast(raw) if cast else raw
            except (ValueError, TypeError):
                self.print_red("Format invalide.")

    def _fmt(self, entity) -> str:
        return str({
            c.name: getattr(entity, c.name)
            for c in entity.__table__.columns
            if c.name != "password_hash"
        })

    # ================================================================= #
    #  ========================= COLLABORATEURS ======================= #
    # ================================================================= #
    def create_user_cli(self, cur: Dict[str, Any]):
        fname = self._ask("Prénom : ")
        lname = self._ask("Nom : ")
        email = self._ask_email("Email : ")
        pwd = self._ask("Mot de passe : ")
        role = self._ask_positive_int("Rôle (1=C, 2=S, 3=G) : ")

        with self.db.create_session() as s:
            try:
                usr = self.writer.create_user(
                    s, cur, None, fname, lname, email,
                    self.auth.hasher.hash(pwd), role
                )
                s.commit()
                self.print_green("✅ Créé : " + self._fmt(usr))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def update_user_cli(self, cur: Dict[str, Any]):
        emp_num = self._ask("Employee Number : ")
        with self.db.create_session() as s_chk:
            usr = s_chk.query(User).filter_by(employee_number=emp_num).first()
        if not usr:
            self.print_red("Collaborateur introuvable.")
            return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        role_id = self._ask_positive_int(
            f"Rôle actuel {usr.role_id} (1=C,2=S,3=G) : ", True)
        fname = self._ask(f"Prénom ({usr.first_name}) : ", allow_empty=True)
        lname = self._ask(f"Nom ({usr.last_name}) : ", allow_empty=True)
        email = self._ask_email(f"Email ({usr.email}) : ", True)
        pwd = self._ask("Nouveau mot de passe : ", allow_empty=True)

        updates: Dict[str, Any] = {}
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
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                mod = self.writer.update_user_by_employee_number(
                    s, cur, emp_num, **updates)
                s.commit()
                self.print_green("✅ Modification : " + self._fmt(mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def delete_user_cli(self, cur: Dict[str, Any]):
        emp = self._ask("Employee Number à supprimer : ")
        with self.db.create_session() as s:
            try:
                self.writer.delete_user(s, cur, emp)
                s.commit()
                self.print_green("✅ Collaborateur supprimé.")
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  ============================ CLIENTS =========================== #
    # ================================================================= #
    def create_client_cli(self, cur: Dict[str, Any]):
        fn = self._ask("Nom complet : ")
        mail = self._ask_email("Email       : ")
        tel = self._ask_phone("Téléphone   : ", True)
        comp = self._ask("Société     : ", allow_empty=True)

        with self.db.create_session() as s:
            try:
                cli = self.writer.create_client(
                    s, cur, fn, mail, tel, comp, None
                )
                s.commit()
                self.print_green("✅ Client créé : " + self._fmt(cli))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def update_client_cli(self, cur: Dict[str, Any]):
        cid = self._ask_positive_int("ID client : ")
        with self.db.create_session() as chk:
            cli = chk.get(Client, cid)
        if not cli:
            self.print_red("Client introuvable.")
            return
        if cur["role"] == "commercial" and cli.commercial_id != cur["id"]:
            self.print_red("Vous n’êtes pas responsable de ce client.")
            return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        new_fn = self._ask("Nom complet : ", allow_empty=True)
        new_em = self._ask_email("Email      : ", True)
        new_tel = self._ask_phone("Téléphone  : ", True)
        new_co = self._ask("Société    : ", allow_empty=True)

        updates = {k: v for k, v in
                   [("full_name", new_fn), ("email", new_em),
                    ("phone", new_tel), ("company_name", new_co)]
                   if v not in (None, "")}
        if not updates:
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                mod = self.writer.update_client(s, cur, cid, **updates)
                s.commit()
                self.print_green("✅ Client modifié : " + self._fmt(mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  ============================ CONTRATS ========================== #
    # ================================================================= #
    def create_contract_cli(self, cur: Dict[str, Any]):
        if cur["role"] == "commercial":
            self.print_red("Les commerciaux ne peuvent pas créer de contrat.")
            return

        cid = self._ask_positive_int("ID client : ")
        tot = self._ask_positive_float("Montant total : ")
        rem = self._ask_positive_float("Montant restant : ")
        signe = self._ask("Signé ? (o/n) : ").lower() == "o"

        with self.db.create_session() as s:
            try:
                ctr = self.writer.create_contract(
                    s, cur, cid, tot, rem, signe)
                s.commit()
                self.print_green("✅ Contrat créé : " + self._fmt(ctr))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def update_contract_cli(self, cur: Dict[str, Any]):
        ctr_id = self._ask_positive_int("ID contrat : ")

        if cur["role"] == "commercial":
            with self.db.create_session() as chk:
                ctr = chk.get(Contract, ctr_id)
            if not ctr:
                self.print_red("Contrat introuvable.")
                return
            if ctr.commercial_id != cur["id"]:
                self.print_red("Vous n’êtes pas responsable de ce contrat.")
                return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        n_cli = self._ask_positive_int("Nouveau ID client : ", True)
        n_tot = self._ask_positive_float("Montant total       : ", True)
        n_rem = self._ask_positive_float("Montant restant     : ", True)

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

        updates: Dict[str, Any] = {}
        if n_cli is not None:
            updates["client_id"] = n_cli
        if n_tot is not None:
            updates["total_amount"] = n_tot
        if n_rem is not None:
            updates["remaining_amount"] = n_rem
        if n_signed is not None:
            updates["is_signed"] = n_signed

        if cur["role"] != "commercial":
            com_emp = self._ask(
                "Employee Number commercial : ", cast=str, allow_empty=True)
            if com_emp:
                with self.db.create_session() as tmp:
                    com = tmp.query(User).filter_by(
                        employee_number=com_emp, role_id=1).first()
                if not com:
                    self.print_red("Commercial introuvable.")
                    return
                updates["commercial_id"] = com.id

        if not updates:
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                mod = self.writer.update_contract(
                    s, cur, ctr_id, **updates)
                s.commit()
                self.print_green("✅ Contrat modifié : " + self._fmt(mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  ========================== ÉVÉNEMENTS ========================== #
    # ================================================================= #
    def create_event_cli(self, cur: Dict[str, Any]):
        if cur["role"] != "commercial":
            self.print_red("Seul le commercial peut créer un événement.")
            return

        ctr_id = self._ask_positive_int("ID contrat : ")
        with self.db.create_session() as chk:
            ctr = chk.get(Contract, ctr_id)
        if not ctr:
            self.print_red("Contrat introuvable.")
            return
        if ctr.commercial_id != cur["id"]:
            self.print_red("Vous ne gérez pas ce contrat.")
            return
        if not ctr.is_signed:
            self.print_red("Le contrat n'est pas signé.")
            return

        sup_emp = self._ask("Employee Number support : ").strip().upper()
        with self.db.create_session() as s_sup:
            sup = s_sup.query(User).filter_by(employee_number=sup_emp).first()
        if not sup or sup.role_id != 2:
            self.print_red("Support introuvable ou rôle incorrect.")
            return
        sup_id = sup.id

        start_dt = self._ask_date(
            "Date début YYYY-MM-DD (vide = aujourd’hui) : ", True)
        if start_dt is None:
            start_dt = datetime.combine(date.today(), time.min)

        end_dt = self._ask_date("Date fin   YYYY-MM-DD : ")
        if end_dt < start_dt:
            self.print_red(
                "La date fin doit être postérieure à la date début.")
            return

        loc = self._ask("Lieu (vide)           : ", allow_empty=True)
        att = self._ask_positive_int("Participants (vide)   : ", True)
        notes = self._ask("Notes (vide)          : ", allow_empty=True)

        with self.db.create_session() as s:
            try:
                ev = self.writer.create_event(
                    s, cur, ctr_id, sup_id, start_dt, end_dt,
                    loc, att, notes)
                s.commit()
                self.print_green("✅ Événement créé : " + self._fmt(ev))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    def list_events_no_support(self, cur: Dict[str, Any]):
        with self.db.create_session() as s:
            evs = s.query(Event).filter_by(support_id=None).all()
            if not evs:
                self.print_yellow("Aucun événement sans support.")
                return
            self.print_green("--- Événements sans support ---")
            for ev in evs:
                print(self._fmt(ev))

    def assign_support_cli(self, cur: Dict[str, Any],
                           event_id: Optional[int] = None,
                           support_emp: Optional[str] = None):
        if event_id is None:
            event_id = self._ask_positive_int("ID événement : ")
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
                    s, cur, event_id, support_id=sup.id)
                s.commit()
                self.print_green("✅ Support assigné : " + self._fmt(ev))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")

    # ================================================================= #
    #  =======  ÉVÉNEMENTS – SOUS-MENU SUPPORT  =======                 #
    # ================================================================= #
    def menu_event_support(self, cur: Dict[str, Any]) -> None:
        while True:
            self.print_header("-- Événements (support) --")
            print(self.BLUE + "[1] Mes événements" + self.END)
            print(self.BLUE + "[2] Mettre à jour un événement" + self.END)
            print(self.BLUE + "[0] Retour" + self.END)
            ch = input(self.CYAN + "Choix : " + self.END).strip()

            if ch == "1":
                self._display_my_events(cur)
            elif ch == "2":
                self._update_my_event_cli(cur)
            elif ch == "0":
                break
            else:
                self.print_red("Option invalide.")

    def _display_my_events(self, cur: Dict[str, Any]) -> None:
        with self.db.create_session() as s:
            evts = s.query(Event).filter_by(support_id=cur["id"]).all()
            if not evts:
                self.print_yellow("Aucun événement ne vous est attribué.")
                return
            self.print_green("--- Vos événements ---")
            for ev in evts:
                print(self._fmt(ev))

    def _update_my_event_cli(self, cur: Dict[str, Any]) -> None:
        ev_id = self._ask_positive_int("ID événement à modifier : ")

        with self.db.create_session() as chk:
            ev = chk.get(Event, ev_id)
        if not ev:
            self.print_red("Événement introuvable.")
            return
        if ev.support_id != cur["id"]:
            self.print_red("Vous n'êtes pas assigné à cet événement.")
            return

        self.print_yellow("→ Laisser vide pour conserver la valeur.")
        new_loc = self._ask("Lieu : ", allow_empty=True)
        new_notes = self._ask("Notes : ", allow_empty=True)

        n_start = self._ask_date("Date début YYYY-MM-DD : ", True)
        n_end = self._ask_date("Date fin   YYYY-MM-DD : ", True)

        if n_start and n_end and n_end < n_start:
            self.print_red("Date fin < date début.")
            return

        n_att = self._ask_positive_int("Participants : ", True)

        updates: Dict[str, Any] = {}
        if new_loc:
            updates["location"] = new_loc
        if new_notes:
            updates["notes"] = new_notes
        if n_start:
            updates["date_start"] = n_start
        if n_end:
            updates["date_end"] = n_end
        if n_att is not None:
            updates["attendees"] = n_att

        if not updates:
            self.print_yellow("Aucune modification.")
            return

        with self.db.create_session() as s:
            try:
                mod = self.writer.update_event(s, cur, ev_id, **updates)
                s.commit()
                self.print_green("✅ Événement mis à jour : " + self._fmt(mod))
            except Exception as exc:
                s.rollback()
                self.print_red(f"❌ {exc}")
