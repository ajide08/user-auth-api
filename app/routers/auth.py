from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas import UserInCreate, UserInLogin, UserOutput, TokenResponse, RefreshTokenRequest
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RefreshToken
from datetime import datetime, timedelta, timezone
from app.config import settings
from app.security import hash_password, verify_password, create_access_token, create_refresh_token, hash_refresh_token, hash_refresh_secret, verify_refresh_secret

router = APIRouter()

@router.post('/register', response_model=UserOutput, status_code=status.HTTP_201_CREATED)
def register(user: UserInCreate, db: Session = Depends(get_db)):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')
    existing_name = db.query(User).filter(User.name == user.name).first()
    if existing_name:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already taken')
    new_user = User(name=user.name, email=user.email, password_hash=hash_password(user.password)) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post('/login', response_model=TokenResponse)
def login(user: UserInLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(db_user.id)
    token_id, secret, raw_token = create_refresh_token()
    refresh_token = RefreshToken(
        token_id=token_id,
        user_id=db_user.id,
        token_hash=hash_refresh_secret(secret),
        expiration=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token)
    db.commit()
    return {'access_token': access_token, 'refresh_token': raw_token, 'token_type': 'bearer'}

@router.post('/refresh', response_model=TokenResponse)
def refresh_access_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        token_id, secret = data.refresh_token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    stored_token = db.query(RefreshToken).filter(RefreshToken.token_id == token_id).first()
    if stored_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    if stored_token.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token has been revoked')
    expiry = stored_token.expiration
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token has expired')
    if not verify_refresh_secret(secret, stored_token.token_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    stored_token.revoked = True
    db_user = db.query(User).filter(User.id == stored_token.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    new_access_token = create_access_token(stored_token.user_id)
    new_token_id, new_secret, new_raw_token = create_refresh_token()
    new_refresh_token = RefreshToken(
        token_id=new_token_id,
        user_id=stored_token.user_id,
        token_hash=hash_refresh_secret(new_secret),
        expiration=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_refresh_token)
    db.commit()
    return {
        "access_token": new_access_token,
        "refresh_token": new_raw_token,
        "token_type": "bearer",
    }

@router.post('/logout')
def logout(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        token_id, secret = data.refresh_token.split(".", 1)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    stored_token = (db.query(RefreshToken).filter(RefreshToken.token_id == token_id).first())
    if stored_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    if stored_token.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token has been revoked')
    expiry = stored_token.expiration
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token has expired')
    if not verify_refresh_secret(secret, stored_token.token_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    stored_token.revoked = True
    db.commit()
    return {"message": "Logged out successfully"}