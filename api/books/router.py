from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session, aliased, exc
from sqlalchemy import func
from sqlalchemy import or_, and_

from .models import *
from .schemas import *

from mixins.database import get_db
from mixins.log import setup_logger

from users.router import get_current_user
from users.schemas import UserCurrent

app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)

@app.get("/api/library", tags=["library"])
async def get_api_library(
        db: Session = Depends(get_db),
    ):
    query = db.query(
        BookModel.library.label("library"), 
        func.count(BookModel.library).label("count")
    )

    query = query.group_by(BookModel.library)
    
    return query.all()

@app.get("/api/books", tags=["book"], response_model=BookGet)
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
        library: str = None,
        fileNameLike: str = None,
        limit:int = 50,
        offset:int = 0,
        sortKey:str = "author-title",
    ):

    user_metadata_subquery = aliased(
        BookUserMetaDataModel, 
        db.query(BookUserMetaDataModel).filter(BookUserMetaDataModel.user_id==current_user.id).subquery("user_metadata_subquery")
    )

    query = db.query(
        BookModel,
        BookModel.uuid,
        BookModel.user_id,
        BookModel.library,
        BookModel.import_file_name,
        BookModel.add_date,
        BookModel.file_date,
        BookModel.author,
        BookModel.genre,
        BookModel.page,
        BookModel.size,
        BookModel.title,
        BookModel.publisher,
        BookModel.is_shered,
        BookModel.tags.all,
        user_metadata_subquery.rate.label("user_rate"),
        user_metadata_subquery.last_open_date.label("user_last_open_date"),
        user_metadata_subquery.read_times.label("user_read_times"),
        user_metadata_subquery.open_page.label("user_open_page"),
    ).outerjoin(
    # query = db.query(BookModel).outerjoin(
        user_metadata_subquery,
        BookModel.uuid==user_metadata_subquery.book_uuid
    )
    from pprint import pprint

    pprint(dir(BookModel.tags))


    # query = db.query(BookModel)

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
        query = query.filter(BookModel.author.like(f'%{authorLike}%'))
    
    if titleLike != None:
        query = query.filter(BookModel.title.like(f'%{titleLike}%'))
    
    if rate != None:
        if rate == 0:
            query = query.filter(or_(BookModel.rate == 0, BookModel.rate == None))
        else:
            query = query.filter(BookModel.rate == rate)

    if genre != None:
        query = query.filter(BookModel.genre == genre)
    
    if library != None:
        query = query.filter(BookModel.library == library)
    
    if fileNameLike != None:
        query = query.filter(BookModel.import_file_name.like(f'%{fileNameLike}%'))

    if sortKey == "file":
        query = query.order_by(BookModel.import_file_name)
    elif sortKey == "author":
        query = query.order_by(BookModel.author)
    elif sortKey == "title":
        query = query.order_by(BookModel.title)
    elif sortKey == "date":
        query = query.order_by(BookModel.add_date.desc())
    elif sortKey == "author-title":
        query = query.order_by(BookModel.author, BookModel.title)
    
    count = query.count()

    query = query.limit(limit).offset(offset)

    rows = query.all()
    
    print(query.statement.compile())

    return {"count": count, "limit": limit, "offset": offset, "rows": rows}

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



@app.post("/api/books/tag", tags=["book"])
def change_user_data(
        model: BookTagBase,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    for book_uuid in model.uuids:
        try:
            book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
        except:
            raise HTTPException(
                status_code=404,
                detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
            )
        book.tags.append(TagModel(name=model.name))

        # try:
        #     tag_model: BookTagModel = db.query(BookTagModel).filter(
        #         BookTagModel.name==model.name
        #     ).one()
        # except exc.NoResultFound:
        #     tag_model = BookTagModel(
        #         name=model.name,

        #     )
        # db.merge(book)
    return db.commit()