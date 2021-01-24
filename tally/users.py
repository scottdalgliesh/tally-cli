from typing import List

from sqlalchemy.orm.session import Session

from .models import ActiveUser, User, get_session
from .utils import safe_commit


def get_users() -> List[str]:
    '''Get all users.'''
    session = get_session()
    users = session.query(User).all()
    if len(users) == 0:
        return []
    else:
        return [user.name for user in users]


def add_user(user_name: str) -> str:
    """Add a new user."""
    session = get_session()
    new_user = User(name=user_name)
    session.add(new_user)
    safe_commit(session)
    return f'User "{user_name}" added successfully.'


def update_user(old_user_name: str, new_user_name: str) -> str:
    """Modify an existing user's name."""
    session = get_session()
    session.autoflush = False
    user = session.query(User).filter_by(name=old_user_name).first()
    if user is None:
        msg = f'User "{old_user_name}" does not exist. Please verify spelling.'
    else:
        user.name = new_user_name
        safe_commit(session)
        msg = f'User "{old_user_name}" successfully updated to "{new_user_name}".'
    return msg


def delete_user(user_name: str) -> str:
    """Delete an existing user."""
    session = get_session()
    session.autoflush = False
    user = session.query(User).filter_by(name=user_name).first()
    if user is None:
        msg = f'User "{user_name}" does not exist. Please verify spelling.'
    else:
        session.delete(user)
        safe_commit(session)
        msg = f'User "{user_name}" successfully deleted.'
    return msg


def active_user_exists(session: Session) -> bool:
    """Check for existance of active user."""
    return len(session.query(ActiveUser).all()) != 0


def get_active_user(session: Session) -> User:
    """Get the active user."""
    return session.query(ActiveUser).first().user


def get_active_user_name(session: Session) -> str:
    """Get name of the active user."""
    return session.query(ActiveUser).first().name


def set_active_user(user_name: str) -> str:
    """Set the active user."""
    session = get_session()
    session.autoflush = False
    msg = f'User "{user_name}" successfully set as active user.'
    if user_name not in get_users():
        msg = f'User "{user_name}" does not exist. Please verify spelling.'
    elif active_user_exists(session):
        active_user = session.query(ActiveUser).first()
        active_user.name = user_name
        safe_commit(session)
    else:
        active_user = ActiveUser(name=user_name)
        session.add(active_user)
        safe_commit(session)
    return msg
