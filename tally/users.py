from typing import List

from .models import ActiveUser, User, session
from .utils import safe_commit


def get_users() -> List[str]:
    '''Get all users.'''
    users = session.query(User).all()
    if len(users) == 0:
        return []
    else:
        return [user.name for user in users]


def add_user(user_name: str) -> str:
    """Add a new user."""
    new_user = User(name=user_name)
    session.add(new_user)
    safe_commit()
    return f'User "{user_name}" added successfully.'


def update_user(old_user_name: str, new_user_name: str) -> str:
    """Modify an existing user's name."""
    session.autoflush = False
    user = session.query(User).filter_by(name=old_user_name).first()
    if user is None:
        msg = f'User "{old_user_name}" does not exist. Please verify spelling.'
    else:
        user.name = new_user_name
        safe_commit()
        msg = f'User "{old_user_name}" successfully updated to "{new_user_name}".'
    return msg


def delete_user(user_name: str) -> str:
    """Delete an existing user."""
    session.autoflush = False
    user = session.query(User).filter_by(name=user_name).first()
    if user is None:
        msg = f'User "{user_name}" does not exist. Please verify spelling.'
    else:
        session.delete(user)
        safe_commit()
        msg = f'User "{user_name}" successfully deleted.'
    return msg


def active_user_exists() -> bool:
    """Check for existance of active user."""
    return len(session.query(ActiveUser).all()) != 0


def get_active_user() -> User:
    """Get the active user."""
    return session.query(ActiveUser).first().user


def get_active_user_name() -> str:
    """Get name of the active user."""
    return session.query(ActiveUser).first().name


def set_active_user(user_name: str) -> str:
    """Set the active user."""
    session.autoflush = False
    msg = f'User "{user_name}" successfully set as active user.'
    if user_name not in get_users():
        msg = f'User "{user_name}" does not exist. Please verify spelling.'
    elif active_user_exists():
        active_user = session.query(ActiveUser).first()
        active_user.name = user_name
        safe_commit()
    else:
        active_user = ActiveUser(name=user_name)
        session.add(active_user)
        safe_commit()
    return msg
