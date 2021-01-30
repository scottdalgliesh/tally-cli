#pylint:disable=[missing-function-docstring, unused-argument]

from datetime import date

import pandas as pd
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from tally.models import ActiveUser, Bill, Category, User, engine, session
from tally.utils import new_bill


def test_basic_query(sample_db):
    res_users = session.query(User).all()
    assert len(res_users) == 2
    assert res_users[0].name == 'scott'
    assert isinstance(res_users[0], User)


def test_pandas_query(sample_db):
    res = pd.read_sql('bills', engine, parse_dates='date')
    assert len(res) == 8
    assert res.loc[0, 'date'] == date(2020, 1, 26)
    assert isinstance(res, pd.DataFrame)


def test_bill_with_bad_user(sample_db, sample_bill):
    sample_bill.user_name = 'Zack'
    with pytest.raises(IntegrityError):
        session.add(sample_bill)
        session.commit()


def test_dup_user(sample_db):
    sample_user = User(name="scott")
    with pytest.raises(IntegrityError):
        session.add(sample_user)
        session.commit()


def test_bill_with_bad_category(sample_db):
    with pytest.raises(NoResultFound):
        bill = new_bill(date(2020, 1, 26), 'sample',
                        100, 'scott', 'unknown_category')
        session.add(bill)
        session.commit()


def test_user_update(sample_db):
    # get bills associated with user, then update user name
    user = session.query(User).filter_by(name='scott').first()
    old_user_bills = user.bills
    user.name = 'sam'
    session.commit()
    # get bills associated with new user name and verify against originals
    new_user = session.query(User).filter_by(name='sam').first()
    new_user_bills = new_user.bills
    assert old_user_bills == new_user_bills
    # verify old user name no longer exists in db
    assert session.query(User).filter_by(name='scott').count() == 0
    assert session.query(Bill).filter_by(
        user_name='scott').count() == 0


def test_category_update(sample_db):
    # get bills associated with category, then update category name
    category = session.query(Category).filter_by(name='gas',
                                                 user_name='scott').first()
    old_category_bills = category.bills
    category.name = 'vehicle'
    session.commit()
    # get bills associated with new category name and verify against originals
    new_category = session.query(Category).filter_by(name='vehicle').first()
    new_category_bills = new_category.bills
    assert old_category_bills == new_category_bills
    # verify old category name no longer exists in db
    assert session.query(Category).filter_by(name='gas',
                                             user_name='scott').count() == 0
    assert session.query(Bill).join(Category).\
        filter(Category.name == 'gas').\
        filter(Bill.user_name == 'scott').count() == 0


def test_active_user_update(sample_db):
    active_user = session.query(ActiveUser).first()
    active_user_bills = active_user.user.bills
    assert active_user_bills[0].descr == 'zehrs'
    active_user.name = 'sarah'
    session.commit()
    new_active_user = session.query(ActiveUser).first().user
    new_active_user_bills = new_active_user.bills
    assert new_active_user_bills[0].descr == 'petro'
