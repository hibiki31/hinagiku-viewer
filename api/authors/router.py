from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from books.models import AuthorModel, BookModel, books_to_authors
from mixins.database import get_db
from mixins.log import setup_logger
from users.router import get_current_user
from users.schemas import UserCurrent

from .schemas import *

app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/authors", tags=["Author"], response_model=List[AuthorGet])
async def list_authors(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
        params: AuthorSearchParams = Depends()
    ):
    """
    著者一覧を取得する

    - name: 完全一致検索
    - name_like: 部分一致検索
    - is_favorite: お気に入りフィルタ（True/False/None）
    """
    # 書籍数をサブクエリで集計
    book_count_subquery = db.query(
        books_to_authors.c.author_id,
        func.count(books_to_authors.c.book_uuid).label('book_count')
    ).group_by(books_to_authors.c.author_id).subquery()

    query = db.query(
        AuthorModel.id,
        AuthorModel.name,
        AuthorModel.is_favorite,
        AuthorModel.description,
        func.coalesce(book_count_subquery.c.book_count, 0).label('book_count')
    ).outerjoin(
        book_count_subquery,
        AuthorModel.id == book_count_subquery.c.author_id
    )

    # フィルタ適用
    if params.name is not None:
        query = query.filter(AuthorModel.name == params.name)

    if params.name_like is not None:
        query = query.filter(AuthorModel.name.like(f'%{params.name_like}%'))

    if params.is_favorite is not None:
        query = query.filter(AuthorModel.is_favorite == params.is_favorite)

    return query.all()


@app.get("/api/authors/{author_id}", tags=["Author"], response_model=AuthorDetail)
async def get_author(
        author_id: int,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    著者の詳細情報を取得する

    - author_id: 著者ID
    """
    # 書籍数を集計
    book_count = db.query(func.count(books_to_authors.c.book_uuid)).filter(
        books_to_authors.c.author_id == author_id
    ).scalar()

    author = db.query(AuthorModel).filter(AuthorModel.id == author_id).one_or_none()

    if author is None:
        raise HTTPException(
            status_code=404,
            detail="指定された著者は存在しません"
        )

    return {
        "id": author.id,
        "name": author.name,
        "is_favorite": author.is_favorite,
        "description": author.description,
        "book_count": book_count or 0
    }


@app.post("/api/books/{book_uuid}/authors", tags=["Author"])
def add_book_author(
        request_model: BookAuthorPost,
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    書籍に著者を追加する

    - author_id: 既存の著者IDを指定
    - author_name: 著者名を指定（存在しない場合は新規作成）
    """
    book_model: BookModel = db.query(BookModel).filter(BookModel.uuid == book_uuid).one_or_none()

    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません,操作は全て取り消されました: {book_uuid}"
        )

    if request_model.author_id is not None:
        author_model = db.query(AuthorModel).filter(AuthorModel.id == request_model.author_id).one_or_none()
        if author_model:
            book_model.authors.append(author_model)
            logger.info(f"書籍に著者を追加: book={book_uuid}, author_id={request_model.author_id}, user={current_user.id}")
        else:
            raise HTTPException(
                status_code=404,
                detail=f"著者が存在しません,操作は全て取り消されました: {request_model.author_id}"
            )

    elif request_model.author_name is not None:
        author_model = db.query(AuthorModel).filter(AuthorModel.name == request_model.author_name).one_or_none()
        if author_model:
            book_model.authors.append(author_model)
            logger.info(f"書籍に既存著者を追加: book={book_uuid}, author={request_model.author_name}, user={current_user.id}")
        else:
            author_model = AuthorModel(name=request_model.author_name)
            book_model.authors.append(author_model)
            logger.info(f"書籍に新規著者を追加: book={book_uuid}, author={request_model.author_name}, user={current_user.id}")

    db.commit()

    return db.query(BookModel).filter(BookModel.uuid == book_uuid).one_or_none()


