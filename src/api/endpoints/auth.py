from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.deps import get_session
from src.db.models.user import User
from src.core.security import get_hash
from src.schemas.user import UserCreate, UserRead

auth_router = APIRouter()

@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register_user(*, session: Session = Depends(get_session), user_in: UserCreate):
    "Register a new user"
    if session.query(User).filter_by(email=user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=user_in.email, hashed_password=get_hash(user_in.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user