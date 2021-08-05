from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table
from sqlalchemy.orm import relationship
from mixins.database import Base, Engine

books_to_tags = Table('tag_to_book', Base.metadata,
    Column('book_uuid', String, ForeignKey('book.uuid')),
    Column('tags_id', Integer, ForeignKey('tag.id'))
)

books_to_authors = Table('book_to_author', Base.metadata,
    Column('book_uuid', String, ForeignKey('book.uuid')),
    Column('author_id', Integer, ForeignKey('author.id'))
)


class TagsModel(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship(
        'BookModel',
        secondary=books_to_tags,
        back_populates='tags',
        lazy=False,
    )

class LibraryModel(Base):
    __tablename__ = 'library'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='library')

class AuthorModel(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String)
    books = relationship(
        'BookModel',
        secondary=books_to_authors,
        back_populates='authors',
        lazy=False,
    )


class GenreModel(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='genre')


class PublisherModel(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='publisher')


class SeriesModel(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='series')



class BookModel(Base):
    __tablename__ = "book"
    uuid = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    # ソフトメタデータ
    title = Column(String)
    
    library_id = Column(Integer, ForeignKey('library.id'), nullable=False)
    library = relationship('LibraryModel',lazy=False, back_populates='books')
    
    authors = relationship(
        'AuthorModel',
        secondary=books_to_authors,
        back_populates='books',
        lazy=False,
    )

    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship('GenreModel',lazy=False, back_populates='books')
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    publisher = relationship('PublisherModel',lazy=False, back_populates='books')
    series_id = Column(Integer, ForeignKey('series.id'))
    series = relationship('SeriesModel',lazy=False, back_populates='books')
    series_no = Column(Integer)

    # タグ
    tags = relationship(
        'TagsModel',
        secondary=books_to_tags,
        back_populates='books',
        lazy=False,
    )
    
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
    user_data = relationship('BookUserMetaDataModel',lazy=False)

class BookUserMetaDataModel(Base):
    __tablename__ = "books_metadata"
    user_id = Column(String, ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    book_uuid = Column(String, ForeignKey('book.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    last_open_date = Column(DateTime)
    read_times = Column(Integer)
    open_page = Column(Integer)
    rate = Column(Integer)