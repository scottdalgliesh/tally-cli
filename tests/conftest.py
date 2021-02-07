#pylint:disable=[missing-function-docstring, redefined-outer-name, unused-argument]

import os
from datetime import date

import pytest
from tally import categ
from tally.models import ActiveUser, Base, Category, User, session
from tally.utils import new_bill


@pytest.fixture(autouse=True)
def check_env():
    """Verify TALLY_TESTING evironment variable is set before running tests."""
    if os.environ.get('TALLY_TESTING') != '1':
        raise RuntimeError(
            'Environment variable "TALLY_TESTING" not detected or misconfigured.'
            '\nAborting tests to preserve production database integrity.')


@pytest.fixture
def clear_test_db():
    """Reset database & session state before/after tests."""
    Base.metadata.drop_all()
    session.close()
    Base.metadata.create_all()
    yield session.rollback()


@pytest.fixture
def sample_db(clear_test_db):
    """Populate test database with sample data."""
    users = [
        User(name='scott'),
        User(name='sarah')
    ]
    session.add_all(users)
    session.commit()

    active_user = ActiveUser(name='scott')
    session.add(active_user)
    session.commit()

    categs = [
        Category(name='groceries', user_name='scott'),
        Category(name='gas', user_name='scott'),
        Category(name='misc', user_name='scott'),
        Category(name='groceries', user_name='sarah'),
        Category(name='gas', user_name='sarah'),
        Category(name='misc', user_name='sarah'),
    ]
    session.add_all(categs)
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


@pytest.fixture
def empty_db(clear_test_db):
    """Populate test database with minimal sample data."""
    user = User(name='scott')
    session.add(user)
    active_user = ActiveUser(name='scott')
    session.add(active_user)
    user.categories.extend(
        [Category(name='category1'), Category(name='category2')])
    session.commit()


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
    session.add_all(new_bills)
    session.commit()

    hidden_categ = Category(
        name='sample_hidden', user_name='scott', hidden=True)
    session.add(hidden_categ)
    hidden_bill = new_bill(
        date(2000, 1, 1), 'hidden', 100, 'scott', 'sample_hidden')
    session.add(hidden_bill)
    session.commit()


@pytest.fixture()
def sample_bill():
    return new_bill(date(2020, 1, 26), 'sample', 100,
                    'scott', 'groceries')


@pytest.fixture
def mock_pick(monkeypatch):
    def _mock_pick(categories, message):
        '''Select category1 if 1 appended to description, else category2'''
        if message.rstrip("\"")[-1] == '1':
            return ('category1', 0)
        else:
            return ('category2', 0)
    monkeypatch.setattr(categ, 'pick', _mock_pick)
