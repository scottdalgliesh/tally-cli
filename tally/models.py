# pylint:disable=[missing-class-docstring, missing-module-docstring]

from pathlib import Path
from typing import Optional, Union

from sqlalchemy import (Column, Date, Float, ForeignKey, Integer, String,
                        UniqueConstraint, create_engine, event)
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import Session

from . import config


def get_engine(url: Optional[Union[str, Path]] = None) -> Engine:
    """Wrapper to delay engine instantiation until runtime."""
    if url is None:
        url = config.DB_URL
    engine = create_engine(f'sqlite:///{url}')
    event.listen(engine, 'connect', _fk_pragma_on_connect)
    return engine


def get_session(url: Optional[Union[str, Path]] = None) -> Session:
    """Wrapper to delay session instantiation until runtime."""
    if url is None:
        url = config.DB_URL
    engine = get_engine(url)
    session = sessionmaker(engine)
    return session()


def _fk_pragma_on_connect(dbapi_con, con_record):  # pylint: disable=unused-argument
    """Enable foreign key enforcement for SQLite3"""
    dbapi_con.execute('pragma foreign_keys=ON')


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    name = Column(String, primary_key=True)
    categories = relationship('Category', back_populates='user',
                              cascade='all, delete-orphan')
    bills = relationship('Bill', back_populates='user',
                         cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User(user_name="{self.name}")>'


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_name = Column(
        String,
        ForeignKey('users.name', onupdate='CASCADE', ondelete='CASCADE'))
    user = relationship('User', back_populates='categories')
    bills = relationship('Bill', back_populates='category',
                         cascade='all, delete-orphan')
    __table_args__ = (UniqueConstraint(
        'user_name', 'name', name='user-category-uc'),)

    def __repr__(self):
        return f'<Category(name="{self.name}", user_name="{self.user_name}")>'


class Bill(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    descr = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    user_name = Column(
        String,
        ForeignKey('users.name', onupdate='CASCADE', ondelete='CASCADE'))
    category_id = Column(
        Integer,
        ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE'))
    user = relationship('User', back_populates='bills')
    category = relationship('Category', back_populates='bills')

    def __repr__(self):
        return (
            f'<Bill(date="{self.date}", descr="{self.descr}", '
            f'value="{self.value}", user_name="{self.user_name}", '
            f'category_id={self.category_id})>')


class ActiveUser(Base):
    __tablename__ = 'active_user'
    name = Column(
        String,
        ForeignKey('users.name', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )
    user = relationship('User')

    def __repr__(self):
        return f'<ActiveUser(name="{self.name}")>'


Base.metadata.create_all(get_engine())
