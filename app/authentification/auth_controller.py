from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.user import User


class AuthController:
    """
    Contrôleur d'authentification qui gère l'enregistrement et la vérification
    des utilisateurs. Utilise argon2 pour hacher et vérifier les mots de passe.
    """

    def __init__(self):
        self.hasher = PasswordHasher()

    def register_user(self, session, employee_number, first_name, last_name, email, password, role_id):
        """
        Enregistre un nouvel utilisateur après avoir haché son mot de passe.
        """
        # Hachage du mot de passe
        password_hash = self.hasher.hash(password)

        # Création de l'utilisateur
        user = User(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id
        )
        session.add(user)
        session.commit()
        return user

    def authenticate_user(self, session, email, password):
        """
        Authentifie un utilisateur en vérifiant son email et le mot de passe.
        Retourne l'utilisateur si l'authentification réussit, sinon None.
        """
        user = session.query(User).filter_by(email=email).first()
        if user is None:
            return None

        try:
            # Vérifie le mot de passe fourni contre le hachage stocké
            self.hasher.verify(user.password_hash, password)
            return user
        except VerifyMismatchError:
            return None
