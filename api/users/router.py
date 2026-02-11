from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth.router import get_current_user
from auth.schemas import UserCurrent, UserPost
from mixins.database import get_db
from mixins.log import setup_logger
from users.models import UserModel
from users.schemas import UserGet

logger = setup_logger(__name__)
app = APIRouter(prefix="/api", tags=["User"])


# パスワードハッシュ化の設定
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


@app.get("/users", summary="ユーザー一覧取得", response_model=List[UserGet])
def list_users(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    ユーザー一覧を取得する

    管理者権限が必要です。
    """
    return db.query(UserModel).all()


@app.get("/users/me/", summary="現在のユーザー情報取得", response_model=UserGet)
def get_current_user_info(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    現在ログイン中のユーザー情報を取得する

    認証トークンから自身のユーザー情報を取得します。
    """
    user = db.query(UserModel).filter(UserModel.id == current_user.id).one()
    return user


@app.post("/users", summary="ユーザー作成", response_model=UserGet)
def create_user(
        user: UserPost,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    新規ユーザーを作成する

    管理者権限が必要です。
    作成されたユーザーは非管理者として登録されます。

    Args:
        user: ユーザー情報（ID、パスワード）

    Returns:
        作成されたユーザー情報

    Raises:
        400: ユーザーIDが既に存在する場合
    """
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

    created_user = db.query(UserModel).filter(UserModel.id == user.id).one()
    return created_user
