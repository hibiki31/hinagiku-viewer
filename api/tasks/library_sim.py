import datetime
import glob
import json
import os
import shutil
import time
import uuid

import imagehash
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import or_

from books.models import BookModel, DuplicationModel
from mixins.log import setup_logger
from settings import DATA_ROOT


logger = setup_logger(__name__)


def main(db: Session, mode):
    if mode == "all":
        books = db.query(BookModel).all()
        for book in books:
            ahash = str(imagehash.average_hash(Image.open(f'{DATA_ROOT}/book_thum/{book.uuid}.jpg'), hash_size=16))
            book.ahash = ahash
            logger.info(f"{book.uuid} : ahash {ahash}")
            db.commit()

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
        

if __name__ == "__main__":
    main()