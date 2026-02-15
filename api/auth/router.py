from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy.orm import Session

from auth.schemas import AuthValidateResponse, TokenRFC6749Response, UserCurrent, UserPost
from mixins.database import get_db
from mixins.log import setup_logger
from settings import SECRET_KEY
from users.models import UserModel

logger = setup_logger(__name__)
app = APIRouter(prefix="/api", tags=["Auth"])


# JWTトークンの設定
ALGORITHM = "HS256"
# 30日で失効
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30

# パスワードハッシュ化の設定（Argon2使用）
pwd_context = PasswordHash([Argon2Hasher()])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証する

    Args:
        plain_password: プレーンテキストのパスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        パスワードが一致する場合True
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    パスワードをハッシュ化する

    Args:
        password: ハッシュ化するパスワード

    Returns:
        ハッシュ化されたパスワード
    """
    return pwd_context.hash(password)
# oAuth2の設定
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth",
    auto_error=False
)


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


@app.post("/auth", summary="ログイン", response_model=TokenRFC6749Response)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
    ):
    """
    ログインしてアクセストークンを取得する

    OAuth2 Password Flowに準拠した認証エンドポイント。
    ユーザー名とパスワードを送信し、JWTアクセストークンを取得します。

    Args:
        form_data: OAuth2のフォームデータ（username, password）

    Returns:
        アクセストークンとトークンタイプ

    Raises:
        401: ユーザー名またはパスワードが間違っている場合
    """
    try:
        user = db.query(UserModel).filter(UserModel.id==form_data.username).one()
    except Exception:
        raise HTTPException(status_code=401, detail="Incorrect username or password") from None

    if not verify_password(form_data.password, user.password):
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


@app.post("/auth/setup", summary="初期セットアップ", response_model=UserCurrent)
async def api_auth_setup(
        user: UserPost,
        db: Session = Depends(get_db)
    ):
    """
    初回セットアップで管理者ユーザーを作成する

    システムに初めてアクセスする際に使用します。
    既にユーザーが存在する場合はエラーを返します。
    作成されたユーザーは管理者権限を持ちます。

    Args:
        user: ユーザー情報（ID、パスワード）

    Returns:
        作成された管理者ユーザー情報

    Raises:
        400: ユーザーIDが空、または既に初期化済みの場合
    """
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
        password=get_password_hash(user.password),
        is_admin=True
    ))
    db.commit()

    created_user = db.query(UserModel).filter(UserModel.id == user.id).one()

    # トークンを発行して返す
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": created_user.id,
            "scopes": [],
            "role": created_user.is_admin,
            },
        expires_delta=access_token_expires,
    )

    return UserCurrent(id=created_user.id, token=access_token, is_admin=created_user.is_admin)


@app.get("/auth/validate", summary="トークン検証", response_model=AuthValidateResponse)
def validate_token(
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    JWTトークンを検証し、ユーザー情報を返す

    認証済みトークンの有効性を確認し、現在のユーザー情報を取得します。
    """
    return {
        "access_token": current_user.token,
        "username": current_user.id,
        "token_type": "Bearer",
        "is_admin": current_user.is_admin
    }
