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


def main(db: Session, uuid: str=None):
    pass


if __name__ == "__main__":
    main()