from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import or_

from .models import *
from .schemas import *

from mixins.database import get_db
from mixins.log import setup_logger


app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)

@app.get("/api/library", tags=["book"])
async def get_api_library(
        db: Session = Depends(get_db),
    ):
    query = db.query(
        BookModel.library.label("library"), 
        func.count(BookModel.library).label("count")
    )

    query = query.group_by(BookModel.library)
    
    return query.all()


@app.get("/api/books", tags=["book"])
async def get_api_books(
        db: Session = Depends(get_db),
        uuid: str = None,
        author_like: str = None,
        title_like: str = None,
        rate: int = None,
        series: str = None,
        state: str = None,
        genre: str = None,
        library: str = None,
        file_name_like: str = None,
        limit:int = 50,
        offset:int = 0,
        sort_key:str = "file",
    ):

    query = db.query(BookModel)

    if uuid != None:
        query = query.filter(BookModel.uuid==uuid)

    if author_like != None:
        query = query.filter(BookModel.author.like(f'%{author_like}%'))
    
    if title_like != None:
        query = query.filter(BookModel.title.like(f'%{title_like}%'))
    
    if rate != None:
        if rate == 0:
            query = query.filter(or_(BookModel.rate == 0, BookModel.rate == None))
        else:
            query = query.filter(BookModel.rate == rate)

    if genre != None:
        query = query.filter(BookModel.genre == genre)
    
    if library != None:
        query = query.filter(BookModel.library == library)
    
    if file_name_like != None:
        query = query.filter(BookModel.import_file_name.like(f'%{file_name_like}%'))

    if sort_key == "file":
        query = query.order_by(BookModel.import_file_name)
    elif sort_key == "author":
        query = query.order_by(BookModel.author)
    elif sort_key == "title":
        query = query.order_by(BookModel.title)
    elif sort_key == "date":
        query = query.order_by(BookModel.add_date)
    
    count = query.count()

    query = query.limit(limit).offset(offset)

    rows = query.all()
    
    # print(query.statement.compile())

    return {"count": count, "limit": limit, "offset": offset, "rows": rows}

@app.put("/api/books", tags=["book"])
async def put_api_books(
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

        if model.rate != None:
            book.rate = model.rate
        
        if model.state != None:
            book.state = model.state
        
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