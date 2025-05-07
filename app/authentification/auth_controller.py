# app/authentification/auth_controller.py
# -*- coding: utf-8 -*-
"""
Gestion de l’authentification, du hachage des mots de passe et des
jetons **JWT** pour l’application Epic Events.

Fonctions principales :
    • Enregistrer un collaborateur avec mot de passe chiffré (`register_user`)
    • Authentifier un utilisateur et retourner l’objet SQLAlchemy (`authenticate_user`)
    • Générer un JWT signé (`generate_token`)
    • Vérifier la validité / l’expiration d’un JWT (`verify_token`)
    • Vérifier qu’un utilisateur est autorisé pour un rôle donné
      à partir de son JWT (`is_authorized`)
"""

from __future__ import annotations

import datetime as dt
import os
from typing import List, Union, Dict, Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from app.models.user import User


class AuthController:
    """
    Contrôleur d’authentification.

    Attributs d’instance
    --------------------
    hasher : PasswordHasher
        Instance Argon2 pour hacher / vérifier les mots de passe.
    jwt_secret : str
        Clé secrète utilisée pour signer les JWT (``JWT_SECRET`` dans le
        ``.env`` ou valeur par défaut moins sûre).
    jwt_algorithm : str
        Algorithme de signature (par défaut « HS256 »).
    jwt_expiration_minutes : int
        Durée de validité des jetons générés, en minutes
        (``JWT_EXPIRATION_MINUTES`` dans le ``.env`` ou 60).
    """

    def __init__(self) -> None:
        self.hasher: PasswordHasher = PasswordHasher()
        self.jwt_secret: str = os.getenv("JWT_SECRET", "default_secret_key")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_minutes: int = int(
            os.getenv("JWT_EXPIRATION_MINUTES", "60")
        )

    # --------------------------------------------------------------------- #
    #  CRUD UTILISATEUR                                                     #
    # --------------------------------------------------------------------- #
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
        """
        Crée un utilisateur et enregistre son mot de passe (haché Argon2).

        Parameters
        ----------
        session : Session
            Session SQLAlchemy active.
        employee_number : str
            Matricule du collaborateur.
        first_name : str
            Prénom.
        last_name : str
            Nom.
        email : str
            Adresse e‑mail (unique).
        password : str
            Mot de passe en clair (sera haché).
        role_id : int
            Identifiant du rôle dans la table ``roles``.

        Returns
        -------
        User
            Instance du modèle nouvellement créée.
        """
        password_hash: str = self.hasher.hash(password)
        user = User(
            employee_number=employee_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
        )
        session.add(user)
        session.commit()
        return user

    # --------------------------------------------------------------------- #
    #  AUTHENTIFICATION                                                     #
    # --------------------------------------------------------------------- #
    def authenticate_user(
        self, session: Session, email: str, password: str
    ) -> User | None:
        """
        Vérifie les identifiants d’un utilisateur.

        Returns
        -------
        User | None
            L’objet utilisateur si les identifiants sont corrects,
            sinon ``None``.
        """
        user: User | None = session.query(User).filter_by(email=email).first()
        if user is None:
            return None
        try:
            self.hasher.verify(user.password_hash, password)
            return user
        except VerifyMismatchError:
            return None

    # --------------------------------------------------------------------- #
    #  JWT                                                                  #
    # --------------------------------------------------------------------- #
    def generate_token(self, user: User) -> str:
        """
        Génère un JWT signé contenant l’identifiant, l’e‑mail et le rôle.

        Le jeton expire automatiquement après ``jwt_expiration_minutes``.

        Returns
        -------
        str
            Chaîne JWT encodée.
        """
        payload: Dict[str, Any] = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.name,
            "exp": dt.datetime.utcnow() +
            dt.timedelta(minutes=self.jwt_expiration_minutes),
        }
        token: Union[str, bytes] = jwt.encode(
            payload, self.jwt_secret, algorithm=self.jwt_algorithm
        )
        return token.decode("utf-8") if isinstance(token, bytes) else token

    def verify_token(self, token: str) -> dict:
        """
        Décodage et validation d’un JWT.

        Raises
        ------
        Exception
            Si le jeton est expiré ou invalide.

        Returns
        -------
        dict
            Le payload décodé.
        """
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise Exception("Le jeton est expiré.") from exc
        except jwt.InvalidTokenError as exc:
            raise Exception("Jeton invalide.") from exc

    def is_authorized(
        self, token: str, required_role: Union[str, List[str]]
    ) -> bool:
        """
        Vérifie qu’un utilisateur possède l’un des rôles requis.

        Parameters
        ----------
        token : str
            Jeton JWT de l’utilisateur.
        required_role : str | list[str]
            Rôle (ou liste de rôles) autorisé(s).

        Returns
        -------
        bool
            ``True`` si l’utilisateur est autorisé, sinon ``False``.
        """
        payload = self.verify_token(token)
        user_role = payload.get("role")
        if isinstance(required_role, list):
            return user_role in required_role
        return user_role == required_role
