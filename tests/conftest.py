#pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

from datetime import date
import sys

import pytest

from tally import config
from tally import categ
from tally.models import ActiveUser, Base, Bill, Category, User, get_engine, get_session

def new_bill(date, descr, value, user_name, category_name):
    """Wrapper function for compact bill definitions below."""
    return Bill(date=date, descr=descr, value=value, user_name=user_name,
                category_name=category_name)


@pytest.fixture
def test_db_path(tmp_path):
    """Create fresh testing directory"""
    return tmp_path / 'test.db'


@pytest.fixture()
def patch_db(monkeypatch, test_db_path):
    """Patch DB URL for testing"""
    monkeypatch.setattr(config, 'DB_URL', str(test_db_path))


@pytest.fixture
def engine(patch_db):
    """Generate test engine"""
    engine = get_engine()
    Base.metadata.create_all(engine)  # type: ignore
    return engine


@pytest.fixture
def session(patch_db):
    """Generate session object"""
    return get_session()


@pytest.fixture
def sample_db(test_db_path, engine, session):
    # create fresh testing directory
    users = [
        User(name='scott'),
        User(name='sarah')
    ]

    active_user = ActiveUser(name='scott')

    categories = [
        Category(name='groceries'),
        Category(name='gas'),
        Category(name='misc'),
    ]

    bills = [
        new_bill(date(2020, 1, 26), 'zehrs', 100, 'scott', 'groceries'),
        new_bill(date(2020, 1, 27), 'walmart', 200, 'scott', 'misc'),
        new_bill(date(2020, 1, 28), 'ren\'s', 300, 'scott', 'misc'),
        new_bill(date(2020, 1, 29), 'sobeys', 400, 'scott', 'groceries'),
        new_bill(date(2020, 1, 26), 'petro', 500, 'sarah', 'gas'),
        new_bill(date(2020, 1, 27), 'canadian tire', 600, 'sarah', 'misc'),
        new_bill(date(2020, 1, 28), 'shell', 700, 'sarah', 'gas'),
        new_bill(date(2020, 1, 29), 'no frills', 800, 'sarah', 'groceries'),
    ]

    session.add_all(users)
    session.add(active_user)
    session.add_all(categories)
    session.add_all(bills)
    session.commit()
    return session

@pytest.fixture
def empty_db(test_db_path, engine, session):
    user = User(name='scott')
    active_user = ActiveUser(name='scott')
    categories = [Category(name='category1'), Category(name='category2')]
    session.add_all([user, active_user, *categories])
    session.commit()
    return session

@pytest.fixture()
def sample_bill():
    return Bill(date=date(2020, 1, 26), descr='sample', value=100,
                user_name='scott', category_name='groceries')


@pytest.fixture()
def sample_user():
    return User(name='delta')


@pytest.fixture()
def mock_exit(monkeypatch):
    def new_exit():
        pass
    monkeypatch.setattr(sys, 'exit', new_exit)

@pytest.fixture
def mock_pick(monkeypatch):
    def _mock_pick(categories, message):
        '''Select category1 if 1 appended to description, else category2'''
        if message.rstrip("\"")[-1] == '1':
            return ('category1', 0)
        else:
            return ('category2', 0)
    monkeypatch.setattr(categ, 'pick', _mock_pick)
