#pylint:disable=[missing-function-docstring, unused-argument]

from datetime import date

import pytest
from tally.categ import (TransDict, add_categ, categorize, delete_categ,
                         get_categs, update_categ)
from tally.models import Bill, Category, get_session

test_input = [
    pytest.param(add_categ, 'new_categ', None, ['groceries', 'gas', 'misc', 'new_categ'],
                 id='add_categ_valid'),
    pytest.param(add_categ, 'groceries', None, ['groceries', 'gas', 'misc'],
                 id='add_categ_duplicate'),
    pytest.param(update_categ, 'groceries', 'groceries2', ['groceries2', 'gas', 'misc'],
                 id='update_categ_valid'),
    pytest.param(update_categ, 'groceries', 'gas', ['groceries', 'gas', 'misc'],
                 id='update_categ_duplicate'),
    pytest.param(update_categ, 'non_existing', 'new', ['groceries', 'gas', 'misc'],
                 id='update_categ_non_existing'),
    pytest.param(delete_categ, 'groceries', None, ['gas', 'misc'],
                 id='delete_categ_valid'),
    pytest.param(delete_categ, 'non_existing', None, ['groceries', 'gas', 'misc'],
                 id='delete_categ_non_existing'),
]


@pytest.mark.parametrize('func,categ1,categ2,categ_list', test_input)
def test_user_operation(sample_db, mock_exit, func, categ1, categ2, categ_list):
    if func is update_categ:
        func(categ1, categ2)
    else:
        func(categ1)
    categs = sample_db.query(Category).all()
    categ_names = [categ.name for categ in categs]
    assert categ_names == categ_list


def test_get_categs(sample_db):
    test_categs = get_categs()
    assert test_categs == ['groceries', 'gas', 'misc']


def test_categorize(empty_db, mock_pick):
    trans_dict: TransDict = {
        'Date': [date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3), date(2020, 1, 4)],
        'Value': [100, 200, 300, 400],
        'Description': ['Sample_description_1', 'Sample_description_2',
                        'Sample_description_1', 'Sample_description_2']
    }
    test_msg = categorize(trans_dict, True)
    assert test_msg == '4 transactions added successfully.'

    session = get_session()
    test_bills = session.query(Bill).all()
    assert len(test_bills) == 4
    assert test_bills[0].date == date(2020, 1, 1)
    assert test_bills[0].value == 100
    assert test_bills[0].descr == 'Sample_description_1'
    assert test_bills[0].user_name == 'scott'
    assert test_bills[0].category_name == 'category1'
    assert test_bills[3].value == 400
