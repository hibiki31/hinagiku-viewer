import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, aliased

from auth.router import get_current_user
from auth.schemas import UserCurrent
from books.models import BookModel, BookUserMetaDataModel, DuplicateExclusionModel, DuplicationModel
from books.schemas import (
    BookCacheCreate,
    BookCacheCreateResponse,
    BookCacheSize,
    DuplicateExclusionCreate,
    DuplicateExclusionResponse,
    DuplicateListResponse,
    LibraryPatch,
)
from mixins.convertor import create_book_page_cache, image_convertor
from mixins.database import get_db
from mixins.log import setup_logger
from settings import APP_ROOT, CONVERT_THREAD, DATA_ROOT
from tasks.utility import create_task

app = APIRouter(
    prefix="/media",
    tags=["Media"]
)
logger = setup_logger(__name__)

# UUIDの正規表現パターン（パストラバーサル対策）
UUID_PATTERN = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')

# 画像高さの制限値
MIN_HEIGHT = 100
MAX_HEIGHT = 4320

# キャッシュ済み画像のHTTPキャッシュ期間（秒）: 7日
CACHE_MAX_AGE = 604800

converter_pool = []
library_pool = []


def _validate_uuid(uuid: str) -> None:
    """UUIDの形式を検証（パストラバーサル対策）"""
    if not UUID_PATTERN.match(uuid):
        raise HTTPException(status_code=400, detail="不正なUUID形式です")


@app.get("/books/cache", response_model=BookCacheSize, summary="キャッシュサイズ確認")
def get_media_books_cache(
        current_user:UserCurrent = Depends(get_current_user)
    ):

    original_size = 0
    convert_size = 0

    for file_path in Path(f"{DATA_ROOT}/book_cache").rglob("*"):
        if file_path.is_file():
            if re.fullmatch(r"^original_.*", file_path.name):
                original_size += file_path.stat().st_size
            else:
                convert_size += file_path.stat().st_size

    return {"original_mb": original_size/1024/1024, "convert_mb": convert_size/1024/1024}


@app.get("/books/duplicate", response_model=DuplicateListResponse, summary="重複書籍確認")
def get_media_books_duplicate(
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
        limit: int = 25,
        offset: int = 0,
    ):
    """
    重複書籍の一覧を返す。

    `duplicate_exclusion` テーブルに登録された除外ペアは結果から除外される。
    除外はペアの順序（uuid_1 < uuid_2）に関わらず両方向でチェックする。
    """
    book_model_1 = aliased(BookModel)
    book1_userdata = aliased(BookUserMetaDataModel)
    book_model_2 = aliased(BookModel)
    book2_userdata = aliased(BookUserMetaDataModel)

    # 除外ペアに該当するレコードをサブクエリで除外（両方向チェック）
    exclusion_exists = db.query(DuplicateExclusionModel).filter(
        or_(
            and_(
                DuplicateExclusionModel.book_uuid_1 == DuplicationModel.book_uuid_1,
                DuplicateExclusionModel.book_uuid_2 == DuplicationModel.book_uuid_2,
            ),
            and_(
                DuplicateExclusionModel.book_uuid_1 == DuplicationModel.book_uuid_2,
                DuplicateExclusionModel.book_uuid_2 == DuplicationModel.book_uuid_1,
            ),
        )
    ).exists()

    # duplication_idでソートして順序を固定する
    duplication_books = db.query(
        DuplicationModel.duplication_id,
        DuplicationModel.score,
        book_model_1.uuid,
        book_model_2.uuid,
        book_model_1.size,
        book_model_2.size,
        book_model_1.page,
        book_model_2.page,
        book_model_1.import_file_name,
        book_model_2.import_file_name,
        book1_userdata.rate,
        book2_userdata.rate,
    ).outerjoin(
        book_model_1, book_model_1.uuid == DuplicationModel.book_uuid_1
    ).outerjoin(
        book_model_2, book_model_2.uuid == DuplicationModel.book_uuid_2
    ).outerjoin(
        book1_userdata, book_model_1.uuid == book1_userdata.book_uuid
    ).outerjoin(
        book2_userdata, book_model_2.uuid == book2_userdata.book_uuid
    ).filter(
        ~exclusion_exists  # 除外ペアを除く
    ).order_by(DuplicationModel.duplication_id)

    res = {}

    for (duplication_id, score, book1_uuid, book2_uuid, book1_size, book2_size, book1_page, book2_page, book1_file, book2_file, book1_rate, book2_rate) in duplication_books.all():
        if duplication_id in res:
            duplication_uuids = [x["uuid"] for x in res[duplication_id]]
            if book1_uuid not in duplication_uuids:
                res[duplication_id].append({"uuid": book1_uuid, "file": book1_file, "size": book1_size, "page": book1_page, "rate": book1_rate, "score": score})
            if book2_uuid not in duplication_uuids:
                res[duplication_id].append({"uuid": book2_uuid, "file": book2_file, "size": book2_size, "page": book2_page, "rate": book2_rate, "score": score})
        else:
            res[duplication_id] = []
            res[duplication_id].append({"uuid": book1_uuid, "file": book1_file, "size": book1_size, "page": book1_page, "rate": book1_rate, "score": score})
            res[duplication_id].append({"uuid": book2_uuid, "file": book2_file, "size": book2_size, "page": book2_page, "rate": book2_rate, "score": score})

    res_list = []
    for key, value in res.items():
        res_list.append({
            "duplicate_uuid": key,
            "books": value
        })

    total = len(res_list)

    return {
        "count": total,
        "page_size": limit,
        "offset": offset,
        "items": res_list[offset:offset + limit],
    }


