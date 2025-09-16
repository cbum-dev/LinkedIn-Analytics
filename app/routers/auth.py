from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import SignupRequest, Token
from app.core.security import create_access_token, get_password_hash, verify_password

router = APIRouter()


@router.post("/signup", response_model=Token)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    role = UserRole(payload.role) if payload.role in {r.value for r in UserRole} else UserRole.user
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=user.email, role=user.role.value, expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(subject=user.email, role=user.role.value)
    return {"access_token": token, "token_type": "bearer"}
