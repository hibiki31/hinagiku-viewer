from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixins.database import Base
import books.models as books_models

class UserModel(Base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)
    password = Column(String)
    is_admin = Column(Boolean)
    books = relationship("BookModel")
    librarys = relationship(
        'LibraryModel',
        secondary=books_models.librarys_to_users,
        back_populates='shered_users',
        lazy=False,
    )