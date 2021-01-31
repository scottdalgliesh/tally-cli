#pylint:disable=[missing-function-docstring, unused-argument]
from contextlib import nullcontext

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from tally.models import ActiveUser, User, session
from tally.users import add_user, delete_user, set_active_user, update_user

test_input = [
    pytest.param(add_user, 'new_user', None, ['scott', 'sarah', 'new_user'],
                 nullcontext(), id='add_user_valid'),
    pytest.param(add_user, 'scott', None, ['scott', 'sarah'],
                 pytest.raises(IntegrityError), id='add_user_duplicate'),
    pytest.param(update_user, 'scott', 'new_user', ['new_user', 'sarah'],
                 nullcontext(), id='update_user_valid'),
    pytest.param(update_user, 'scott', 'sarah', ['scott', 'sarah'],
                 pytest.raises(IntegrityError), id='update_user_duplicate'),
    pytest.param(update_user, 'non_existing_user', 'sarah', ['scott', 'sarah'],
                 pytest.raises(NoResultFound), id='update_user_non_existing'),
    pytest.param(delete_user, 'scott', None, ['sarah'],
                 nullcontext(), id='delete_user_valid'),
    pytest.param(delete_user, 'non_existing_user', None, ['scott', 'sarah'],
                 pytest.raises(NoResultFound), id='delete_user_non_existing'),
]


@pytest.mark.parametrize('func,user1,user2,users_list,context', test_input)
def test_user_operation(sample_db, func, user1, user2, users_list, context):
    with context:
        if func is update_user:
            func(user1, user2)
        else:
            func(user1)
    if not context is nullcontext():
        session.rollback()
    users = session.query(User).all()
    user_names = [user.name for user in users]
    assert user_names == users_list


test_input = [
    pytest.param('sarah', False, 'sarah', nullcontext(), id='valid'),
    pytest.param('scott', False, 'scott',
                 nullcontext(), id='already_active_user'),
    pytest.param('non_existing_user', False, 'scott',
                 pytest.raises(NoResultFound), id='non_existing_user'),
    pytest.param('scott', True, 'scott',
                 nullcontext(), id='from_empty_table'),
]


@pytest.mark.parametrize('user_name,table_is_empty,active_user, context', test_input)
def test_update_active_user(sample_db, user_name, table_is_empty, active_user, context):
    if table_is_empty:
        current_active_user = session.query(ActiveUser).first()
        session.delete(current_active_user)
        session.commit()
    with context:
        set_active_user(user_name)
    if not context is nullcontext():
        session.rollback()
    new_active_users = session.query(ActiveUser).one()
    assert new_active_users.name == active_user
