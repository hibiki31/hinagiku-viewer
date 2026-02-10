from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, exc

from mixins.database import get_db
from mixins.log import setup_logger
from mixins.purser import get_model_dict
from users.router import get_current_user
from users.schemas import UserCurrent

from .schemas import *

app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)

@app.put("/api/books/user-data", tags=["User data"], summary="本のユーザデータ（レート）を一括更新")
def change_user_data(
        db: Session = Depends(get_db),
        model: BookUserMetaDataPut = None,
        current_user: UserCurrent = Depends(get_current_user)
    ):
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
    db.commit()
    return metadata_model

@app.patch("/api/books/user-data",
    tags=["User data"],
    summary="開いているページ、読んだ回数の管理",
    description="""
- 本を開いたとき status=open, page=0
- 本を途中で閉じた時 status=pause, page=5
- 本を読み終わったとき status=close, page=None
"""
)
def signal_book_status(
        db: Session = Depends(get_db),
        model: BookUserMetaDataPatch = None,
        current_user: UserCurrent = Depends(get_current_user)
    ):
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

