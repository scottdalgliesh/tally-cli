# pylint:disable=[missing-function-docstring, unused-argument]

import copy
from datetime import date
from typing import Dict

import pytest

from tally import parse
from tally.parse import get_statement_dates, get_transactions, parse_statement

trans_dict1 = {
    'Date': [date(2019, 3, 22), date(2019, 3, 23), date(2019, 4, 1),
             date(2019, 3, 23), date(2019, 3, 27), date(2019, 4, 10),
             date(2019, 4, 12)],
    'Description': ['TIM HORTONS TORONTO ON', 'PETROCAN TORONTO ON',
                    'PAYMENT - THANK YOU / PAIEMENT - MERCI', 'CANADIAN TIRE TORONTO ON',
                    'REN\'S PET DEPOT TORONTO ON', 'GREASY PIZZA PLACE TORONTO ON',
                    'SHELL TORONTO ON'],
    'Value': [44.71, 16.27, -143.66, 28.56, 34.94, 25.03, 43.79]
}

trans_dict2 = copy.deepcopy(trans_dict1)
trans_dict2['Date'] = [date(2019, 12, 20), date(2019, 12, 23), date(2020, 1, 1),
                       date(2019, 12, 28), date(2020, 1, 5), date(2020, 1, 6),
                       date(2020, 1, 10)]

sample1 = {
    'url': 'tests/data/sample_statement_text1.txt',
    'start_date': date(2019, 3, 20),
    'end_date': date(2019, 4, 22),
    'trans_dict': trans_dict1
}
with open(str(sample1['url'])) as file:
    sample1['statement_text'] = file.read()

sample2 = {
    'url': 'tests/data/sample_statement_text2.txt',
    'start_date': date(2019, 12, 20),
    'end_date': date(2020, 1, 20),
    'trans_dict': trans_dict2
}
with open(str(sample2['url'])) as file:
    sample2['statement_text'] = file.read()


test_input = [
    pytest.param(sample1['statement_text'], sample1['start_date'], sample1['end_date'],
                 id='mid-year'),
    pytest.param(sample2['statement_text'], sample2['start_date'], sample2['end_date'],
                 id='transition')
]


@pytest.mark.parametrize('statement_text,start_date,end_date', test_input)
def test_get_statement_dates(statement_text, start_date, end_date):
    test_start_date, test_end_date = get_statement_dates(statement_text)
    assert test_start_date == start_date
    assert test_end_date == end_date


test_input = [
    pytest.param(sample1['statement_text'], sample1['start_date'], sample1['end_date'],
                 sample1['trans_dict'], id='mid-year'),
    pytest.param(sample2['statement_text'], sample2['start_date'], sample2['end_date'],
                 sample2['trans_dict'], id='transition')
]


@pytest.mark.parametrize('statement_text,start_date,end_date,trans_dict', test_input)
def test_get_transactions(statement_text, start_date, end_date, trans_dict):
    test_trans_dict = get_transactions(statement_text, start_date, end_date)
    assert test_trans_dict == trans_dict


test_input = [
    pytest.param(sample1['url'],
                 sample1['statement_text'], sample1['trans_dict'], id='mid-year'),
    pytest.param(sample2['url'], sample2['statement_text'],
                 sample2['trans_dict'], id='transition')
]

@pytest.mark.parametrize('statement_url,statement_text, trans_dict', test_input)
def test_parse_statement(monkeypatch, statement_url, statement_text, trans_dict):
    class MockTika:
        '''Mock Tika.parser response'''
        @staticmethod
        def from_file(url: str) -> Dict[str, str]:
            return {'content': statement_text}

    monkeypatch.setattr(parse, 'parser', MockTika)
    test_trans_dict = parse_statement(statement_url)
    assert test_trans_dict == trans_dict