@app.post("/books/duplicate/exclude", response_model=DuplicateExclusionResponse, summary="重複除外ペア登録")
def post_media_books_duplicate_exclude(
        model: DuplicateExclusionCreate,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
    ):
    """
    AとBは重複でないと判断したペアを除外リストに登録する。

    登録されたペアは `GET /media/books/duplicate` の結果から除外される。
    UUIDは辞書順で正規化（小さい方が uuid_1）して格納するため、
    (A, B) と (B, A) は同一ペアとして扱われる。

    既に登録済みの場合は何もせず正常応答を返す。
    """
    uuid_1, uuid_2 = sorted([model.book_uuid_1, model.book_uuid_2])

    # 既に登録済みか確認
    existing = db.query(DuplicateExclusionModel).filter(
        DuplicateExclusionModel.book_uuid_1 == uuid_1,
        DuplicateExclusionModel.book_uuid_2 == uuid_2,
    ).one_or_none()

    if existing is None:
        exclusion = DuplicateExclusionModel(
            book_uuid_1=uuid_1,
            book_uuid_2=uuid_2,
            created_at=datetime.now(timezone.utc),
        )
        db.add(exclusion)
        db.commit()
        logger.info(f"重複除外ペア登録: {uuid_1} <-> {uuid_2}, user={current_user.id}")

    return DuplicateExclusionResponse(
        message="除外ペアを登録しました" if existing is None else "既に登録済みです",
        book_uuid_1=uuid_1,
        book_uuid_2=uuid_2,
    )


@app.delete("/books/duplicate/exclude", response_model=DuplicateExclusionResponse, summary="重複除外ペア解除")
def delete_media_books_duplicate_exclude(
        model: DuplicateExclusionCreate,
        db: Session = Depends(get_db),
        current_user: UserCurrent = Depends(get_current_user),
    ):
    """
    除外リストからペアを解除する。

    解除後は `GET /media/books/duplicate` の結果に再び表示される。
    登録されていないペアを指定した場合は 404 を返す。
    """
    uuid_1, uuid_2 = sorted([model.book_uuid_1, model.book_uuid_2])

    existing = db.query(DuplicateExclusionModel).filter(
        DuplicateExclusionModel.book_uuid_1 == uuid_1,
        DuplicateExclusionModel.book_uuid_2 == uuid_2,
    ).one_or_none()

    if existing is None:
        raise HTTPException(status_code=404, detail="指定されたペアは除外リストに登録されていません")

    db.delete(existing)
    db.commit()
    logger.info(f"重複除外ペア解除: {uuid_1} <-> {uuid_2}, user={current_user.id}")

    return DuplicateExclusionResponse(
        message="除外ペアを解除しました",
        book_uuid_1=uuid_1,
        book_uuid_2=uuid_2,
    )



@app.get("/books/{uuid}", summary="サムネイル取得")
def get_media_books_uuid(
        uuid: str
    ):
    _validate_uuid(uuid)
    file_path = f"{DATA_ROOT}/book_thum/{uuid}.webp"
    if not Path(file_path).exists():
        raise HTTPException(
            status_code=404,
            detail="ファイルが存在しません",
        )
    return FileResponse(
        file_path,
        headers={"Cache-Control": f"public, max-age={CACHE_MAX_AGE}"},
    )


