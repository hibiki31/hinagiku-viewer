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
    if mode == "all":
        books = db.query(BookModel).all()
        for book in books:
            ahash = str(imagehash.average_hash(Image.open(f'{DATA_ROOT}/book_thum/{book.uuid}.jpg'), hash_size=16))
            book.ahash = ahash
            logger.info(f"{book.uuid} : ahash {ahash}")
            db.commit()

    # リザルト取得迄は恐らく動く、resultのリストをDBにUpdateするところで断念
    if mode == "all-multiprocess":
        books = db.query(BookModel.uuid).all()

        process_list = []
        result = []

        size = len(books)
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

    done_uuids = []
    
    if mode == "all":
        books = db.query(BookModel).all()
        for book_base in books:
            for book_check in books:
                if book_base.uuid == book_check.uuid:
                    continue
                # チェック対象の本がすでにbook_baseで検査済みならスキップ
                if book_check.uuid in done_uuids:
                    continue

                hash1 = int(book_base.ahash,16)
                hash2 = int(book_check.ahash,16)
                score = bin(hash1 ^ hash2).count('1')
                if score < 50:
                    logger.info(f"{book_base.uuid}, {book_check.uuid}, {score}")

                    duplication_book = db.query(DuplicationModel).filter(or_(
                        DuplicationModel.book_uuid_1 == book_base.uuid,
                        DuplicationModel.book_uuid_1 == book_check.uuid,
                        DuplicationModel.book_uuid_2 == book_base.uuid,
                        DuplicationModel.book_uuid_2 == book_check.uuid,
                    )).all()
                    if duplication_book == []:
                        duplication_uuid = uuid.uuid4()
                    
                    else:
                        duplication_uuid = duplication_book[0].duplication_id,

                    db.add(DuplicationModel(
                        duplication_id = duplication_uuid,
                        book_uuid_1 = book_base.uuid,
                        book_uuid_2 = book_check.uuid,
                        score = score,
                    ))
                    db.commit()
                
                done_uuids.append(book_base.uuid)



def get_ahash_task(send_rev, book_uuids):
    get_ahash = lambda book_uuid : str(imagehash.average_hash(Image.open(f'{DATA_ROOT}/book_thum/{book_uuid}.jpg'), hash_size=16))

    result = []
    for book_uuid in book_uuids:
        ahash = get_ahash(book_uuid)
        logger.info(f"{book_uuid} : ahash {ahash}")
        result.append({
            "uuid": book_uuid,
            "ahash": ahash
        })
    send_rev.send(result)


if __name__ == "__main__":
    main()