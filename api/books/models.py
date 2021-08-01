from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from mixins.database import Base, Engine

association_table = Table('tag_to_book', Base.metadata,
    Column('book_uuid', String, ForeignKey('books.uuid')),
    Column('tags_id', Integer, ForeignKey('tags.id'))
)


class TagsModel(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship(
        'BookModel',
        secondary=association_table,
        back_populates='tags',
        lazy=False,
    )

class LibraryModel(Base):
    __tablename__ = 'library'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False)

class AuthorModel(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String)
    books = relationship('BookModel',lazy=False)


class GenreModel(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False)


class PublisherModel(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False)


class SeriesModel(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False)



class BookModel(Base):
    __tablename__ = "books"
    uuid = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    # ソフトメタデータ
    title = Column(String)
    library = Column(Integer, ForeignKey('library.id'), nullable=False)
    author = Column(Integer, ForeignKey('author.id'))
    genre = Column(Integer, ForeignKey('genre.id'))
    publisher = Column(Integer, ForeignKey('publisher.id'))
    series = Column(Integer, ForeignKey('series.id'))
    series_no = Column(Integer)
    
    # ハードメタデータ
    size = Column(Integer)
    sha1 = Column(String)
    page = Column(Integer)
    add_date = Column(DateTime)
    file_date = Column(DateTime)
    import_file_name = Column(String)
    # 設定
    is_shered = Column(Boolean)
    state = Column(String)
    # タグ
    tags = relationship(
        'TagsModel',
        secondary=association_table,
        back_populates='books',
        lazy=False,
    )
    user_data = relationship('BookUserMetaDataModel',lazy=False)

class BookUserMetaDataModel(Base):
    __tablename__ = "books_metadata"
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    book_uuid = Column(String, ForeignKey('books.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    last_open_date = Column(DateTime)
    read_times = Column(Integer)
    open_page = Column(Integer)
    rate = Column(Integer)