@app.delete("/api/books/{book_uuid}/authors", tags=["Author"])
def remove_book_author(
        request_model: BookAuthorDelete,
        book_uuid: str,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    書籍から著者を削除する

    - author_id: 削除する著者ID
    """
    book_model: BookModel = db.query(BookModel).filter(BookModel.uuid == book_uuid).one_or_none()

    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail="指定された本は存在しません"
        )

    author_model = db.query(AuthorModel).filter(AuthorModel.id == request_model.author_id).one_or_none()

    if author_model is None:
        raise HTTPException(
            status_code=404,
            detail="指定された著者は存在しません"
        )

    if author_model not in book_model.authors:
        raise HTTPException(
            status_code=404,
            detail="指定された本に指定された著者は登録されていません"
        )

    book_model.authors.remove(author_model)
    logger.info(f"書籍から著者を削除: book={book_uuid}, author_id={request_model.author_id}, user={current_user.id}")

    db.commit()

    return db.query(BookModel).filter(BookModel.uuid == book_uuid).one_or_none()


@app.patch("/api/authors/{author_id}", tags=["Author"], response_model=AuthorDetail)
def update_author_by_id(
        author_id: int,
        request_model: AuthorUpdate,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    著者情報を更新する

    - name: 著者名
    - is_favorite: お気に入り設定
    - description: 説明
    """
    author_model = db.query(AuthorModel).filter(AuthorModel.id == author_id).one_or_none()

    if author_model is None:
        raise HTTPException(
            status_code=404,
            detail="指定された著者は存在しません"
        )

    # 更新処理
    if request_model.name is not None:
        # 名前の重複チェック
        existing = db.query(AuthorModel).filter(
            AuthorModel.name == request_model.name,
            AuthorModel.id != author_id
        ).one_or_none()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="指定された著者名は既に存在します"
            )
        author_model.name = request_model.name
        logger.info(f"著者名を更新: author_id={author_id}, new_name={request_model.name}, user={current_user.id}")

    if request_model.is_favorite is not None:
        author_model.is_favorite = request_model.is_favorite
        logger.info(f"著者お気に入りを更新: author_id={author_id}, is_favorite={request_model.is_favorite}, user={current_user.id}")

    if request_model.description is not None:
        author_model.description = request_model.description

    db.commit()

    # 書籍数を集計
    book_count = db.query(func.count(books_to_authors.c.book_uuid)).filter(
        books_to_authors.c.author_id == author_id
    ).scalar()

    return {
        "id": author_model.id,
        "name": author_model.name,
        "is_favorite": author_model.is_favorite,
        "description": author_model.description,
        "book_count": book_count or 0
    }


@app.patch("/api/authors", tags=["Author"], deprecated=True)
def update_author(
        request_model: PatchAuthor,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    著者情報を更新する（旧形式・非推奨）

    このエンドポイントは後方互換性のために残されています。
    新規実装では PATCH /api/authors/{author_id} を使用してください。
    """
    author_model = db.query(AuthorModel).filter(AuthorModel.id == request_model.author_id).one_or_none()

    if author_model is None:
        raise HTTPException(
            status_code=404,
            detail="指定された著者は存在しません"
        )

    author_model.is_favorite = request_model.is_favorite
    logger.info(f"著者お気に入りを更新（旧API）: author_id={request_model.author_id}, is_favorite={request_model.is_favorite}, user={current_user.id}")

    db.commit()

    return author_model


@app.delete("/api/authors/{author_id}", tags=["Author"])
def delete_author(
        author_id: int,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    著者を削除する

    書籍に紐づいている著者は削除できません。
    """
    author_model = db.query(AuthorModel).filter(AuthorModel.id == author_id).one_or_none()

    if author_model is None:
        raise HTTPException(
            status_code=404,
            detail="指定された著者は存在しません"
        )

    # 書籍との紐づきをチェック
    book_count = db.query(func.count(books_to_authors.c.book_uuid)).filter(
        books_to_authors.c.author_id == author_id
    ).scalar()

    if book_count and book_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"この著者は{book_count}冊の書籍に紐づいているため削除できません"
        )

    logger.info(f"著者を削除: author_id={author_id}, name={author_model.name}, user={current_user.id}")

    db.delete(author_model)
    db.commit()

    return {"message": "著者を削除しました", "author_id": author_id}
