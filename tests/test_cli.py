#pylint:disable=[missing-function-docstring, unused-argument]
from datetime import date
from typing import Dict

import pytest
from click.testing import CliRunner

from tally import categ, parse, users
from tally.cli import cli
from tally.models import Bill, User, get_session
from tally.review import TransData
from .test_parse import sample1

MSG_USER_NO_OPTIONS = (
    '''
List of Users:
--------------
*scott
sarah

'''.lstrip('\n')
)

test_input = [
    pytest.param(['user'], ['scott', 'sarah'],
                 MSG_USER_NO_OPTIONS, id='no args'),
    pytest.param(['user', '-a', 'delta', '-u', 'delta', 'sam'],
                 ['scott', 'sarah'], None, id='too many options'),
    pytest.param(['user', '-a', 'delta'],
                 ['scott', 'sarah', 'delta'], None, id='add: valid'),
    pytest.param(['user', '-a', 'scott'],
                 ['scott', 'sarah'], None, id='add: dup'),
    pytest.param(['user', '-u', 'scott', 'new_scott'],
                 ['new_scott', 'sarah'], None, id='update: valid'),
    pytest.param(['user', '-u', 'scott'],
                 ['scott', 'sarah'], None, id='update: missing second arg'),
    pytest.param(['user', '-u', 'scott', 'sarah'],
                 ['scott', 'sarah'], None, id='update: duplicate'),
    pytest.param(['user', '-u', 'invalid', 'delta'],
                 ['scott', 'sarah'], None, id='update: does not exist'),
    pytest.param(['user', '-d', 'scott', '--confirm'],
                 ['sarah'], None, id='delete: valid'),
    pytest.param(['user', '-d', 'scott'],
                 ['scott', 'sarah'], None, id='delete: missing confirm'),
    pytest.param(['user', '-d', 'delta'],
                 ['scott', 'sarah'], None, id='delete: does not exist'),
]


@pytest.mark.parametrize('cli_input,user_list,output_msg', test_input)
def test_user_general_operations(sample_db, cli_input, user_list, output_msg):
    runner = CliRunner()
    result = runner.invoke(cli, cli_input)
    if output_msg:
        assert result.output == output_msg
    test_users = users.get_users()
    assert test_users == user_list


test_input = [
    pytest.param(['user', '-s', 'sarah'], None, '*sarah', id='valid'),
    pytest.param(['user', '-s', 'delta'], None,
                 '*scott', id='non-existing user'),
    pytest.param(['user', '-s', 'scott'], ['scott', 'sarah'],
                 'No users exist', id='empty table'),
    pytest.param(['user', '-s', 'sarah'], ['scott'],
                 '*sarah', id='from no active user'),
]


@pytest.mark.parametrize('cli_input,delete_users,partial_message', test_input)
def test_user_set_active(sample_db, cli_input, delete_users, partial_message):
    runner = CliRunner()
    if delete_users:
        for user_name in delete_users:
            sample_db.query(User).filter_by(name=user_name).delete()
        sample_db.commit()
    runner.invoke(cli, cli_input)
    result = runner.invoke(cli, ['user'])
    assert partial_message in result.output


MSG_CATEG_NO_OPTIONS = (
    '''
List of Categories:
-------------------
groceries
gas
misc

'''.lstrip('\n')
)

test_input = [
    pytest.param(['categ'], ['groceries', 'gas', 'misc'],
                 MSG_CATEG_NO_OPTIONS, id='no args'),
    pytest.param('categ -a new -u groceries groceries2'.split(), ['groceries', 'gas', 'misc'],
                 None, id='too many options'),
    pytest.param('categ -a new'.split(), ['groceries', 'gas', 'misc', 'new'],
                 None, id='add valid'),
    pytest.param('categ -a groceries'.split(), ['groceries', 'gas', 'misc'],
                 None, id='add duplicate'),
    pytest.param('categ -u groceries groc2'.split(), ['groc2', 'gas', 'misc'],
                 None, id='update valid'),
    pytest.param('categ -u groceries'.split(), ['groceries', 'gas', 'misc'],
                 None, id='update missing second arg'),
    pytest.param('categ -u groceries gas'.split(), ['groceries', 'gas', 'misc'],
                 None, id='update duplicate'),
    pytest.param('categ -u new1 new2'.split(), ['groceries', 'gas', 'misc'],
                 None, id='update does not exist'),
    pytest.param('categ -d groceries --confirm'.split(), ['gas', 'misc'],
                 None, id='delete valid'),
    pytest.param('categ -d groceries'.split(), ['groceries', 'gas', 'misc'],
                 None, id='delete no confirm'),
    pytest.param('categ -d new --confirm'.split(), ['groceries', 'gas', 'misc'],
                 None, id='delete non-existing'),
]


@pytest.mark.parametrize('cli_input,categ_list,output_msg', test_input)
def test_categ_operations(sample_db, cli_input, categ_list, output_msg):
    runner = CliRunner()
    result = runner.invoke(cli, cli_input)
    if output_msg:
        assert result.output == output_msg
    test_categs = categ.get_categs()
    assert test_categs == categ_list


def test_parse(empty_db, monkeypatch, mock_pick):
    # mock the tika parser
    statement_text = sample1['statement_text']

    class MockTika:
        '''Mock Tika.parser response'''
        @staticmethod
        def from_file(url: str) -> Dict[str, str]:
            return {'content': statement_text}
    monkeypatch.setattr(parse, 'parser', MockTika)

    # run parse on sample input with user categorization (pick) mocked
    runner = CliRunner()
    result = runner.invoke(cli, f'parse --no_confirm {sample1["url"]}'.split())
    assert result.output == '7 transactions added successfully.\n'

    # verify database integrity after testing
    session = get_session()
    test_bills = session.query(Bill).all()
    assert len(test_bills) == 7
    assert test_bills[0].date == date(2019, 3, 22)
    assert test_bills[0].value == 44.71
    assert test_bills[0].descr == 'TIM HORTONS TORONTO ON'
    assert test_bills[0].user_name == 'scott'
    assert test_bills[0].category_name == 'category2'
    assert test_bills[6].value == 43.79


def test_review(review_db):
    cli_input = 'review'
    runner = CliRunner()
    result = runner.invoke(cli, cli_input)
    sample_df = TransData('scott').summarize_all()
    assert str(sample_df) in result.output


def test_review_filter_edges(review_db):
    cli_input = 'review --filter_edges'
    runner = CliRunner()
    result = runner.invoke(cli, cli_input)
    sample_df = TransData('scott')
    sample_df.filter_first_and_last_month()
    sample_df = sample_df.summarize_all()
    assert str(sample_df) in result.output


def test_review_filter_by_category(review_db):
    cli_input = 'review -c groceries'
    runner = CliRunner()
    result = runner.invoke(cli, cli_input)
    sample_df = TransData('scott')
    sample_df.filter_by_category('groceries')
    assert str(sample_df.data) in result.output
