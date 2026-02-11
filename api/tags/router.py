
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session, exc

from books.models import BookModel, TagsModel
from mixins.database import get_db
from mixins.log import setup_logger
from mixins.schema import MessageResponse
from tags.schemas import TagCreate, TagResponse
from users.router import get_current_user
from users.schemas import UserCurrent

app = APIRouter(prefix="/api", tags=["Tag"])
logger = setup_logger(__name__)


@app.post("/books/{uuid}/tags", summary="タグ追加", response_model=MessageResponse)
def add_book_tag(
        uuid: str = Path(..., description="書籍UUID"),
        model: TagCreate = None,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    指定した書籍にタグを追加する
    
    タグ名が既に存在する場合は既存のタグを使用し、
    存在しない場合は新規作成します。
    
    Raises:
        404: 書籍が存在しない、または所有していない場合
    """
    try:
        book: BookModel = db.query(BookModel).filter(
            BookModel.uuid == uuid,
            BookModel.user_id == current_user.id
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません: {uuid}",
        ) from None

    try:
        tags_model: TagsModel = db.query(TagsModel).filter(TagsModel.name == model.name).one()
    except exc.NoResultFound:
        tags_model = TagsModel(name=model.name)

    # 既に追加されていないかチェック
    if tags_model not in book.tags:
        book.tags.append(tags_model)

    db.merge(book)
    db.commit()
    db.refresh(book)

    logger.info(f"タグ追加: book={uuid}, tag={model.name}, user={current_user.id}")
    return MessageResponse(message=f"タグ '{model.name}' を追加しました")


@app.delete("/books/{uuid}/tags/{tag_id}", summary="タグ削除", response_model=MessageResponse)
def remove_book_tag(
        uuid: str = Path(..., description="書籍UUID"),
        tag_id: int = Path(..., description="タグID"),
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    指定した書籍から指定したタグを削除する
    
    Raises:
        404: 書籍、タグが存在しない、またはタグが関連付けられていない場合
    """
    try:
        book: BookModel = db.query(BookModel).filter(
            BookModel.uuid == uuid,
            BookModel.user_id == current_user.id
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません: {uuid}",
        ) from None

    try:
        tags_model: TagsModel = db.query(TagsModel).filter(TagsModel.id == tag_id).one()
        book.tags.remove(tags_model)
    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail=f"タグが存在しません: {tag_id}",
        ) from None
    except ValueError:
        # タグが書籍に関連付けられていない場合
        raise HTTPException(
            status_code=404,
            detail=f"書籍にタグが関連付けられていません: {tag_id}",
        ) from None

    db.merge(book)
    db.commit()
    db.refresh(book)

    logger.info(f"タグ削除: book={uuid}, tag_id={tag_id}, user={current_user.id}")
    return MessageResponse(message="タグを削除しました")


@app.get("/books/{uuid}/tags", summary="書籍のタグ一覧取得", response_model=List[TagResponse])
def get_book_tags(
        uuid: str = Path(..., description="書籍UUID"),
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    指定した書籍のタグ一覧を取得する
    
    Raises:
        404: 書籍が存在しない、または所有していない場合
    """
    try:
        book: BookModel = db.query(BookModel).filter(
            BookModel.uuid == uuid,
            BookModel.user_id == current_user.id
        ).one()
    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail=f"本が存在しません: {uuid}",
        ) from None

    return book.tags


@app.get("/tags", summary="タグ一覧取得", response_model=List[TagResponse])
def list_tags(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user)
    ):
    """
    タグ一覧を取得する
    
    ユーザーが所有する書籍に関連付けられているタグのみを返します。
    """
    query = db.query(TagsModel).filter(TagsModel.books.any(user_id=current_user.id))

    return query.all()
