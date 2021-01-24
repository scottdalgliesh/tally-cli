#pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

from datetime import date
import sys

import pytest

from tally import config
from tally import categ
from tally.models import ActiveUser, Base, Category, User, get_engine, get_session
from tally.utils import new_bill


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
    session.add_all(users)
    session.commit()

    active_user = ActiveUser(name='scott')
    session.add(active_user)
    session.commit()

    categ_names = ['groceries', 'gas', 'misc']
    for user in users:
        for categ_name in categ_names:
            user.categories.append(Category(name=categ_name))
    session.commit()

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
    session.add_all(bills)
    session.commit()
    return session


@pytest.fixture
def empty_db(test_db_path, engine, session):
    user = User(name='scott')
    session.add(user)
    active_user = ActiveUser(name='scott')
    session.add(active_user)
    user.categories.extend(
        [Category(name='category1'), Category(name='category2')])
    session.commit()
    return session


@pytest.fixture
def review_db(sample_db):
    '''Add some additional data to the base sample_db'''
    new_bills = [
        new_bill(date(2019, 12, 31), 'Previous month', 1, 'scott', 'misc'),
        new_bill(date(2020, 1, 1), 'Start of current month',
                 1, 'scott', 'misc'),
        new_bill(date(2020, 1, 31), 'End of current month', 1, 'scott', 'misc'),
        new_bill(date(2020, 2, 1), 'Next month', 1, 'scott', 'misc'),
    ]
    sample_db.add_all(new_bills)
    sample_db.commit()
    return sample_db


@pytest.fixture()
def sample_bill():
    return new_bill(date(2020, 1, 26), 'sample', 100,
                    'scott', 'groceries')


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
