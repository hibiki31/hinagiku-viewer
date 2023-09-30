import datetime
import glob
import json
import os
import shutil
import time
import uuid
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

    done_uuids = []
    books = db.query(BookModel.uuid, BookModel.ahash).all()
    logger.info(f"{len(books)}件でハッシュ突合を行います")
    
    for (book_base_uuid, book_base_ahash) in books:
        for (book_check_uuid, book_check_ahash) in books:
            if book_base_uuid == book_check_uuid:
                continue
            # チェック対象の本がすでにbook_baseで検査済みならスキップ
            if book_check_uuid in done_uuids:
                continue

            hash1 = int(book_base_ahash,16)
            hash2 = int(book_check_ahash,16)
            score = bin(hash1 ^ hash2).count('1')
            if score < 50:
                logger.info(f"{book_base_uuid}, {book_check_uuid}, {score}")

                duplication_book = db.query(DuplicationModel).filter(or_(
                    DuplicationModel.book_uuid_1 == book_base_uuid,
                    DuplicationModel.book_uuid_1 == book_check_uuid,
                    DuplicationModel.book_uuid_2 == book_base_uuid,
                    DuplicationModel.book_uuid_2 == book_check_uuid,
                )).all()
                if duplication_book == []:
                    duplication_uuid = uuid.uuid4()
                
                else:
                    duplication_uuid = duplication_book[0].duplication_id,

                db.merge(DuplicationModel(
                    duplication_id = duplication_uuid,
                    book_uuid_1 = book_base_uuid,
                    book_uuid_2 = book_check_uuid,
                    score = score,
                ))
                db.commit()
            
            done_uuids.append(book_base_uuid)
        logger.info(f"{book_base_uuid}: 突合終了")



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