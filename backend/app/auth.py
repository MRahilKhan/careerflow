import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from .models import User


# ============================================================
# JWT CONFIGURATION
# ============================================================

SECRET_KEY = os.getenv("CAREERFLOW_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "CAREERFLOW_SECRET_KEY is not configured"
    )

if len(SECRET_KEY) < 32:
    raise RuntimeError(
        "CAREERFLOW_SECRET_KEY must contain at least 32 characters"
    )


ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


# ============================================================
# AUTHENTICATION
# ============================================================

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return pwd.verify(
            password,
            password_hash,
        )
    except Exception:
        # Never expose password-hashing errors to the client.
        return False


# ============================================================
# TOKEN CREATION
# ============================================================

def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    expires = now + timedelta(
        minutes=ACCESS_TOKEN_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "jti": uuid4().hex,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ============================================================
# CURRENT USER
# ============================================================

def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        security
    ),
    db: Session = Depends(get_db),
) -> User:

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        # Only CareerFlow access tokens are accepted.
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        subject = payload.get("sub")

        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        try:
            user_id = int(subject)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

    except HTTPException:
        raise

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    user = db.get(
        User,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user
