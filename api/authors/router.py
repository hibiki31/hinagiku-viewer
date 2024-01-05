from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .schemas import *

from mixins.database import get_db
from mixins.log import setup_logger
from users.router import get_current_user
from users.schemas import UserCurrent

from books.models import AuthorModel, BookModel

app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/authors", tags=["Author"], response_model=List[AuthorGet])
async def get_api_library(
        isFavorite: bool,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
        name: str = None,
        nameLike: str = None
    ):
    query = db.query(
        AuthorModel.name, 
        AuthorModel.id,
        AuthorModel.is_favorite
    )

    if name:
        query = query.filter(AuthorModel.name == name)
    if nameLike:
        query = query.filter(AuthorModel.name.like(f'%{nameLike}%'))
    if isFavorite != None and isFavorite == False:
        query = query.filter(AuthorModel.is_favorite == False)
    if isFavorite != None and isFavorite == True:
        query = query.filter(AuthorModel.is_favorite == True)
    return query.all()


@app.post("/api/books/{book_uuid}/authors", tags=["Author"])
def post_api_books_uuid_authors(
        request_model:BookAuthorPost,
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):

    book_model: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one_or_none()

    if book_model == None:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
        )
    
    if request_model.author_id != None:
        if author_model := db.query(AuthorModel).filter(AuthorModel.id==request_model.author_id).one_or_none():
            book_model.authors.append(author_model)
        else:
            raise HTTPException(
                status_code=404,
                detail=f"著者が存在しません,操作は全て取り消されました: {book_uuid}",
            )
    
    elif request_model.author_name != None:
        if author_model := db.query(AuthorModel).filter(AuthorModel.name==request_model.author_name).one_or_none():
            book_model.authors.append(author_model)
        else:
            author_model = AuthorModel(name=request_model.author_name)
            book_model.authors.append(author_model)
    
    db.commit()

    return db.query(BookModel).filter(BookModel.uuid==book_uuid).one_or_none()


@app.delete("/api/books/{book_uuid}/authors", tags=["Author"])
def delete_api_books_uuid_authors(
        request_model: BookAuthorDelete,
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):

    book_model: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one_or_none()

    if book_model == None:
        raise HTTPException(
            status_code=404,
            detail=f"指定された本は存在しません",
        )

    if author_model := db.query(AuthorModel).filter(AuthorModel.id==request_model.author_id).one_or_none():
        if author_model not in book_model.authors:
            raise HTTPException(
                status_code=404,
                detail=f"指定された本に指定された著者は登録されていません",
            )

        book_model.authors.remove(author_model)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"指定された著者は存在しません",
        )
    
    db.commit()

    return db.query(BookModel).filter(BookModel.uuid==book_uuid).one_or_none()


@app.patch("/api/authors", tags=["Author"])
def delete_api_books_uuid_authors(
        request_model: PatchAuthor,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):

    if author_model := db.query(AuthorModel).filter(AuthorModel.id==request_model.author_id).one_or_none():
        author_model.is_favorite = request_model.is_favorite
    else:
        raise HTTPException(
            status_code=404,
            detail=f"指定された著者は存在しません",
        )
    
    db.commit()

    return author_model
