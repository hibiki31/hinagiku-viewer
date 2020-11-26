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
        db: Session = Depends(get_db)
    ):

    return db.query(BookModel).all()


@app.put("/api/books", tags=["book"])
async def put_api_books(
        db: Session = Depends(get_db),
        model: BookSelect = None
    ):
    # タスクを追加
    book: BookModel = db.query(BookModel).filter(BookModel.uuid==model.uuid).one()
    book.state = "request"
    db.commit()
    return book