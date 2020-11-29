from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

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


@app.get("/api/books", tags=["book"],response_model=List[BookBase])
async def get_api_books(
        db: Session = Depends(get_db),
        uuid: str = None,
        author_like: str = None,
        title_like: str = None,
        rate: str = None,
        series: str = None,
        state: str = None,
        file_name_like: str = None
    ):

    query = db.query(BookModel)

    if uuid != None:
        query = query.filter(BookModel.uuid==uuid)

    if author_like != None:
        query = query.filter(BookModel.author.like(f'%{author_like}%'))
    
    if title_like != None:
        query = query.filter(BookModel.title.like(f'%{title_like}%'))
    
    if file_name_like != None:
        query = query.filter(BookModel.import_file_name.like(f'%{file_name_like}%'))

    return query.order_by(BookModel.import_file_name).all()


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