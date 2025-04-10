import os
import datetime
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.user import User


class AuthController:
    """
    Contrôleur d'authentification : enregistrement, authentification et gestion des tokens JWT.
    """

    def __init__(self):
        self.hasher = PasswordHasher()
        self.jwt_secret = os.getenv("JWT_SECRET", "default_secret_key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_minutes = int(
            os.getenv("JWT_EXPIRATION_MINUTES", "60"))

    def register_user(self, session, employee_number, first_name, last_name, email, password, role_id):
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
        user = session.query(User).filter_by(email=email).first()
        if user is None:
            return None
        try:
            self.hasher.verify(user.password_hash, password)
            return user
        except VerifyMismatchError:
            return None

    def generate_token(self, user):
        payload = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.name,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=self.jwt_expiration_minutes)
        }
        token = jwt.encode(payload, self.jwt_secret,
                           algorithm=self.jwt_algorithm)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    def verify_token(self, token):
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignatureError:
            raise Exception("Le jeton est expiré.")
        except jwt.InvalidTokenError:
            raise Exception("Jeton invalide.")

    def is_authorized(self, token, required_role):
        payload = self.verify_token(token)
        user_role = payload.get("role")
        if isinstance(required_role, list):
            return user_role in required_role
        return user_role == required_role
