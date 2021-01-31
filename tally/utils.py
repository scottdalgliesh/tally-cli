import functools
from datetime import date as date_obj
from typing import Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from .models import Bill, Category, session
from .users import active_user_exists


def handle_db_session(func: Callable) -> Callable:
    """Handle database exceptions for the decorated function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except IntegrityError as int_err:
            session.rollback()
            if 'unique' in int_err.orig.args[0].lower():
                print('Entry is not unique. Please verify it is not a duplicate.')
            else:
                print('Database error, operation aborted. See error message '
                      f'below for details.\n {int_err.orig.args}')
        except NoResultFound:
            print('No result found which matches input. Please verify spelling.')
        return result
    return wrapper


def require_active_user(func: Callable) -> Callable:
    """Require active user to be set to execute the decorated function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if active_user_exists():
            result = func(*args, **kwargs)
        else:
            print('Aborted. Active user must be set to execute this command.\n'
                  'See command "user -s" to set the active user.')
            result = None
        return result
    return wrapper


def new_bill(date: date_obj, descr: str, value: float,
             user_name: str, category_name: str) -> Bill:
    """Define a new bill by category_name, rather than category_id"""
    category = session.query(Category).filter_by(
        user_name=user_name, name=category_name).one()
    return Bill(date=date, descr=descr, value=value,  # type:ignore
                user_name=user_name, category_id=category.id)
