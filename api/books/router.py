from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, aliased

from mixins.database import get_db
from mixins.log import setup_logger
from mixins.parser import book_result_mapper
from tasks.library_delete import main as library_delete
from users.router import get_current_user
from users.schemas import UserCurrent

from .models import *
from .schemas import *

app = APIRouter()
logger = setup_logger(__name__)


exception_notfund = HTTPException(
    status_code=404,
    detail="Object not fund."
)


@app.get("/api/libraries", tags=["Library"], response_model=List[GetLibrary])
async def list_libraries(
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
async def search_books(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
        uuid: Optional[str] = None,
        fileNameLike: Optional[str] = None,
        cached: Optional[bool] = None,
        authorLike: Optional[str] = None,
        titleLike: Optional[str] = None,
        fullText: Optional[str] = None,
        rate: Optional[int] = None,
        seriesId: Optional[str] = None,
        genreId: Optional[str] = None,
        libraryId: int = 1,
        tag: Optional[str] = None,
        state: Optional[str] = None,
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
                BookModel.is_shared,
                BookModel.user_id==current_user.id,
            )
        )

    query = base_query

    # フィルター
    if uuid is not None:
        query = query.filter(BookModel.uuid==uuid)
    else:
        query = query.filter(BookModel.library_id == libraryId)
        if titleLike is not None:
            query = query.filter(BookModel.title.like(f'%{titleLike}%'))

        if rate is not None:
            if rate == 0:
                query = query.filter(user_data.rate is None)
            else:
                query = query.filter(user_data.rate == rate)

        if genreId is not None:
            query = query.filter(BookModel.genre_id == genreId)

        if authorLike is not None:
            query = query.outerjoin(BookModel.authors).filter(
                AuthorModel.name.like(f'%{authorLike}%')
            )

        if cached is not None:
            query = query.filter(BookModel.cached == cached)

        elif fullText is not None:
            query = query.outerjoin(
                BookModel.authors
            ).filter(or_(
                BookModel.title.like(f'%{fullText}%'),
                BookModel.import_file_name.like(f'%{fullText}%'),
                AuthorModel.name.like(f'%{fullText}%')
            )).union(
                base_query.filter(BookModel.tags.any(name=tag))
            )

        if fileNameLike is not None:
            query = query.filter(BookModel.import_file_name.like(f'%{fileNameLike}%'))

        if tag is not None:
            query = query.filter(BookModel.tags.any(name=tag))


    if sortKey == "title" and not sortDesc:
        query = query.order_by(BookModel.title)
    elif sortKey == "title" and sortDesc:
        query = query.order_by(BookModel.title.desc())

    elif sortKey == "addDate" and not sortDesc:
        query = query.order_by(BookModel.add_date.desc())
    elif sortKey == "addDate" and sortDesc:
        query = query.order_by(BookModel.add_date)

    elif sortKey == "size" and not sortDesc:
        query = query.order_by(BookModel.size.desc())
    elif sortKey == "size" and sortDesc:
        query = query.order_by(BookModel.size)

    elif sortKey == "userData.lastOpenDate" and not sortDesc:
        query = query.order_by(user_data.last_open_date.desc())
    elif sortKey == "userData.lastOpenDate" and sortDesc:
        query = query.order_by(user_data.last_open_date)

    elif sortKey == "authors" and not sortDesc:
        query = query.outerjoin(
            BookModel.authors
        ).order_by(AuthorModel.name, BookModel.title)
    elif sortKey == "authors" and sortDesc:
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
def update_books(
        db: Session = Depends(get_db),
        model: BookPut = None,
        current_user: UserCurrent = Depends(get_current_user)
    ):
    for book_uuid in model.uuids:
        try:
            book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
            ) from None

        if model.library_id is not None:
            book.library_id = model.library_id

        if model.publisher is not None:
            if publisher_model := db.query(PublisherModel).filter(PublisherModel.name==model.publisher).one_or_none():
                book.publisher_id = publisher_model.id
            else:
                publisher_model = PublisherModel(name=model.publisher)
                db.add(publisher_model)
                db.commit()
                book.publisher_id = publisher_model.id

        if model.series is not None:
            book.series = model.series

        if model.series_number is not None:
            book.series_no = model.series_number

        if model.title is not None:
            book.title = model.title

        if model.genre is not None:
            book.genre = model.genre

    db.commit()
    return book

@app.delete("/api/books/{book_uuid}", tags=["Book"])
def delete_book(
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
    ):
    try:
        book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}",
        ) from None

    library_delete(db=db, delete_uuid=book_uuid, file_name=book.import_file_name)
    db.query(BookUserMetaDataModel).filter(BookUserMetaDataModel.book_uuid==book_uuid).filter(BookUserMetaDataModel.user_id==current_user.id).delete()
    db.commit()
    db.delete(book)
    db.commit()
    return book
