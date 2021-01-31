#pylint:disable=[missing-function-docstring, unused-argument]

from contextlib import nullcontext
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from tally.categ import (TransDict, add_categ, categorize, delete_categ,
                         get_categs, update_categ)
from tally.models import Bill, Category, session

test_input = [
    pytest.param(add_categ, 'new_categ', None, ['groceries', 'gas', 'misc', 'new_categ'],
                 nullcontext(), id='add_categ_valid'),
    pytest.param(add_categ, 'groceries', None, ['groceries', 'gas', 'misc'],
                 pytest.raises(IntegrityError), id='add_categ_duplicate'),
    pytest.param(update_categ, 'groceries', 'groceries2', ['groceries2', 'gas', 'misc'],
                 nullcontext(), id='update_categ_valid'),
    pytest.param(update_categ, 'groceries', 'gas', ['groceries', 'gas', 'misc'],
                 pytest.raises(IntegrityError), id='update_categ_duplicate'),
    pytest.param(update_categ, 'non_existing', 'new', ['groceries', 'gas', 'misc'],
                 pytest.raises(NoResultFound), id='update_categ_non_existing'),
    pytest.param(delete_categ, 'groceries', None, ['gas', 'misc'],
                 nullcontext(), id='delete_categ_valid'),
    pytest.param(delete_categ, 'non_existing', None, ['groceries', 'gas', 'misc'],
                 pytest.raises(NoResultFound), id='delete_categ_non_existing'),
]


@pytest.mark.parametrize('func,categ1,categ2,categ_list,context', test_input)
def test_user_operation(sample_db, func, categ1, categ2, categ_list, context):
    with context:
        if func is update_categ:
            func(categ1, categ2)
        else:
            func(categ1)
    if not context is nullcontext():
        session.rollback()
    categs = session.query(Category).filter_by(user_name='scott').all()
    categ_names = [categ.name for categ in categs]
    assert sorted(categ_names) == sorted(categ_list)


def test_get_categs(sample_db):
    test_categs = get_categs()
    assert sorted(test_categs) == sorted(['groceries', 'gas', 'misc'])


def test_categorize(empty_db, mock_pick):
    trans_dict: TransDict = {
        'Date': [date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3), date(2020, 1, 4)],
        'Value': [100, 200, 300, 400],
        'Description': ['Sample_description_1', 'Sample_description_2',
                        'Sample_description_1', 'Sample_description_2']
    }
    test_msg = categorize(trans_dict, True)
    assert test_msg == '4 transactions added successfully.'

    test_bills = session.query(Bill).all()
    assert len(test_bills) == 4
    assert test_bills[0].date == date(2020, 1, 1)
    assert test_bills[0].value == 100
    assert test_bills[0].descr == 'Sample_description_1'
    assert test_bills[0].user_name == 'scott'
    assert test_bills[0].category.name == 'category1'
    assert test_bills[3].value == 400
