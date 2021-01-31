from typing import List

from .models import ActiveUser, User, session


def get_users() -> List[str]:
    '''Get all users.'''
    users = session.query(User).all()
    return [user.name for user in users]


def add_user(user_name: str) -> str:
    """Add a new user."""
    new_user = User(name=user_name)
    session.add(new_user)
    session.commit()
    return f'User "{user_name}" added successfully.'


def update_user(old_user_name: str, new_user_name: str) -> str:
    """Modify an existing user's name."""
    user = session.query(User).filter_by(name=old_user_name).one()
    user.name = new_user_name
    session.commit()
    return f'User "{old_user_name}" successfully updated to "{new_user_name}".'


def delete_user(user_name: str) -> str:
    """Delete an existing user."""
    user = session.query(User).filter_by(name=user_name).one()
    session.delete(user)
    session.commit()
    return f'User "{user_name}" successfully deleted.'


def active_user_exists() -> bool:
    """Check for existance of active user."""
    return session.query(ActiveUser).count() != 0


def get_active_user() -> User:
    """Get the active user."""
    return session.query(ActiveUser).one().user


def get_active_user_name() -> str:
    """Get name of the active user."""
    return session.query(ActiveUser).one().name


def set_active_user(user_name: str) -> str:
    """Set the active user."""
    session.query(User).filter_by(name=user_name).one()
    if active_user_exists():
        active_user = session.query(ActiveUser).one()
        active_user.name = user_name
    else:
        active_user = ActiveUser(name=user_name)
        session.add(active_user)
    session.commit()
    return f'User "{user_name}" successfully set as active user.'
