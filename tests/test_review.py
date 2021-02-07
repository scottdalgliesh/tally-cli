#pylint:disable=[missing-function-docstring, unused-argument]

from math import isclose

import pandas as pd
from tally.review import TransData


def test_init(review_db):
    data = TransData('scott').data
    assert len(data) == 8
    assert data.columns.to_list() == ['Description', 'Value', 'Category']
    assert data.iloc[0].to_list() == ['Previous month', 1, 'misc']


def test_show_hidden(review_db):
    data = TransData('scott', show_hidden=True).data
    assert len(data) == 9
    assert data.iloc[0].to_list() == ['hidden', 100, 'sample_hidden']


def test_filter_first_and_last_month(review_db):
    # verify the data added to the previous and next month was filtered out
    trans_data = TransData('scott')
    trans_data.filter_first_and_last_month()
    data = trans_data.data
    assert len(data) == 6
    assert data.iloc[0].to_list() == ['Start of current month', 1.0, 'misc']
    assert data.iloc[-1].to_list() == ['End of current month', 1.0, 'misc']


def test_filter_by_category(sample_db):
    trans_data = TransData('scott')
    trans_data.filter_by_category('groceries')
    assert len(trans_data.data) == 2
    assert trans_data.data['Category'].unique() == 'groceries'


def test_summarize_all(review_db):
    # get transactions from db
    trans_data = TransData('scott')
    pivot = trans_data.summarize_all()

    # create expected result
    cols = ['Year', 'Month', 'misc', 'groceries', 'total']
    rows = [
        (2019, 'December', 1.0, 0.0, 1.0),
        (2020, 'January', 502.0, 500.0, 1002.0),
        (2020, 'February', 1.0, 0.0, 1.0),
        ('Average', '', 504/3, 500/3, 1004/3),
    ]
    test_df = pd.DataFrame(rows, columns=cols)
    test_df.set_index(['Year', 'Month'], inplace=True)

    # comapre # rows, columns and index
    assert len(pivot) == len(test_df)
    assert list(pivot.columns) == list(test_df.columns)
    assert all(pivot.index == test_df.index)

    # compare rows
    for ind in range(len(pivot)-1):
        assert pivot.iloc[ind].to_list() == test_df.iloc[ind].to_list()
    for ind in range(3):
        assert isclose(pivot.iloc[-1, ind], test_df.iloc[-1, ind])
