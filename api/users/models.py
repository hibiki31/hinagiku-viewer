from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

import books.models as books_models
from mixins.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    password = Column(String)
    is_admin = Column(Boolean)
    books = relationship("BookModel")
    libraries = relationship(
        'LibraryModel',
        secondary=books_models.libraries_to_users,
        back_populates='shared_users',
        lazy=False,
    )
