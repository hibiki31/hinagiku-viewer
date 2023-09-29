from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table, Numeric
from sqlalchemy.orm import relationship
from mixins.database import Base, Engine


books_to_tags = Table('tag_to_book', Base.metadata,
    Column('book_uuid', String, ForeignKey('books.uuid')),
    Column('tags_id', Integer, ForeignKey('tags.id'))
)


books_to_authors = Table('book_to_author', Base.metadata,
    Column('book_uuid', String, ForeignKey('books.uuid')),
    Column('author_id', Integer, ForeignKey('authors.id'))
)


librarys_to_users = Table('library_to_user', Base.metadata,
    Column('library_id', Integer, ForeignKey('librarys.id')),
    Column('user_id', String, ForeignKey('users.id'))
)


class LibraryModel(Base):
    __tablename__ = 'librarys'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    books = relationship('BookModel',lazy=False, back_populates='library')
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    shered_users = relationship(
        'UserModel',
        secondary=librarys_to_users,
        back_populates='librarys',
        lazy=False,
    )


class AuthorModel(Base):
    __tablename__ = 'authors'
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
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='genre')


class PublisherModel(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='publisher')


class SeriesModel(Base):
    __tablename__ = 'series'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship('BookModel',lazy=False, back_populates='series')


class BookModel(Base):
    __tablename__ = "books"
    # ID
    uuid = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    
    # ハードメタデータ
    size = Column(Numeric, nullable=False)
    sha1 = Column(String, nullable=False)
    ahash = Column(String, nullable=True)
    page = Column(Integer, nullable=False)
    add_date = Column(DateTime, nullable=False)
    file_date = Column(DateTime, nullable=False)
    import_file_name = Column(String, nullable=False)
    chached = Column(Boolean, nullable=False, server_default='f', default=False)
    
    # ソフトメタデータ
    title = Column(String)
    series_no = Column(Integer)
    
    # ソフトメタデータ 多対一
    library_id = Column(Integer, ForeignKey('librarys.id'), nullable=False)
    library = relationship('LibraryModel',lazy=False, back_populates='books')
    genre_id = Column(Integer, ForeignKey('genres.id'))
    genre = relationship('GenreModel',lazy=True, back_populates='books')
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    publisher = relationship('PublisherModel',lazy=True, back_populates='books')
    series = relationship('SeriesModel',lazy=True, back_populates='books')
    series_id = Column(Integer, ForeignKey('series.id'))
    
    # ソフトメタデータ 多対多
    authors = relationship(
        'AuthorModel',
        secondary=books_to_authors,
        back_populates='books',
        lazy=True,
    )
    tags = relationship(
        'TagsModel',
        secondary=books_to_tags,
        back_populates='books',
        lazy=True,
    )
    
    # 設定
    is_shered = Column(Boolean)
    
    # ユーザ固有データ
    user_data = relationship('BookUserMetaDataModel',lazy=False)
    
    # 処理用
    state = Column(String)


class BookUserMetaDataModel(Base):
    __tablename__ = "book_metadatas"
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    book_uuid = Column(String, ForeignKey('books.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    last_open_date = Column(DateTime)
    read_times = Column(Integer)
    open_page = Column(Integer)
    rate = Column(Integer)


class TagsModel(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    books = relationship(
        'BookModel',
        secondary=books_to_tags,
        back_populates='tags',
        lazy=True,
    )


class DuplicationModel(Base):
    __tablename__ = 'duplication'
    duplication_id = Column(String)
    book_uuid_1 = Column(String, ForeignKey('books.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    book_uuid_2 = Column(String, ForeignKey('books.uuid', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    score = Column(Integer)