from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session, aliased, exc, selectinload
from sqlalchemy import func
from sqlalchemy import or_, and_

from .models import *
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

@app.get("/api/library", tags=["library"])
async def get_api_library(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    query = db.query(
        func.count(BookModel.uuid).label("count"),
        LibraryModel.name.label("name"),
        LibraryModel.id.label("id")
    ).outerjoin(LibraryModel).group_by(
        LibraryModel.name
    )
    
    return query.all()


#, response_model=BookGet
@app.get("/api/books", tags=["book"])
async def get_api_books(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
        uuid: str = None,
        authorLike: str = None,
        titleLike: str = None,
        rate: int = None,
        series: str = None,
        state: str = None,
        genre: str = None,
        library: int = None,
        fileNameLike: str = None,
        limit:int = 50,
        offset:int = 0,
        tag: str = None,
        sortKey:str = "author-title",
    ):

    user_metadata_subquery = db.query(
        BookUserMetaDataModel
    ).filter(
        BookUserMetaDataModel.user_id==current_user.id
    ).subquery()

    user_data = aliased(BookUserMetaDataModel, user_metadata_subquery)

    query = db.query(
            BookModel,
            user_data,
        ).outerjoin(
        user_data,
        BookModel.uuid==user_data.book_uuid
    )

    if not current_user.is_admin:
        query = query.filter(
            or_(
                BookModel.is_shered==True,
                BookModel.user_id==current_user.id,
            )
        )

    if uuid != None:
        query = query.filter(BookModel.uuid==uuid)

    if authorLike != None:
        query = query.filter(BookModel.author_id.like(f'%{authorLike}%'))
    
    if titleLike != None:
        query = query.filter(BookModel.title.like(f'%{titleLike}%'))
    
    if rate != None:
        if rate == 0:
            query = query.filter(or_(BookModel.rate == 0, BookModel.rate == None))
        else:
            query = query.filter(BookModel.rate == rate)

    if genre != None:
        query = query.filter(BookModel.genre_id == genre)
    
    if library != None:
        query = query.filter(BookModel.library_id == library)
    
    if fileNameLike != None:
        query = query.filter(BookModel.import_file_name.like(f'%{fileNameLike}%'))
    
    if tag != None:
        query = query.filter(BookModel.tags.any(name=tag))

    if sortKey == "file":
        query = query.order_by(BookModel.import_file_name)
    elif sortKey == "author":
        query = query.order_by(BookModel.title)
    elif sortKey == "title":
        query = query.order_by(BookModel.title)
    elif sortKey == "date":
        query = query.order_by(BookModel.add_date.desc())
    elif sortKey == "author-title":
        query = query.order_by(BookModel.title)
    
    count = query.count()

    query = query.limit(limit).offset(offset)

    rows = query.all()
    rows = book_result_mapper(rows)

    # print(query.statement.compile())

    return {"count": count, "limit": limit, "offset": offset, "rows": rows}


@app.get("/api/authors", tags=["author"])
def read_api_authors(
        db: Session = Depends(get_db)
    ):
    row = db.query(AuthorModel).all()
    return row



@app.put("/api/books", tags=["book"])
def change_book_data(
        db: Session = Depends(get_db),
        model: BookPut = None
    ):
    for book_uuid in model.uuids:
        try:
            book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
        except:
            raise HTTPException(
                status_code=404,
                detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
            )

        if model.library != None:
            book.library = model.library

        if model.publisher != None:
            book.publisher = model.publisher
        
        if model.series != None:
            book.series = model.series

        if model.series_no != None:
            book.series_no = model.series_no

        if model.author != None:
            book.author = model.author

        if model.title != None:
            book.title = model.title
        
        if model.genre != None:
            book.genre = model.genre
    
    db.commit()
    return book

@app.put("/api/books/user-data", tags=["book"])
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

@app.patch("/api/books/user-data", tags=["book"])
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

@app.post("/api/books/tag", tags=["book"])
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
            )
        try:
            tags_model: TagsModel = db.query(TagsModel).filter(TagsModel.name==model.name).one()
        except exc.NoResultFound:
            tags_model = TagsModel(name=model.name)
        book.tags.append(tags_model)

        
        result_data.append(get_model_dict(book))
        db.merge(book)
    db.commit()
    return result_data

@app.delete("/api/books/tag", tags=["book"])
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
            )
        try:
            tags_model: TagsModel = db.query(TagsModel).filter(TagsModel.name==model.name).one()
        except exc.NoResultFound:
            pass
        book.tags.remove(tags_model)
        
        result_data.append(get_model_dict(book))
        db.merge(book)
    db.commit()
    return result_data

@app.get("/api/books/tag", tags=["book"])
def show_tag(
    db: Session = Depends(get_db),
    current_user: UserCurrent = Depends(get_current_user)
    ):
    tags = db.query(TagsModel).filter(TagsModel.books.any(user_id=current_user.id)).all()
    return tags