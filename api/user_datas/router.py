from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session, aliased, exc, query, selectinload
from sqlalchemy import func, select, join, table, literal_column, text
from sqlalchemy import or_, and_

from .schemas import *

from mixins.database import get_db
from mixins.log import setup_logger
from mixins.purser import book_result_mapper, get_model_dict
from users.router import get_current_user
from users.schemas import UserCurrent

from datetime import datetime

app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)

@app.put("/api/books/user-data", tags=["User data"])
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

@app.patch("/api/books/user-data", tags=["User data"])
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
        if model.status == "open":
            metadata_model.open_page = 0
            metadata_model.last_open_date = datetime.now()
            if metadata_model.read_times == None:
                metadata_model.read_times = 0
            metadata_model.read_times += 1
        elif model.status == "pause":
            metadata_model.open_page = model.page
            metadata_model.last_open_date = datetime.now()
        elif model.status == "close" :
            metadata_model.open_page = None
            metadata_model.last_open_date = datetime.now()
        resulet_data.append(get_model_dict(metadata_model))
        db.merge(metadata_model)
    db.commit()
    return resulet_data

