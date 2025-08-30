from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session, aliased, exc, query, selectinload
from sqlalchemy import func, select, join, table, literal_column, text
from sqlalchemy import or_, and_

from .models import *
from .schemas import *

from mixins.database import get_db
from mixins.log import setup_logger
from mixins.purser import book_result_mapper, get_model_dict
from users.router import get_current_user
from users.schemas import UserCurrent
from tasks.library_delete import main as library_delete

from datetime import datetime

app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)


@app.get("/api/libraries", tags=["Library"], response_model=List[GetLibrary])
async def get_api_library(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    query = db.query(
        func.count(BookModel.uuid).label("count"),
        LibraryModel.name.label("name"),
        LibraryModel.id.label("id"),
        LibraryModel.user_id.label("user_id")
    ).outerjoin(LibraryModel).group_by(
        LibraryModel.name,
        LibraryModel.id.label("id")
    )
    
    return query.all()


@app.get("/api/books", tags=["Book"], response_model=BookGet)
async def get_api_books(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
        uuid: str = None,
        fileNameLike: str = None,
        chached: bool = None,
        authorLike: str = None,
        titleLike: str = None,
        fullText: str = None,
        rate: int = None,
        seriesId: str = None,
        genreId: str = None,
        libraryId: int = 1,
        tag: str = None,
        state: str = None,
        limit:int = 50,
        offset:int = 0,
        sortKey:str = "authors",
        sortDesc:bool = False
    ):

    # ユーザデータのサブクエリ
    user_metadata_subquery = db.query(
        BookUserMetaDataModel
    ).filter(
        BookUserMetaDataModel.user_id==current_user.id
    ).subquery()
    user_data = aliased(BookUserMetaDataModel, user_metadata_subquery)

    # ユーザデータ結合
    base_query = db.query(
            BookModel,
            user_data,
        ).outerjoin(
        user_data,
        BookModel.uuid==user_data.book_uuid
    )

    # 管理者はすべて表示
    # 管理者以外は自分ののみ
    # 共有は全員に表示
    if not current_user.is_admin:
        base_query = base_query.filter(
            or_(
                BookModel.is_shered==True,
                BookModel.user_id==current_user.id,
            )
        )
    
    query = base_query

    # フィルター
    if uuid != None:
        query = query.filter(BookModel.uuid==uuid)
    else:
        query = query.filter(BookModel.library_id == libraryId)
        if titleLike != None:
            query = query.filter(BookModel.title.like(f'%{titleLike}%'))
        
        if rate != None:
            if rate == 0:
                query = query.filter(user_data.rate == None)
            else:
                query = query.filter(user_data.rate == rate)
        
        if genreId != None:
            query = query.filter(BookModel.genre_id == genreId)
        
        if authorLike != None:
            query = query.outerjoin(BookModel.authors).filter(
                AuthorModel.name.like(f'%{authorLike}%')
            )
        
        if chached != None:
            query = query.filter(BookModel.chached == chached)
        
        elif fullText != None:
            query = query.outerjoin(
                BookModel.authors
            ).filter(or_(
                BookModel.title.like(f'%{fullText}%'),
                BookModel.import_file_name.like(f'%{fullText}%'),
                AuthorModel.name.like(f'%{fullText}%')
            )).union(
                base_query.filter(BookModel.tags.any(name=tag))
            )

        if fileNameLike != None:
            query = query.filter(BookModel.import_file_name.like(f'%{fileNameLike}%'))
        
        if tag != None:
            query = query.filter(BookModel.tags.any(name=tag))
        
        
    if sortKey == "title" and sortDesc == False:
        query = query.order_by(BookModel.title)
    elif sortKey == "title" and sortDesc == True:
        query = query.order_by(BookModel.title.desc())
    
    elif sortKey == "addDate" and sortDesc == False:
        query = query.order_by(BookModel.add_date.desc())
    elif sortKey == "addDate" and sortDesc == True:
        query = query.order_by(BookModel.add_date)
    
    elif sortKey == "size" and sortDesc == False:
        query = query.order_by(BookModel.size.desc())
    elif sortKey == "size" and sortDesc == True:
        query = query.order_by(BookModel.size)

    elif sortKey == "userData.lastOpenDate" and sortDesc == False:
        query = query.order_by(user_data.last_open_date.desc())
    elif sortKey == "userData.lastOpenDate" and sortDesc == True:
        query = query.order_by(user_data.last_open_date)
    
    elif sortKey == "authors" and sortDesc == False:
        query = query.outerjoin(
            BookModel.authors
        ).order_by(AuthorModel.name, BookModel.title)
    elif sortKey == "authors" and sortDesc == True:
        query = query.outerjoin(
            BookModel.authors
        ).order_by(AuthorModel.name.desc(), BookModel.title)
    
    count = query.count()

    if limit != 0:
        query = query.limit(limit).offset(offset)

    rows = query.all()
    rows = book_result_mapper(rows)

    # print(query.statement.compile())

    return {"count": count, "limit": limit, "offset": offset, "rows": rows}



@app.put("/api/books", tags=["Book"])
def change_book_data(
        db: Session = Depends(get_db),
        model: BookPut = None,
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

        if model.library_id != None:
            book.library_id = model.library_id

        if model.publisher != None:
            if publisher_model := db.query(PublisherModel).filter(PublisherModel.name==model.publisher).one_or_none():
                book.publisher_id = publisher_model.id
            else:
                publisher_model = PublisherModel(name=model.publisher)
                db.add(publisher_model)
                db.commit()
                book.publisher_id = publisher_model.id
        
        if model.series != None:
            book.series = model.series

        if model.series_no != None:
            book.series_no = model.series_no

        if model.title != None:
            book.title = model.title
        
        if model.genre != None:
            book.genre = model.genre
    
    db.commit()
    return book

@app.delete("/api/books/{book_uuid}", tags=["Book"])
def delete_book_data(
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
    ):
    try:
        book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
    except:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
        )
    
    library_delete(db=db, delete_uuid=book_uuid, file_name=book.import_file_name)
    db.query(BookUserMetaDataModel).filter(BookUserMetaDataModel.book_uuid==book_uuid).filter(BookUserMetaDataModel.user_id==current_user.id).delete()
    db.commit()
    db.delete(book)
    db.commit()
    return book
    