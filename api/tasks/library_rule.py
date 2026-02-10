
from typing import Optional

from sqlalchemy.orm import Session

from mixins.log import setup_logger

logger = setup_logger(__name__)


def main(db: Session, uuid: Optional[str] = None, task_id: Optional[str] = None):
    pass


if __name__ == "__main__":
    main()
