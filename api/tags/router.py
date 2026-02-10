import contextlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, exc

from books.models import BookModel, TagsModel
from mixins.database import get_db
from mixins.log import setup_logger
from mixins.parser import get_model_dict
from tags.schemas import BookTagBase
from users.router import get_current_user
from users.schemas import UserCurrent

app = APIRouter()
logger = setup_logger(__name__)


@app.post("/api/books/tag", tags=["Tag"])
def append_tag(
        model: BookTagBase,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    result_data = []
    for book_uuid in model.uuids:
        try:
            book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
        except exc.NoResultFound:
            raise HTTPException(
                status_code=404,
                detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
            ) from None
        try:
            tags_model: TagsModel = db.query(TagsModel).filter(TagsModel.name==model.name).one()
        except exc.NoResultFound:
            tags_model = TagsModel(name=model.name)
        book.tags.append(tags_model)


        result_data.append(get_model_dict(book))
        db.merge(book)
    db.commit()
    return result_data

@app.delete("/api/books/tag", tags=["Tag"])
def delete_tag(
        model: BookTagBase,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    result_data = []
    for book_uuid in model.uuids:
        try:
            book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
        except exc.NoResultFound:
            raise HTTPException(
                status_code=404,
                detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
            ) from None
        with contextlib.suppress(exc.NoResultFound):
            tags_model: TagsModel = db.query(TagsModel).filter(TagsModel.name==model.name).one()
        book.tags.remove(tags_model)

        result_data.append(get_model_dict(book))
        db.merge(book)
    db.commit()
    return result_data

@app.get("/api/books/tag", tags=["Tag"])
def show_tag(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    query = db.query(TagsModel).filter(TagsModel.books.any(user_id=current_user.id))

    print(query.statement.compile())

    return query.all()
