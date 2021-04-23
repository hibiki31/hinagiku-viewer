from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from mixins.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    password = Column(String)
    is_admin = Column(Boolean)
    books = relationship("BookModel")