"""Sign-in: salted PBKDF2 password hashes + signed expiring tokens (standard library only).
Set SECRET_KEY in your environment (.env) before any real deployment."""
import base64, hashlib, hmac, json, os, secrets, time

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import User, get_db

SECRET = os.getenv("SECRET_KEY", "dev-only-change-me")


def hash_pw(pw: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    return salt + "$" + hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 200_000).hex()


def check_pw(pw: str, stored: str) -> bool:
    return hmac.compare_digest(hash_pw(pw, stored.split("$")[0]), stored)


def make_token(uid: int) -> str:
    body = base64.urlsafe_b64encode(json.dumps({"u": uid, "e": int(time.time()) + 86400}).encode()).decode()
    return body + "." + hmac.new(SECRET.encode(), body.encode(), "sha256").hexdigest()


def current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    try:
        body, sig = (authorization or "").removeprefix("Bearer ").split(".")
        if not hmac.compare_digest(sig, hmac.new(SECRET.encode(), body.encode(), "sha256").hexdigest()):
            raise ValueError
        data = json.loads(base64.urlsafe_b64decode(body))
        user = db.get(User, data["u"]) if data["e"] > time.time() else None
    except Exception:
        user = None
    if not user:
        raise HTTPException(401, "Please sign in again")
    return user
