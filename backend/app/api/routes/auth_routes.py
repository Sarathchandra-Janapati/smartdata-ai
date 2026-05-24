from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.mysql_db import get_db, get_user_by_username, get_user_by_email, create_user
from app.database.models import UserRegister, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.utils.validators import validate_email, validate_password, validate_username
from app.core.logger import api_logger

router = APIRouter()


@router.post("/register", status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    validate_username(payload.username)
    validate_email(payload.email)
    validate_password(payload.password)

    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(payload.password)
    user = create_user(db, payload.username, payload.email, hashed, payload.role)
    api_logger.info(f"New user registered: {payload.username}")
    return {"message": "User registered successfully", "username": user.username, "role": user.role}


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form.username)
    if not user or not verify_password(form.password, user.password):
        api_logger.warning(f"Failed login attempt for: {form.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": user.username, "role": user.role})
    api_logger.info(f"User logged in: {user.username}")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}
