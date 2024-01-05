import datetime
import glob
import json
import os
import shutil
import time
import uuid
import sys
from multiprocessing import Array, Pipe, Process, Queue, Value

import imagehash
from PIL import Image
from sqlalchemy import or_
from sqlalchemy.orm import Session

from books.models import BookModel, DuplicationModel
from mixins.log import setup_logger
from settings import CONVERT_THREAD, DATA_ROOT

logger = setup_logger(__name__)


def main(db: Session, mode):
    ## multithreadでハッシュを取得する、取得済みは基本スキップ
    if mode == "all-force":
        books = db.query(BookModel.uuid).all()
    else:
        books = db.query(BookModel.uuid).filter(BookModel.ahash == None).all()
    
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
            start = int((size*i/CONVERT_THREAD))
            end = int((size*(i+1)/CONVERT_THREAD))
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
        logger.info(f"DBへの書き込み完了")

    ## DBのデータで突合開始
    db_ahash_check(db=db)


def db_ahash_check(db: Session):
    db.query(DuplicationModel).delete()
    db.commit()
    check_delete = db.query(DuplicationModel).all()
    logger.info(check_delete)
    # done_uuids = []
    books_list = [(book[0], book[1]) for book in db.query(BookModel.uuid, BookModel.ahash).limit(10000).all()]
    
    logger.info(f"{len(books_list)}件でハッシュ突合を行います 配列のメモリ使用量{round(sys.getsizeof(books_list)/1024,2)} kb")
    
    size = len(books_list)
    logger.info(f"{CONVERT_THREAD}のスレッドで{size}件のAhashを突合します")
    
    process_list = []
    result = []
    
    for i in range(CONVERT_THREAD):
        start = int((size*i/CONVERT_THREAD))
        end = int((size*(i+1)/CONVERT_THREAD))
        logger.info(f"process[{i}]: {start}:{end}")
        get_rev,send_rev  = Pipe(False)
        process_list.append((
            Process(target=check_ahash_range, args=(send_rev, books_list[start:end], books_list)),
            get_rev
        ))

    for i in process_list:
        i[0].start()
        
    logger.info(f"{len(books_list)}件でハッシュ突合を開始")
    for i in process_list:
        i[0].join()
        result.extend(i[1].recv())
    logger.info(f"{len(books_list)}件でハッシュ突合を終了")
    
    logger.info(f"{len(result)}の重複内容をデータベースに保存中")
    for i in result:
        duplicate_book_save(db=db, uuid_1=i[0], uuid_2=i[1], score=i[2])
        


def check_ahash_range(send_rev, src_books, all_books):
    duplicate_list = []
    logger.info(f"{len(src_books)} * {len(all_books)}")
    for (book_base_uuid, book_base_ahash) in src_books:
        for (book_check_uuid, book_check_ahash) in all_books:
            if book_base_uuid == book_check_uuid:
                continue
            # チェック対象の本がすでにbook_baseで検査済みならスキップ
            # if book_check_uuid in done_uuids:
            #     continue

            hash1 = int(book_base_ahash,16)
            hash2 = int(book_check_ahash,16)
            score = bin(hash1 ^ hash2).count('1')
            # 閾値
            if score < 10:
                logger.info(f"{book_base_uuid}, {book_check_uuid}, {score}")
                duplicate_list.append(
                    (book_base_uuid, book_check_uuid, score)
                )
                
            
            # done_uuids.append(book_base_uuid)
        logger.info(f"{book_base_uuid}: 突合終了")
    send_rev.send(duplicate_list)
    logger.info("プロセスの処理が終了")


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
    get_ahash = lambda book_uuid : str(imagehash.average_hash(Image.open(f'{DATA_ROOT}/book_thum/{book_uuid}.jpg'), hash_size=16))

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