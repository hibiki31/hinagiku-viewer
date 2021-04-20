import os
import jwt
import secrets

from datetime import datetime, timedelta
from typing import List, Optional
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from fastapi import APIRouter, Depends, Request, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from mixins.database import get_db
from mixins.log import setup_logger
from mixins import settings

from .models import *
from .schemas import *


logger = setup_logger(__name__)
app = APIRouter()



    

# JWTトークンの設定
if settings.IS_DEV:
    SECRET_KEY = "KEY"
else:
    SECRET_KEY = secrets.token_urlsafe(128)
ALGORITHM = "HS256"
# 30日で失効
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

# パスワードハッシュ化の設定
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)
# oAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth",
    auto_error=False
)


#  トークン生成
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme), 
        db: Session = Depends(get_db)
    ):
    # ペイロード確認
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Illegal credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user = db.query(UserModel).filter(UserModel.id==user_id).one()
    except:
        raise HTTPException(status_code=400, detail="Bad token")

    return UserCurrent(id=user_id, token=token, is_admin=user.is_admin)


@app.post("/api/auth", response_model=TokenRFC6749Response, tags=["auth"])
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), 
        db: Session = Depends(get_db)
    ):

    try:
        user = db.query(UserModel).filter(UserModel.id==form_data.username).one()
    except:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "scopes": form_data.scopes,
            "role": user.is_admin,
            },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/setup", tags=["auth"])
async def api_auth_setup(
        user: UserPost, 
        db: Session = Depends(get_db)
    ):
    if not db.query(UserModel).all() == []:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already initialized"
        )

    db.add(UserModel(
        id=user.id, 
        password=pwd_context.hash(user.password),
        is_admin=True
    ))
    db.commit()

    return user


@app.get("/api/auth/validate", tags=["auth"])
async def read_auth_validate(
        current_user: UserCurrent = Depends(get_current_user)
    ):
    return {"access_token": current_user.token, "token_type": "bearer"}



@app.get("/api/users/me/", tags=["user"], response_model=UserGet)
async def read_users_me(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):

    user = db.query(UserModel).filter(UserModel.id == current_user.id).one()
   
    return user


@app.post("/api/users", tags=["user"])
async def post_api_users(
        user: UserPost, 
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    db.add(UserModel(
        id=user.id, 
        password=pwd_context.hash(user.password),
        is_admin=False
        ))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request user already exists"
        )

    return user


@app.get("/api/users", tags=["user"],response_model=List[UserGet])
async def get_api_users(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ): 
    return db.query(UserModel).all()