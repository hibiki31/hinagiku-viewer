from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, exc

from books.models import BookUserMetaDataModel
from mixins.database import get_db
from mixins.log import setup_logger
from mixins.parser import get_model_dict
from user_datas.schemas import UserDataUpdateResponse
from users.router import get_current_user
from users.schemas import UserCurrent

from .schemas import *

app = APIRouter(prefix="/api", tags=["User data"])
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)

@app.put("/books/user-data", summary="レート一括更新", response_model=UserDataUpdateResponse)
def change_user_data(
        db: Session = Depends(get_db),
        model: BookUserMetaDataPut = None,
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    書籍のユーザーデータ（レート）を一括更新する
    
    指定された書籍の評価を一括で設定します。
    
    Args:
        model: 更新する書籍UUIDリストと評価値
    
    Returns:
        更新結果
    """
    updated_count = 0
    for book_uuid in model.uuids:
        try:
            metadata_model: BookUserMetaDataModel = db.query(BookUserMetaDataModel).filter(
                and_(
                    BookUserMetaDataModel.book_uuid==book_uuid,
                    BookUserMetaDataModel.user_id==current_user.id
                )
            ).one()
            metadata_model.rate = model.rate
        except exc.NoResultFound:
            metadata_model = BookUserMetaDataModel(
                user_id = current_user.id,
                book_uuid = str(book_uuid),
                rate = model.rate,
            )
        db.merge(metadata_model)
        updated_count += 1
    db.commit()
    logger.info(f"ユーザーデータ更新: {updated_count}件, rate={model.rate}, user={current_user.id}")
    return UserDataUpdateResponse(message=f"{updated_count}件のレートを更新しました", updated_count=updated_count)

@app.patch("/books/user-data",
    summary="閲覧状態更新",
    description="""
- 本を開いたとき status=open, page=0
- 本を途中で閉じた時 status=pause, page=5
- 本を読み終わったとき status=close, page=None
""",
    response_model=List[BookUserDataBase]
)
def signal_book_status(
        db: Session = Depends(get_db),
        model: BookUserMetaDataPatch = None,
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    書籍の閲覧状態を更新する
    
    書籍を開いた時、閉じた時、読み終わった時の状態を記録します。
    
    Args:
        model: 書籍UUIDリスト、ページ番号、ステータス
    
    Returns:
        更新されたユーザーデータリスト
    
    Raises:
        400: ステータスが不正な場合
    """
    resulet_data = []
    for book_uuid in model.uuids:
        try:
            metadata_model: BookUserMetaDataModel = db.query(BookUserMetaDataModel).filter(
                and_(
                    BookUserMetaDataModel.book_uuid==book_uuid,
                    BookUserMetaDataModel.user_id==current_user.id
                )
            ).one()

        except exc.NoResultFound:
            metadata_model = BookUserMetaDataModel(
                user_id = current_user.id,
                book_uuid = str(book_uuid),
            )

        # 共通の処理
        metadata_model.last_open_date = datetime.now()

        # 本を開いたとき
        if model.status == "open":
            metadata_model.open_page = 0

        # 本を途中で閉じるとき
        elif model.status == "pause":
            metadata_model.open_page = model.page

        # 読み終わったとき、開いているページをNone、読んだ回数をインクリメント
        elif model.status == "close" :
            metadata_model.open_page = None
            if metadata_model.read_times is None:
                metadata_model.read_times = 0
            metadata_model.read_times += 1
        else:
            db.rollback()
            raise HTTPException(status_code=400, detail="Incorrect status specified")
        resulet_data.append(get_model_dict(metadata_model))
        db.merge(metadata_model)
    db.commit()
    return resulet_data

