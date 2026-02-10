from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mixins.database import get_db
from mixins.log import setup_logger
from settings import SECRET_KEY
from users.models import UserModel
from users.schemas import AuthValidateResponse, TokenRFC6749Response, UserCurrent, UserGet, UserPost

logger = setup_logger(__name__)
app = APIRouter()


# JWTトークンの設定
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


class CurrentUser(BaseModel):
    id: str
    token: str
    scopes: List[str] = []
    projects: List[str] = []
    def verify_scope(self, scopes, return_bool=False):
        # 要求Scopeでループ
        for request_scope in scopes:
            match_scoped = False
            # 持っているScopeでループ
            for having_scope in self.scopes:
                if having_scope in request_scope:
                    match_scoped = True
            # 持っているScopeが権限を持たない場合終了
            if not match_scoped:
                if return_bool:
                    return False
                raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not enough permissions",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
        # すべての要求Scopeをクリア
        return True



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 指定が無ければ24時間
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
    # ペイロード確認
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
    except Exception:
        # トークンがデコード出来なかった場合は認証失敗
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Illegal credentials",
            headers={"WWW-Authenticate": "Bearer"}
        ) from None

    try:
        # 正常なトークンだけどユーザが存在しない場合は認証失敗
        # もはやサーバー側のエラー
        user = db.query(UserModel).filter(UserModel.id==user_id).one()
    except Exception:
        raise HTTPException(status_code=401, detail="Illegal credentials") from None

    return UserCurrent(id=user_id, token=token, is_admin=user.is_admin)


@app.get("/api/users", tags=["User"],response_model=List[UserGet])
def list_users(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    return db.query(UserModel).all()


@app.get("/api/users/me/", tags=["User"], response_model=UserGet)
def get_current_user_info(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):

    user = db.query(UserModel).filter(UserModel.id == current_user.id).one()
    return user


@app.post("/api/users", tags=["User"])
def create_user(
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
        ) from None

    return user


@app.post("/api/auth", response_model=TokenRFC6749Response, tags=["Auth"])
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):

    try:
        user = db.query(UserModel).filter(UserModel.id==form_data.username).one()
    except Exception:
        raise HTTPException(status_code=401, detail="Incorrect username or password") from None

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.id,
            "scopes": form_data.scopes,
            "role": user.is_admin,
            },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/api/auth/setup", tags=["Auth"])
async def api_auth_setup(
        user: UserPost,
        db: Session = Depends(get_db)
    ):
    if user.id is None or user.id == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User id is brank"
        )

    # ユーザがいる場合はセットアップ済みなのでイジェクト
    if not db.query(UserModel).all() == []:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already initialized"
        )

    # ユーザ追加
    db.add(UserModel(
        id=user.id,
        password=pwd_context.hash(user.password),
        is_admin=True
    ))
    db.commit()

    return user


@app.get("/api/auth/validate", tags=["Auth"], response_model=AuthValidateResponse)
def validate_token(
        current_user: CurrentUser = Security(get_current_user, scopes=["user"])
    ):
    return {"access_token": current_user.token, "username": current_user.id, "token_type": "Bearer"}
