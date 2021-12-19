from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table, Numeric
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


librarys_to_users = Table('library_to_user', Base.metadata,
    Column('library_id', Integer, ForeignKey('library.id')),
    Column('user_id', String, ForeignKey('user.id'))
)


class LibraryModel(Base):
    __tablename__ = 'library'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    books = relationship('BookModel',lazy=False, back_populates='library')
    user_id = Column(String, ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    shered_users = relationship(
        'UserModel',
        secondary=librarys_to_users,
        back_populates='librarys',
        lazy=False,
    )


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
    # ID
    uuid = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    
    # ハードメタデータ
    size = Column(Numeric, nullable=False)
    sha1 = Column(String, nullable=False)
    page = Column(Integer, nullable=False)
    add_date = Column(DateTime, nullable=False)
    file_date = Column(DateTime, nullable=False)
    import_file_name = Column(String, nullable=False)
    
    # ソフトメタデータ
    title = Column(String)
    series_no = Column(Integer)
    
    # ソフトメタデータ 多対一
    library_id = Column(Integer, ForeignKey('library.id'), nullable=False)
    library = relationship('LibraryModel',lazy=False, back_populates='books')
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship('GenreModel',lazy=False, back_populates='books')
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    publisher = relationship('PublisherModel',lazy=False, back_populates='books')
    series = relationship('SeriesModel',lazy=False, back_populates='books')
    series_id = Column(Integer, ForeignKey('series.id'))
    
    # ソフトメタデータ 多対多
    authors = relationship(
        'AuthorModel',
        secondary=books_to_authors,
        back_populates='books',
        lazy=False,
    )
    tags = relationship(
        'TagsModel',
        secondary=books_to_tags,
        back_populates='books',
        lazy=False,
    )
    
    # 設定
    is_shered = Column(Boolean)
    
    # ユーザ固有データ
    user_data = relationship('BookUserMetaDataModel',lazy=False)
    
    # 処理用
    state = Column(String)


class BookUserMetaDataModel(Base):
    __tablename__ = "books_metadata"
    user_id = Column(String, ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    book_uuid = Column(String, ForeignKey('book.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    last_open_date = Column(DateTime)
    read_times = Column(Integer)
    open_page = Column(Integer)
    rate = Column(Integer)
    ratea = Column(Integer)


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