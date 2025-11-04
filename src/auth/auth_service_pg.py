from __future__ import annotations
import os, time
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from passlib.hash import bcrypt
import jwt

# ---------- env ----------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
AUTH_SECRET = os.getenv("AUTH_SECRET_KEY", "dev-secret-change-me")
AUTH_TTL = int(os.getenv("AUTH_TOKEN_TTL_SECONDS", "86400"))

if not DATABASE_URL:
    raise RuntimeError("Missing DATABASE_URL in .env")

# ---------- engine ----------
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# ---------- helpers ----------
def _user_row_to_dict(row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row.get("full_name"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with engine.connect() as cx:
        res = cx.execute(
            text("select id, email, full_name, created_at, updated_at, password_hash from public.users where email=:e"),
            {"e": email.lower().strip()},
        ).mappings().first()
        if not res:
            return None
        d = _user_row_to_dict(res)
        d["password_hash"] = res["password_hash"]
        return d

def create_user(email: str, password: str, full_name: str = "") -> Tuple[bool, str]:
    email = email.lower().strip()
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if get_user_by_email(email):
        return False, "Email already registered."

    pwd_hash = bcrypt.hash(password)
    with engine.begin() as cx:
        cx.execute(
            text("""
                insert into public.users (email, password_hash, full_name)
                values (:e, :ph, :n)
            """),
            {"e": email, "ph": pwd_hash, "n": full_name},
        )
    return True, "Signup successful."

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.verify(password, password_hash)
    except Exception:
        return False

# ---------- tokens (optional) ----------
def make_token(user_id: str, email: str) -> str:
    now = int(time.time())
    payload = {"sub": user_id, "email": email, "iat": now, "exp": now + AUTH_TTL}
    return jwt.encode(payload, AUTH_SECRET, algorithm="HS256")

def parse_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except Exception:
        return None

# ---------- public API used by UIs ----------
def signup_email_password(email: str, password: str, full_name: str = "") -> Tuple[bool, str]:
    try:
        ok, msg = create_user(email, password, full_name)
        return ok, msg
    except Exception as e:
        return False, f"Signup error: {e}"

def login_email_password(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    user = get_user_by_email(email)
    if not user:
        return False, "User not found.", None
    if not verify_password(password, user["password_hash"]):
        return False, "Invalid credentials.", None
    user_public = {k: v for k, v in user.items() if k != "password_hash"}
    # token is optional; UIs may just stash user_public in session
    token = make_token(user_public["id"], user_public["email"])
    user_public["token"] = token
    return True, "Login successful.", user_public
    