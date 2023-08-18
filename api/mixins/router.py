from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from mixins.database import get_db
from mixins.log import setup_logger
from mixins.schema import BaseSchema
from settings import API_VERSION
from users.models import UserModel


app = APIRouter(prefix="/api",tags=["mixin"])
logger = setup_logger(__name__)


class Version(BaseSchema):
    initialized: bool
    version: str


@app.get("/version", response_model=Version)
def get_version(
        db: Session = Depends(get_db)
    ):
    '''
    初期化済みか判定用
    '''
    initialized = (not db.query(UserModel).all() == [])

    return {"initialized": initialized, "version": API_VERSION}