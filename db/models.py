from sqlalchemy import create_engine, String, ForeignKey, BOOLEAN
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column

from db.config import *

engine = create_engine("postgresql+psycopg2://postgres:1@localhost:5432/shop_db")

class Base(DeclarativeBase):
    pass

class QR(Base,CRUD):
    __tablename__ = "qr_codes"
    id:Mapped[int] = mapped_column(primary_key = True, autoincrement=True)
    is_active:Mapped[bool] = mapped_column(BOOLEAN, default=True)


class User(Base,CRUD):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key = True, autoincrement=True)
    name:Mapped[str] = mapped_column(String(255))
    qr_code_id:Mapped[int] = mapped_column(ForeignKey('qr_codes.id', ondelete='cascade'))

Base.metadata.create_all(engine)


