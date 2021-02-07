# pylint:disable=[missing-class-docstring, missing-module-docstring]

from sqlalchemy import (Boolean, Column, Date, Float, ForeignKey, Integer,
                        String, UniqueConstraint, create_engine, event)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from . import config


def _fk_pragma_on_connect(dbapi_con, con_record):  # pylint: disable=unused-argument
    """Enable foreign key enforcement for SQLite3"""
    dbapi_con.execute('pragma foreign_keys=ON')


engine = create_engine(f'sqlite:///{config.DB_URL}')
event.listen(engine, 'connect', _fk_pragma_on_connect)
Session = sessionmaker(engine)
session = Session()

Base = declarative_base(bind=engine)


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
    hidden = Column(Boolean, default=False)
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


Base.metadata.create_all()
