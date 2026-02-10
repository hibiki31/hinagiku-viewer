from pprint import pprint

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import SQLALCHEMY_DATABASE_URL


# プリントでデバッグしやすいように
class RepresentableBase:
    def __repr__(self):
        columns = ', '.join([
            f'{k}={self.__dict__[k]!r}'
            for k in self.__dict__ if k[0] != '_'
        ])
        return f'<{self.__class__.__name__}({columns})>'
    def debug(self):
        print('<self.__class__.__name__>')
        pprint(self.__dict__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_url():
    return SQLALCHEMY_DATABASE_URL


Engine = create_engine(
    get_db_url(), connect_args={}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# 全てのクラスに共通のスーパークラスを追加
Base = declarative_base(cls=RepresentableBase)
