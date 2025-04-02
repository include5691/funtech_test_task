from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.api.deps import get_session
from src.db.models.user import User
from src.core.security import get_hash, authenticate_user, create_access_token
from src.schemas.user import UserCreate, UserRead
from src.schemas.token import Token

auth_router = APIRouter()

@auth_router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register_user(user_in: UserCreate, session: Session = Depends(get_session)):
    "Register a new user"
    if session.query(User).filter_by(email=user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=user_in.email, hashed_password=get_hash(user_in.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@auth_router.post("/token/", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    "Login and get access token"
    user = authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}