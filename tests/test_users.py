#pylint:disable=[missing-function-docstring, unused-argument]

import pytest

from tally.models import ActiveUser, User
from tally.users import active_user_exists, add_user, delete_user, set_active_user, update_user

test_input = [
    pytest.param(add_user, 'new_user', None, ['scott', 'sarah', 'new_user'],
                 id='add_user_valid'),
    pytest.param(add_user, 'scott', None, ['scott', 'sarah'],
                 id='add_user_duplicate'),
    pytest.param(update_user, 'scott', 'new_user', ['new_user', 'sarah'],
                 id='update_user_valid'),
    pytest.param(update_user, 'scott', 'sarah', ['scott', 'sarah'],
                 id='update_user_duplicate'),
    pytest.param(update_user, 'non_existing_user', 'sarah', ['scott', 'sarah'],
                 id='update_user_non_existing'),
    pytest.param(delete_user, 'scott', None, ['sarah'],
                 id='delete_user_valid'),
    pytest.param(delete_user, 'non_existing_user', None, ['scott', 'sarah'],
                 id='delete_user_non_existing'),
]


@pytest.mark.parametrize('func,user1,user2,users_list', test_input)
def test_user_operation(sample_db, mock_exit, func, user1, user2, users_list):
    if func is update_user:
        func(user1, user2)
    else:
        func(user1)
    users = sample_db.query(User).all()
    user_names = [user.name for user in users]
    assert user_names == users_list


test_input = [
    pytest.param('sarah', False, ['sarah'], id='valid'),
    pytest.param('scott', False, ['scott'], id='already_active_user'),
    pytest.param('non_existing_user', False, [
                 'scott'], id='non_existing_user'),
    pytest.param('scott', True, ['scott'], id='from_empty_table'),
]


@pytest.mark.parametrize('user_name,table_is_empty,active_user', test_input)
def test_update_active_user(sample_db, mock_exit, user_name, table_is_empty, active_user):
    if table_is_empty:
        current_active_user = sample_db.query(ActiveUser).first()
        sample_db.delete(current_active_user)
        sample_db.commit()
    exists = active_user_exists(sample_db)
    assert exists is not table_is_empty
    set_active_user(user_name)
    new_active_users = sample_db.query(ActiveUser).all()
    new_active_users_names = [
        active_user.name for active_user in new_active_users]
    assert new_active_users_names == active_user
