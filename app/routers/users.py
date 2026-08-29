from app.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.schemas import UserOutput
router = APIRouter()

@router.get('/me', response_model=UserOutput)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user