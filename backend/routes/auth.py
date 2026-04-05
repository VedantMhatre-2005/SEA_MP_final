"""Authentication routes with MongoDB-backed credentials."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from core.schemas import (
    AuthTokenResponse,
    AuthUser,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
)
from core.security import create_access_token, get_current_user, hash_password, verify_password
from db.mongo import LEGACY_USERS_COLLECTION, REGISTERED_USERS_COLLECTION, get_db

router = APIRouter(prefix="/auth")
logger = logging.getLogger(__name__)


def _users_collection(db):
    return db[REGISTERED_USERS_COLLECTION]


def _legacy_users_collection(db):
    return db[LEGACY_USERS_COLLECTION]


def _find_user_by_email(db, email: str):
    normalized = email.lower()
    user = _users_collection(db).find_one({"email": normalized})
    if user:
        return user, _users_collection(db)
    user = _legacy_users_collection(db).find_one({"email": normalized})
    if user:
        return user, _legacy_users_collection(db)
    return None, _users_collection(db)


@router.post("/register", response_model=MessageResponse)
async def register(payload: RegisterRequest) -> MessageResponse:
    try:
        logger.info("Registration started for %s", payload.email.lower())
        db = get_db()
        users = _users_collection(db)
        existing, _ = _find_user_by_email(db, payload.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        now = datetime.now(timezone.utc)
        users.insert_one(
            {
                "name": payload.name.strip(),
                "email": payload.email.lower(),
                "password_hash": hash_password(payload.password),
                "created_at": now,
            }
        )
        logger.info("Registration inserted user for %s", payload.email.lower())
        logger.info("Registration completed for %s", payload.email.lower())
        return MessageResponse(message="Registration successful. Please login.")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected registration failure for %s", payload.email.lower())
        raise HTTPException(status_code=500, detail=f"Registration failed: {type(exc).__name__}") from exc


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest) -> AuthTokenResponse:
    try:
        db = get_db()
        user, _ = _find_user_by_email(db, payload.email)
        if not user or not verify_password(payload.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = str(user["_id"])
        token = create_access_token(user_id)
        auth_user = AuthUser(id=user_id, name=user["name"], email=user["email"])
        return AuthTokenResponse(access_token=token, user=auth_user)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected login failure for %s", payload.email.lower())
        raise HTTPException(status_code=500, detail=f"Login failed: {type(exc).__name__}") from exc


@router.get("/me", response_model=AuthUser)
async def me(current_user: dict = Depends(get_current_user)) -> AuthUser:
    return AuthUser(**current_user)
