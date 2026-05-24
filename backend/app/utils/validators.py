import re
from fastapi import HTTPException


def validate_email(email: str) -> str:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    if not re.match(pattern, email):
        raise HTTPException(status_code=422, detail="Invalid email address")
    return email.lower()


def validate_password(password: str) -> str:
    if len(password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")
    return password


def validate_username(username: str) -> str:
    if not re.match(r"^[a-zA-Z0-9_]{3,50}$", username):
        raise HTTPException(status_code=422, detail="Username must be 3-50 alphanumeric characters or underscores")
    return username
