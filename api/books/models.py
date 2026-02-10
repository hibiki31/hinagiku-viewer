from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.orm import relationship

from mixins.database import Base

books_to_tags = Table('tag_to_book', Base.metadata,
    Column('book_uuid', String, ForeignKey('books.uuid', onupdate='CASCADE', ondelete='CASCADE')),
    Column('tags_id', Integer, ForeignKey('tags.id', onupdate='CASCADE', ondelete='CASCADE'))
)


books_to_authors = Table('book_to_author', Base.metadata,
    Column('book_uuid', String, ForeignKey('books.uuid', onupdate='CASCADE', ondelete='CASCADE')),
    Column('author_id', Integer, ForeignKey('authors.id', onupdate='CASCADE', ondelete='CASCADE'))
)


libraries_to_users = Table('library_to_user', Base.metadata,
    Column('library_id', Integer, ForeignKey('libraries.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('user_id', String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
)


class LibraryModel(Base):
    __tablename__ = 'libraries'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    books = relationship('BookModel',lazy=False, back_populates='library')
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    shared_users= relationship(
        'UserModel',
        secondary=libraries_to_users,
        back_populates='libraries',
        lazy=False,
    )


class AuthorModel(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    is_favorite = Column(Boolean, nullable=False, server_default='f', default=False)
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
    phash = Column(String, nullable=True)
    dhash = Column(String, nullable=True)
    page = Column(Integer, nullable=False)
    add_date = Column(DateTime, nullable=False)
    file_date = Column(DateTime, nullable=False)
    import_file_name = Column(String, nullable=False)
    cached = Column(Boolean, nullable=False, server_default='f', default=False)

    # ソフトメタデータ
    title = Column(String)
    series_no = Column(Integer)

    # ソフトメタデータ 多対一
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable=False)
    library = relationship('LibraryModel',lazy=False, back_populates='books')
    genre_id = Column(Integer, ForeignKey('genres.id'))
    genre = relationship('GenreModel',lazy=False, back_populates='books')
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
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
    is_shared = Column(Boolean)

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


class DuplicateSettingsModel(Base):
    __tablename__ = 'duplicate_settings'
    id = Column(Integer, primary_key=True)
    ahash_threshold = Column(Integer, nullable=False, default=10)
    phash_threshold = Column(Integer, nullable=False, default=12)
    dhash_threshold = Column(Integer, nullable=False, default=15)
    lsh_bands = Column(Integer, nullable=False, default=16)
    lsh_band_size = Column(Integer, nullable=False, default=16)
    updated_at = Column(DateTime, nullable=False)
