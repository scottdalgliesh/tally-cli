#pylint:disable=[missing-function-docstring, unused-argument]

from click.testing import CliRunner
import pytest

from tally import users
from tally.cli import cli
from tally.models import User

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
