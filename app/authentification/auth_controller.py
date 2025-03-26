import os
import datetime
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.user import User


class AuthController:
    """
    Contrôleur d'authentification qui gère l'enregistrement, l'authentification
    et la gestion des jetons JWT pour l'accès persistant.
    """

    def __init__(self):
        self.hasher = PasswordHasher()
        # Lecture du secret, de l'algorithme et de la durée d'expiration depuis l'environnement (définis dans .env)
        self.jwt_secret = os.getenv("JWT_SECRET", "default_secret_key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_minutes = int(
            os.getenv("JWT_EXPIRATION_MINUTES", "60"))

    def register_user(self, session, employee_number, first_name, last_name, email, password, role_id):
        """
        Enregistre un nouvel utilisateur après avoir haché son mot de passe.
        """
        password_hash = self.hasher.hash(password)
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
        Authentifie un utilisateur en vérifiant son email et son mot de passe.
        Retourne l'utilisateur si l'authentification réussit, sinon None.
        """
        user = session.query(User).filter_by(email=email).first()
        if user is None:
            return None

        try:
            self.hasher.verify(user.password_hash, password)
            return user
        except VerifyMismatchError:
            return None

    def generate_token(self, user):
        """
        Génère un jeton JWT pour un utilisateur authentifié.
        Le payload inclut l'identifiant de l'utilisateur, son email, son rôle et la date d'expiration.
        """
        payload = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.name,  # Assurez-vous que la relation role est chargée
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=self.jwt_expiration_minutes)
        }
        token = jwt.encode(payload, self.jwt_secret,
                           algorithm=self.jwt_algorithm)
        # PyJWT retourne une chaîne dans les versions récentes ; sinon, décodage en UTF-8
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    def verify_token(self, token):
        """
        Vérifie et décode un jeton JWT.
        Lève une exception si le jeton est expiré ou invalide.
        Retourne le payload si tout est correct.
        """
        try:
            payload = jwt.decode(token, self.jwt_secret,
                                 algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Le jeton est expiré.")
        except jwt.InvalidTokenError:
            raise Exception("Jeton invalide.")

    def is_authorized(self, token, required_role):
        """
        Vérifie si le jeton contient un rôle autorisé.
        'required_role' peut être une chaîne ou une liste de rôles acceptés.
        Retourne True si le rôle dans le jeton est autorisé, sinon False.
        """
        payload = self.verify_token(token)
        user_role = payload.get("role")
        if isinstance(required_role, list):
            return user_role in required_role
        return user_role == required_role
