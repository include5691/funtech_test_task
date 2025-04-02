from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.core.config import settings
from src.db.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"])

def verify_password(password: str, hash: str) -> bool:
    "Verify password with hash password"
    return pwd_context.verify(password, hash)

def get_hash(password: str) -> str:
    "Get hash password"
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    "Create access token"
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def authenticate_user(session: Session, email: str, password: str) -> User | None:
    "Authenticate user"
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return None
    if verify_password(password, user.hashed_password):
        return user