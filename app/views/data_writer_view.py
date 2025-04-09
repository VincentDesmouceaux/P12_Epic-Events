from app.controllers.data_writer import DataWriter
from datetime import datetime


class DataWriterView:
    """
    Vue pour la création et la mise à jour des données dans l'application CRM.
    Encapsule l'utilisation du contrôleur DataWriter.
    """

    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.writer = DataWriter(self.db_conn)

    def run(self):
        """
        Version 'interactive' existante : simule un utilisateur 'gestion', crée
        et met à jour un user, un contrat, un event, etc.
        Ajout de prints pour debug.
        """
        session = self.db_conn.create_session()
        current_user = {"id": 1, "role": "gestion"}

        print("\n[DEBUG] DataWriterView.run() - START")
        print("[DEBUG] current_user =", current_user)

        # Créer un collaborateur
        print("[DEBUG] Creating user with role_id=2 ...")
        try:
            new_user = self.writer.create_user(
                session,
                current_user,
                employee_number="EMP123",
                first_name="Jean",
                last_name="Dupont",
                email="jean.dupont@example.com",
                password_hash="hashed_value",  # En production, hacher le mot de passe
                role_id=2  # ex. ID du rôle "commercial"
            )
            print("[DEBUG] new_user =", new_user)
            if new_user:
                print("[DEBUG] new_user.id =", new_user.id)
        except Exception as e:
            print("[DEBUG] Exception creating user:", e)
            session.rollback()

        # Mettre à jour ce collaborateur
        # (uniquement si new_user a bien été créé)
        if 'new_user' in locals() and new_user:
            try:
                updated_user = self.writer.update_user(
                    session,
                    current_user,
                    new_user.id,
                    first_name="Jean-Pierre",
                    email="jp.dupont@example.com"
                )
                print("[DEBUG] updated_user.first_name =",
                      updated_user.first_name)
                print("[DEBUG] updated_user.email =", updated_user.email)
            except Exception as e:
                print("[DEBUG] Exception updating user:", e)
                session.rollback()

        # Créer un contrat
        print("[DEBUG] Creating contract ...")
        if 'new_user' in locals() and new_user:
            try:
                new_contract = self.writer.create_contract(
                    session,
                    current_user,
                    client_id=1,           # Exemple d'ID client
                    commercial_id=new_user.id,
                    total_amount=10000.0,
                    remaining_amount=5000.0,
                    is_signed=True
                )
                print("[DEBUG] new_contract.id =",
                      new_contract.id if new_contract else None)
            except Exception as e:
                print("[DEBUG] Exception creating contract:", e)
                session.rollback()

        # Mettre à jour le contrat
        if 'new_contract' in locals() and new_contract:
            try:
                updated_contract = self.writer.update_contract(
                    session,
                    current_user,
                    new_contract.id,
                    remaining_amount=0.0,
                    is_signed=True
                )
                print("[DEBUG] updated_contract.remaining_amount =",
                      updated_contract.remaining_amount)
            except Exception as e:
                print("[DEBUG] Exception updating contract:", e)
                session.rollback()

        # Créer un événement
        print("[DEBUG] Creating event ...")
        if 'new_contract' in locals() and new_contract:
            try:
                new_event = self.writer.create_event(
                    session,
                    current_user,
                    contract_id=new_contract.id,
                    support_id=3,  # Exemple d'ID pour un support
                    date_start=datetime(2023, 6, 4, 13, 0),
                    date_end=datetime(2023, 6, 5, 2, 0),
                    location="53 Rue du Château, 41120 Candé-sur-Beuvron, France",
                    attendees=75,
                    notes="Wedding starts at 3PM, by the river."
                )
                print("[DEBUG] new_event.id =",
                      new_event.id if new_event else None)
            except Exception as e:
                print("[DEBUG] Exception creating event:", e)
                session.rollback()

        # Mettre à jour l'événement
        if 'new_event' in locals() and new_event:
            try:
                updated_event = self.writer.update_event(
                    session,
                    current_user,
                    new_event.id,
                    attendees=80,
                    notes="Updated notes for the event."
                )
                print("[DEBUG] updated_event.attendees =",
                      updated_event.attendees)
                print("[DEBUG] updated_event.notes =", updated_event.notes)
            except Exception as e:
                print("[DEBUG] Exception updating event:", e)
                session.rollback()

        session.close()
        print("[DEBUG] DataWriterView.run() - END\n")

    # ---- Nouvelles méthodes CLI ----

    def create_user_cli(self, current_user, empnum, fname, lname, email, password_hash, role_id):
        """
        Crée un user via DataWriter, en évitant les prompts.
        """
        session = self.db_conn.create_session()
        try:
            user = self.writer.create_user(
                session,
                current_user,
                employee_number=empnum,
                first_name=fname,
                last_name=lname,
                email=email,
                password_hash=password_hash,
                role_id=role_id
            )
            print(f"Utilisateur créé : ID={user.id if user else 'None'}")
        except Exception as e:
            print(f"Erreur: {e}")
            session.rollback()
        finally:
            session.close()

    def update_user_cli(self, current_user, user_id, **updates):
        """
        Met à jour un user existant. Les champs modifiés sont passés en **updates.
        """
        session = self.db_conn.create_session()
        try:
            updated = self.writer.update_user(
                session,
                current_user,
                user_id,
                **updates
            )
            print(f"Utilisateur {updated.id} mis à jour.")
        except Exception as e:
            print(f"Erreur: {e}")
            session.rollback()
        finally:
            session.close()