@app.get("/books/{uuid}/{page}", summary="ページ画像取得")
def media_books_uuid_page(
        uuid: str,
        page: int,
        height: int = Query(default=1080, ge=MIN_HEIGHT, le=MAX_HEIGHT,
                            description=f"画像の高さ（{MIN_HEIGHT}〜{MAX_HEIGHT}）"),
    ):
    _validate_uuid(uuid)
    if page < 1:
        raise HTTPException(status_code=400, detail="pageは1以上を指定してください")

    cache_file = f"{DATA_ROOT}/book_cache/{uuid}/{height}_{str(page).zfill(4)}.webp"
    original_pattern = f"original_{str(page).zfill(4)}*"

    if Path(cache_file).exists():
        logger.debug(f"完全キャッシュから読み込み {uuid} p.{page}")
    else:
        # Path.globでマッチするファイルを検索
        matched_files = list(Path(f"{DATA_ROOT}/book_cache/{uuid}").glob(original_pattern))
        if matched_files:
            logger.debug(f"部分キャッシュから読み込み {uuid} p.{page}")
            image_convertor(str(matched_files[0]), cache_file, to_height=height, quality=85)
        else:
            try:
                create_book_page_cache(uuid, page, height, 85)
            except FileNotFoundError:
                raise HTTPException(
                    status_code=404, detail="書籍のZIPファイルが見つかりません"
                ) from None

    if not Path(cache_file).exists():
        raise HTTPException(status_code=500, detail="キャッシュファイルの生成に失敗しました")

    return FileResponse(
        path=cache_file,
        headers={"Cache-Control": f"public, max-age={CACHE_MAX_AGE}"},
    )


@app.patch("/books", response_model=BookCacheCreateResponse, summary="書籍一括変換タスク実行")
def patch_media_books_(
        model: BookCacheCreate,
        current_user:UserCurrent = Depends(get_current_user)
    ):

    for i, w in enumerate(converter_pool):
        if w.poll() is not None:
            logger.debug(f"完了したプロセスをプールから削除 {w.args}")
            del converter_pool[i]

    # [:-CONVERT_THREAD]で4を超える要素を先頭から（古いプロセスから）切っていける
    for w in converter_pool[:-CONVERT_THREAD]:
        logger.warn(f"最大並行数：{CONVERT_THREAD}を超える{w.args[3]}を強制終了させました")
        w.terminate()

    converter_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "convert", model.uuid, str(model.height)]))
    return { "status": "ok", "uuid": model.uuid, "height": model.height }


@app.patch("/library", summary="ライブラリロード・エクスポート（非推奨）", deprecated=True)
def patch_media_library(
        model: LibraryPatch,
        db: Session = Depends(get_db),
        current_user:UserCurrent = Depends(get_current_user)
    ):
    """
    **[非推奨] このエンドポイントは非推奨です。代わりに POST /api/tasks を使用してください。**

    各種バックグラウンドタスクを開始する

    state:
    - load: ライブラリのロード
    - fixmetadata: メタデータの修正
    - export: ライブラリのエクスポート
    - export_uuid: UUID指定エクスポート
    - sim_all: 全体の類似度計算
    - rule: ルール適用
    - thumbnail_recreate: サムネイル再作成
    - integrity_check: 整合性チェック
    """
    logger.warning("DEPRECATED: /media/library PATCH is deprecated. Use POST /api/tasks instead.")

    for i in library_pool:
        if i.poll() is None:
            return { "status": "already", "deprecated": True }

    # タスクレコード作成
    task_id = str(uuid4())
    create_task(db=db, task_id=task_id, task_type=model.state, user_id=current_user.id)

    if model.state == "load":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "load", current_user.id, task_id]))
    elif model.state == "fixmetadata":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "fixmetadata", current_user.id, task_id]))
    elif model.state == "export":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "export", task_id]))
    elif model.state == "export_uuid":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "export_uuid", task_id]))
    elif model.state == "sim_all":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "sim", "all", task_id]))

    elif model.state == "rule":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "rule", task_id]))

    elif model.state == "thumbnail_recreate":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "thumbnail_recreate", task_id]))

    elif model.state == "integrity_check":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "integrity_check", task_id]))

    return { "status": "ok", "taskId": task_id, "deprecated": True }
