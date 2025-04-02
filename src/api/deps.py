import logging
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.core.config import settings
from src.db.models.user import User
from src.db.session import get_session

CredentialsException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
) -> User:
    "Get current user from token"
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise CredentialsException
    except JWTError:
        logging.error("JWTError: Invalid token")
        raise CredentialsException
    user = session.query(User).filter_by(email=email).first()
    if not user:
        logging.error("User not found")
        raise CredentialsException
    return user