from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixins.database import Base, Engine


class BookModel(Base):
    __tablename__ = "books"
    uuid = Column(String, primary_key=True, index=True)
    # ソフトメタデータ
    title = Column(String)
    author = Column(String)
    series = Column(String)
    series_no = Column(Integer)
    rate = Column(Integer)
    genre = Column(String)
    library = Column(String)
    publisher = Column(String)
    # ハードメタデータ
    size = Column(Integer)
    page = Column(Integer)
    add_date = Column(DateTime)
    file_date = Column(DateTime)
    import_file_name = Column(String)
    # アクティブメタデータ
    cache_date = Column(DateTime)
    open_date = Column(DateTime)
    open_count = Column(Integer)
    state = Column(String)
    