from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixins.database import Base, Engine


class BookModel(Base):
    __tablename__ = "books"
    uuid = Column(String, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    series = Column(String)
    series_no = Column(Integer)
    size = Column(Integer)
    page = Column(Integer)
    add_date = Column(DateTime)
    file_date = Column(DateTime)
    cache_date = Column(DateTime)
    open_date = Column(DateTime)
    import_file_name = Column(String)
    state = Column(String)
    