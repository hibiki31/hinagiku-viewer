import sys
import uuid
from multiprocessing import Pipe, Pool, Process
from typing import Optional

import imagehash
from PIL import Image
from sqlalchemy import or_
from sqlalchemy.orm import Session

from books.models import BookModel, DuplicationModel
from mixins.log import setup_logger
from settings import CONVERT_THREAD, DATA_ROOT

logger = setup_logger(__name__)


def main(db: Session, mode, task_id: Optional[str] = None):
    ## multithreadでハッシュを取得する、取得済みは基本スキップ
    if mode == "all-force":
        books = db.query(BookModel.uuid).all()
    else:
        books = db.query(BookModel.uuid).filter(BookModel.ahash is None).all()

    logger.info(f"{len(books)}件のAhashを取得します")

    if len(books) <= 16:
        for book in books:
            ahash = str(imagehash.average_hash(Image.open(f'{DATA_ROOT}/book_thum/{book.uuid}.jpg'), hash_size=16))
            book.ahash = ahash
            logger.info(f"{book.uuid} : ahash {ahash}")
            db.commit()

    else:
        process_list = []
        result = []

        size = len(books)
        logger.info(f"{CONVERT_THREAD}のスレッドで{len(books)}件のAhashを取得します")
        for i in range(CONVERT_THREAD):
            start = int(size*i/CONVERT_THREAD)
            end = int(size*(i+1)/CONVERT_THREAD)
            logger.info(f"process[{i}]: {start}:{end}")
            get_rev,send_rev  = Pipe(False)
            process_list.append((
                Process(target=get_ahash_task, args=(send_rev, books[start:end],)),
                get_rev
            ))

        for i in process_list:
            i[0].start()
        for i in process_list:
            i[0].join()
            result.extend(i[1].recv())

        logger.info(f"{len(result)}件のAhashを取得しましたDBに書き込みます")
        for i in result:
            book = db.query(BookModel).filter(BookModel.uuid == i["uuid"]).one()
            book.ahash = i["ahash"]
        db.commit()
        logger.info("DBへの書き込み完了")

    ## DBのデータで突合開始
    db_ahash_check(db=db)


def db_ahash_check(db: Session):
    # 重複結果を削除
    db.query(DuplicationModel).delete()
    db.commit()
    check_delete = db.query(DuplicationModel).all()
    logger.info(check_delete)

    # 突合用UUIDとAHASHを取得
    book_list = [(str(book[0]), str(book[1])) for book in db.query(BookModel.uuid, BookModel.ahash).all()]
    book_list_size = len(book_list)

    # 処理開始
    logger.info(f"{CONVERT_THREAD}のスレッドで{book_list_size}件のハッシュ突合を行います 配列のメモリ使用量{round(sys.getsizeof(book_list)/1024,2)} kb")

    # 分割数を指定
    p = Pool(CONVERT_THREAD)
    n = 1000 # 1000件のデータを1プロセスに投げる

    map_values = [(book_list, i, i + n) for i in range(0, book_list_size, n)]
    result = p.map(process_check_ahash, map_values)
    flat_result = [x for row in result for x in row]

    logger.info(f"{book_list_size}件でハッシュ突合を終了")

    logger.info(f"{len(flat_result)}の重複内容をデータベースに保存中")
    for i in flat_result:
        duplicate_book_save(db=db, uuid_1=i[0], uuid_2=i[1], score=i[2])



def process_check_ahash(input):
    all_books = input[0]
    start_index = input[1]
    end_index = input[2]
    logger.info(f"{start_index}:{end_index}開始")

    duplicate_list = []
    for book_base_uuid, book_base_ahash in all_books[start_index:end_index]:
        for (book_comaier_uuid, book_comaier_ahash) in all_books:
            # 自身のUUIDはスキップ
            if book_base_uuid == book_comaier_uuid:
                continue

            # ビット演算で比較
            hash1 = int(book_base_ahash,16)
            hash2 = int(book_comaier_ahash,16)
            score = bin(hash1 ^ hash2).count('1')

            # 閾値
            if score < 10:
                logger.info(f"重複 {book_base_uuid}, {book_comaier_uuid}, {score}")
                duplicate_list.append(
                    (book_base_uuid, book_comaier_uuid, score)
                )

        logger.debug(f"{book_base_uuid}: 突合終了")
    return duplicate_list


def duplicate_book_save(db: Session, uuid_1, uuid_2, score):
    duplication_book = db.query(DuplicationModel).filter(or_(
        DuplicationModel.book_uuid_1 == uuid_1,
        DuplicationModel.book_uuid_1 == uuid_2,
        DuplicationModel.book_uuid_2 == uuid_1,
        DuplicationModel.book_uuid_2 == uuid_2,
    )).all()
    if duplication_book == []:
        duplication_uuid = uuid.uuid4()

    else:
        duplication_uuid = duplication_book[0].duplication_id,

    db.merge(DuplicationModel(
        duplication_id = duplication_uuid,
        book_uuid_1 = uuid_1,
        book_uuid_2 = uuid_2,
        score = score,
    ))
    db.commit()


def get_ahash_task(send_rev, book_uuids):
    def get_ahash(book_uuid):
        return str(imagehash.average_hash(Image.open(f'{DATA_ROOT}/book_thum/{book_uuid}.jpg'), hash_size=16))

    result = []
    for book_uuid in book_uuids:
        ahash = get_ahash(book_uuid[0])
        logger.info(f"{book_uuid[0]} : ahash {ahash}")
        result.append({
            "uuid": book_uuid[0],
            "ahash": ahash
        })
    send_rev.send(result)


if __name__ == "__main__":
    main()
