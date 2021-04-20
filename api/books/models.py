from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from mixins.database import Base, Engine


class BookModel(Base):
    __tablename__ = "books"
    uuid = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'))
    # ソフトメタデータ
    library = Column(String)
    title = Column(String)
    author = Column(String)
    series = Column(String)
    series_no = Column(Integer)
    genre = Column(String)
    publisher = Column(String)
    # ハードメタデータ
    size = Column(Integer)
    page = Column(Integer)
    add_date = Column(DateTime)
    file_date = Column(DateTime)
    import_file_name = Column(String)
    # 設定
    is_shered = Column(Boolean)