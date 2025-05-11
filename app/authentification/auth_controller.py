# -*- coding: utf-8 -*-
"""
Gestion de l’authentification, du hachage des mots de passe et des
jetons **JWT** pour l’application EpicEvents.

Fonctions :
    • register_user()  – création d’un collaborateur (hash Argon2)
    • authenticate_user()  – vérification e‑mail / mot de passe
    • generate_token()  – génération d’un JWT signé et horodaté
    • verify_token()    – décodage + contrôles d’intégrité / expiration
    • is_authorized()   – test d’appartenance à un ou plusieurs rôles
"""
from __future__ import annotations

import datetime as dt
import os
from typing import Any, Dict, List, Union

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from app.models.user import User

# --------------------------------------------------------------------------- #
# Chargement des variables d’environnement                                    #
# --------------------------------------------------------------------------- #
_JWT_SECRET: str | None = os.getenv("JWT_SECRET")          # obligatoire
if not _JWT_SECRET:
    raise RuntimeError(
        "Variable d’environnement JWT_SECRET manquante; "
        "merci de la renseigner dans .env ou votre gestionnaire de secrets."
    )

_JWT_ALGO: str = os.getenv("JWT_ALGORITHM")
_JWT_EXP_MIN: int = int(os.getenv("JWT_EXPIRATION_MINUTES"))


class AuthController:
    """Contrôleur d’authentification et d’autorisation (JWT)."""

    def __init__(self) -> None:
        self.hasher: PasswordHasher = PasswordHasher()
        self.jwt_secret: str = _JWT_SECRET
        self.jwt_algorithm: str = _JWT_ALGO
        self.jwt_expiration_minutes: int = _JWT_EXP_MIN

    # ------------------------------------------------------------------ #
    # CRUD UTILISATEUR                                                   #
    # ------------------------------------------------------------------ #
    def register_user(
        self,
        session: Session,
        employee_number: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        role_id: int,
    ) -> User:
        """Crée un utilisateur en hachant son mot de passe (Argon2)."""
        user = User(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=self.hasher.hash(password),
            role_id=role_id,
        )
        session.add(user)
        session.commit()
        return user

    # ------------------------------------------------------------------ #
    # AUTHENTIFICATION                                                   #
    # ------------------------------------------------------------------ #
    def authenticate_user(
        self, session: Session, email: str, password: str
    ) -> User | None:
        """Retourne l’objet User si les identifiants sont valides, sinon None."""
        user: User | None = session.query(User).filter_by(email=email).first()
        if user is None:
            return None
        try:
            self.hasher.verify(user.password_hash, password)
            return user
        except VerifyMismatchError:
            return None

    # ------------------------------------------------------------------ #
    # JWT                                                                 #
    # ------------------------------------------------------------------ #
    def generate_token(self, user: User) -> str:
        """Génère un JWT signé contenant id, e‑mail, rôle et date d’expiration."""
        payload: Dict[str, Any] = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.name,
            "exp": dt.datetime.utcnow() + dt.timedelta(
                minutes=self.jwt_expiration_minutes
            ),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str) -> dict:
        """Décode un JWT et lève une Exception explicite s’il est invalide."""
        try:
            return jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithm]
            )
        except jwt.ExpiredSignatureError as exc:
            raise Exception("Le jeton est expiré.") from exc
        except jwt.InvalidTokenError as exc:
            raise Exception("Jeton invalide.") from exc

    def is_authorized(
        self, token: str, required_role: Union[str, List[str]]
    ) -> bool:
        """Vérifie si le rôle contenu dans *token* appartient à *required_role*."""
        payload = self.verify_token(token)
        user_role = payload.get("role")
        if isinstance(required_role, list):
            return user_role in required_role
        return user_role == required_role
