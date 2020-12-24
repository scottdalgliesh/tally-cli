#pylint:disable=[missing-function-docstring, unused-argument]

from datetime import date

import pandas as pd
import pytest
from sqlalchemy.exc import IntegrityError

from tally.models import ActiveUser, Bill, Category, User


def test_basic_query(sample_db):
    res_users = sample_db.query(User).all()
    assert len(res_users) == 2
    assert res_users[0].name == 'scott'
    assert isinstance(res_users[0], User)


def test_pandas_query(sample_db, engine):
    res = pd.read_sql('bills', engine, parse_dates='date')
    assert len(res) == 8
    assert res.loc[0, 'date'] == date(2020, 1, 26)
    assert isinstance(res, pd.DataFrame)


def test_bill_with_bad_user(sample_db, sample_bill):
    sample_bill.user_name = 'Zack'
    with pytest.raises(IntegrityError):
        sample_db.add(sample_bill)
        sample_db.commit()


def test_dup_user(sample_db, sample_user):
    sample_user.name = 'scott'
    with pytest.raises(IntegrityError):
        sample_db.add(sample_user)
        sample_db.commit()


def test_bill_with_bad_category(sample_db, sample_bill):
    sample_bill.category_name = 'unknown_category'
    with pytest.raises(IntegrityError):
        sample_db.add(sample_bill)
        sample_db.commit()


def test_user_update(sample_db):
    # get bills associated with user, then update user name
    user = sample_db.query(User).filter_by(name='scott').first()
    old_user_bills = user.bills
    user.name = 'sam'
    sample_db.commit()
    # get bills associated with new user name and verify against originals
    new_user = sample_db.query(User).filter_by(name='sam').first()
    new_user_bills = new_user.bills
    assert old_user_bills == new_user_bills
    # verify old user name no longer exists in db
    assert len(sample_db.query(User).filter_by(name='scott').all()) == 0
    assert len(sample_db.query(Bill).filter_by(
        category_name='scott').all()) == 0


def test_category_update(sample_db):
    # get bills associated with category, then update category name
    category = sample_db.query(Category).filter_by(name='gas').first()
    old_category_bills = category.bills
    category.name = 'vehicle'
    sample_db.commit()
    # get bills associated with new category name and verify against originals
    new_category = sample_db.query(Category).filter_by(name='vehicle').first()
    new_category_bills = new_category.bills
    assert old_category_bills == new_category_bills
    # verify old category name no longer exists in db
    assert len(sample_db.query(Category).filter_by(name='gas').all()) == 0
    assert len(sample_db.query(Bill).filter_by(category_name='gas').all()) == 0


def test_active_user_update(sample_db):
    active_user = sample_db.query(ActiveUser).first()
    active_user_bills = active_user.user.bills
    assert active_user_bills[0].descr == 'zehrs'
    active_user.name = 'sarah'
    sample_db.commit()
    new_active_user = sample_db.query(ActiveUser).first().user
    new_active_user_bills = new_active_user.bills
    assert new_active_user_bills[0].descr == 'petro'
