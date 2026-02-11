
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, aliased

from books.schemas import BookDeleteResponse, BookUpdateResponse
from mixins.database import get_db
from mixins.log import setup_logger
from mixins.parser import book_result_mapper
from settings import DATA_ROOT
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
    """
    ライブラリ一覧を取得する

    各ライブラリに含まれる書籍数とともにライブラリ情報を取得します。
    """
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
    """
    書籍を検索する

    様々な条件で書籍を検索し、ページネーション形式で結果を返します。
    管理者は全ての書籍を、一般ユーザーは自分の書籍と共有された書籍のみを検索できます。

    検索条件:
    - uuid: 書籍UUID（完全一致）
    - fileNameLike: ファイル名（部分一致）
    - cached: キャッシュ済みか
    - authorLike: 著者名（部分一致）
    - authorIsFavorite: お気に入り著者フィルタ
    - titleLike: タイトル（部分一致）
    - fullText: 全文検索（タイトル、ファイル名、著者名、タグ名）
    - rate: 評価（0は未評価）
    - tag: タグ名（完全一致）
    - sortKey: ソートキー（title, addDate, size, userData.lastOpenDate, authors）
    - sortDesc: 降順ソート
    """
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

        if params.state is not None:
            query = query.filter(BookModel.state == params.state)

        elif params.full_text is not None:
            query = query.outerjoin(
                BookModel.authors
            ).outerjoin(
                BookModel.tags
            ).filter(or_(
                BookModel.title.ilike(f'%{params.full_text}%'),
                BookModel.import_file_name.ilike(f'%{params.full_text}%'),
                AuthorModel.name.ilike(f'%{params.full_text}%'),
                TagsModel.name.ilike(f'%{params.full_text}%')
            )).distinct()

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



@app.put("/api/books", tags=["Book"], response_model=BookUpdateResponse)
def update_books(
        db: Session = Depends(get_db),
        model: BookPut = None,
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    書籍情報を一括更新する

    指定されたUUID一覧の書籍に対して、同じ変更を適用します。

    更新可能な項目:
    - title: タイトル
    - series: シリーズ名
    - seriesNo: シリーズ番号
    - publisher: 出版社名
    - genre: ジャンル
    - libraryId: ライブラリID

    Raises:
        404: 指定された書籍が存在しない場合
    """
    updated_count = 0
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

        updated_count += 1

    db.commit()
    logger.info(f"書籍更新: {updated_count}件, user={current_user.id}")
    return BookUpdateResponse(message=f"{updated_count}件の書籍を更新しました", updated_count=updated_count)

@app.delete("/api/books/{book_uuid}", tags=["Book"], response_model=BookDeleteResponse)
def delete_book(
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
    ):
    """
    書籍を削除する

    指定された書籍を完全に削除します。
    書籍ファイル、ユーザーデータ、データベースレコードが全て削除されます。

    Args:
        book_uuid: 削除する書籍のUUID

    Raises:
        404: 指定された書籍が存在しない場合
    """
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
    logger.info(f"書籍削除: {book_uuid}, user={current_user.id}")
    return BookDeleteResponse(message="書籍を削除しました", uuid=book_uuid)


@app.get("/api/books/{book_uuid}/download", tags=["Book"], summary="本のZipファイルダウンロード")
def download_book(
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
    ):
    """指定された本のZipファイルをダウンロードする"""
    try:
        book: BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません: {book_uuid}",
        ) from None

    # 権限チェック: 管理者、自分の本、または共有されている本のみアクセス可能
    if not current_user.is_admin and book.user_id != current_user.id and not book.is_shared:
        raise HTTPException(
            status_code=403,
            detail="この本にアクセスする権限がありません",
        )

    # Zipファイルのパスを構築
    file_path = Path(f"{DATA_ROOT}/book_library/{book_uuid}.zip")

    # ファイルの存在確認
    if not file_path.exists():
        logger.error(f"Zipファイルが見つかりません: {file_path}")
        raise HTTPException(
            status_code=404,
            detail="ファイルが見つかりません",
        )

    # ダウンロード時のファイル名を設定（元のファイル名を使用）
    download_filename = book.import_file_name if book.import_file_name.endswith('.zip') else f"{book.import_file_name}.zip"

    logger.info(f"書籍ダウンロード: {book_uuid} ({download_filename}) by {current_user.id}")

    # RFC 5987に準拠したUTF-8エンコードファイル名（日本語対応）
    encoded_filename = quote(download_filename, safe='')

    return FileResponse(
        path=str(file_path),
        media_type="application/zip",
        filename=download_filename,
        headers={
            "Content-Disposition": f"attachment; filename=\"{download_filename.encode('ascii', 'ignore').decode('ascii') or 'download.zip'}\"; filename*=UTF-8''{encoded_filename}"
        }
    )
