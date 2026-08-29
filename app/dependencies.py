from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from app.config import settings
from app.database import get_db
from app.models import User
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credential_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise credential_exceptions
    except InvalidTokenError:
        raise credential_exceptions
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credential_exceptions
    return user