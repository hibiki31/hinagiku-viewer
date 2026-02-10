
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
        params: BookSearchParams = Depends()
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
    if params.uuid is not None:
        query = query.filter(BookModel.uuid==params.uuid)
    else:
        query = query.filter(BookModel.library_id == params.library_id)
        if params.title_like is not None:
            query = query.filter(BookModel.title.like(f'%{params.title_like}%'))

        if params.rate is not None:
            if params.rate == 0:
                query = query.filter(user_data.rate is None)
            else:
                query = query.filter(user_data.rate == params.rate)

        if params.genre_id is not None:
            query = query.filter(BookModel.genre_id == params.genre_id)

        if params.author_like is not None:
            query = query.outerjoin(BookModel.authors).filter(
                AuthorModel.name.like(f'%{params.author_like}%')
            )

        if params.author_is_favorite is not None:
            query = query.outerjoin(BookModel.authors).filter(
                AuthorModel.is_favorite == params.author_is_favorite
            )

        if params.cached is not None:
            query = query.filter(BookModel.cached == params.cached)

        elif params.full_text is not None:
            query = query.outerjoin(
                BookModel.authors
            ).filter(or_(
                BookModel.title.like(f'%{params.full_text}%'),
                BookModel.import_file_name.like(f'%{params.full_text}%'),
                AuthorModel.name.like(f'%{params.full_text}%')
            )).union(
                base_query.filter(BookModel.tags.any(name=params.tag))
            )

        if params.file_name_like is not None:
            query = query.filter(BookModel.import_file_name.like(f'%{params.file_name_like}%'))

        if params.tag is not None:
            query = query.filter(BookModel.tags.any(name=params.tag))


    if params.sort_key == "title" and not params.sort_desc:
        query = query.order_by(BookModel.title)
    elif params.sort_key == "title" and params.sort_desc:
        query = query.order_by(BookModel.title.desc())

    elif params.sort_key == "addDate" and not params.sort_desc:
        query = query.order_by(BookModel.add_date.desc())
    elif params.sort_key == "addDate" and params.sort_desc:
        query = query.order_by(BookModel.add_date)

    elif params.sort_key == "size" and not params.sort_desc:
        query = query.order_by(BookModel.size.desc())
    elif params.sort_key == "size" and params.sort_desc:
        query = query.order_by(BookModel.size)

    elif params.sort_key == "userData.lastOpenDate" and not params.sort_desc:
        query = query.order_by(user_data.last_open_date.desc())
    elif params.sort_key == "userData.lastOpenDate" and params.sort_desc:
        query = query.order_by(user_data.last_open_date)

    elif params.sort_key == "authors" and not params.sort_desc:
        query = query.outerjoin(
            BookModel.authors
        ).order_by(AuthorModel.name, BookModel.title)
    elif params.sort_key == "authors" and params.sort_desc:
        query = query.outerjoin(
            BookModel.authors
        ).order_by(AuthorModel.name.desc(), BookModel.title)

    count = query.count()

    if params.limit != 0:
        query = query.limit(params.limit).offset(params.offset)

    rows = query.all()
    rows = book_result_mapper(rows)

    # print(query.statement.compile())

    return {"count": count, "limit": params.limit, "offset": params.offset, "rows": rows}



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
