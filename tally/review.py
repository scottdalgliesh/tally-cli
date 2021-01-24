from copy import deepcopy
from datetime import date
import pandas as pd

from .models import get_engine, get_session, Category


# set pandas global display options
pd.options.display.max_rows = 10_000
pd.options.display.max_columns = 100
pd.options.display.width = 250
pd.options.display.precision = 2


class TransData():
    '''
    A class used to retrieve and manipulate transaction data for the specified user.

    Attributes
    ----------
    data : pd.DataFrame
        A pandas DataFrame containing transaction data

    Methods
    -------
    filter_by_category(category: str)
        Filter out all data which does not match the specified category.
    filter_first_and_last_month()
        Filter out data from the first and last month on record, which may be incomplete.
    summarize_all()
        Returns a pivot table summary by month and category.

    '''

    def __init__(self, user_name: str):
        '''Retrieve all data for the specified user and store as a DataFrame, indexed by date.'''
        # get bill data for specified user
        engine = get_engine()
        user_data = pd.read_sql('bills', engine, index_col='date', parse_dates='date',
                                columns=['date', 'descr', 'value', 'user_name', 'category_id'])
        user_data = user_data.sort_index()
        user_filt = user_data['user_name'] == user_name
        user_data = user_data[user_filt]

        # convert category_id to category name
        session = get_session()
        user_categs = session.query(Category).\
            filter_by(user_name=user_name).all()
        categ_map = {categ.id: categ.name for categ in user_categs}
        user_data['Category'] = user_data['category_id'].\
            apply(lambda x: categ_map[x])

        # drop unnecessary columns and rename columns
        user_data.drop(columns=['user_name', 'category_id'], inplace=True)
        user_data.rename(columns={'descr': 'Description', 'value': 'Value'},
                         inplace=True)
        user_data.index.rename('Date', inplace=True)
        self.data = user_data

    def filter_first_and_last_month(self):
        '''Filter out data from the first and last month on record, which may be incomplete.'''
        start = self.data.index[0] + pd.offsets.MonthBegin(1)
        end = self.data.index[-1] - pd.offsets.MonthEnd(1)
        if start > end:
            raise ValueError('Error during data filtering. Insufficient data exists '
                             'to filter out (potentially incomplete) first and last month data.')
        filt_start = self.data.index >= start
        filt_end = self.data.index <= end
        self.data = self.data[filt_start & filt_end]

    def filter_by_category(self, category: str):
        '''Filter out all data which does not match the specified category.'''
        filt = self.data['Category'] == category
        self.data = self.data[filt]

    def summarize_all(self) -> pd.DataFrame:
        '''Return a pivot table summary by month and category.'''
        # create pivot table, sorted by year then month
        data = deepcopy(self.data)
        data['Month'] = data.index.to_series().map(
            lambda row: row.strftime('%B'))
        data['Year'] = data.index.to_series().map(lambda row: row.year)
        months = {date(1, month, 1).strftime('%B'): month
                  for month in range(1, 13)}
        pivot = pd.pivot_table(data, values='Value', columns='Category',
                               aggfunc='sum', fill_value=0, index=['Year', 'Month'])
        pivot.sort_index(level=1, key=lambda rows: sorted(
            rows, key=lambda row: months[row]), inplace=True)
        pivot.sort_index(level=0, inplace=True, sort_remaining=False)

        # add category averages and month totals
        pivot.loc[('Average', ''), :] = pivot.mean(axis=0)
        pivot = pivot.sort_values(by=pivot.index[-1], axis=1, ascending=False)
        pivot['total'] = pivot.sum(1)
        return pivot
