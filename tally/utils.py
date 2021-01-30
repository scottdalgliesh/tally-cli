import sys
from datetime import date as date_obj

from sqlalchemy.exc import IntegrityError

from .models import Bill, Category, session


def safe_commit() -> None:
    """If required, catch commit exceptions, rollback transaction, then exit."""
    try:
        session.commit()
    except IntegrityError as err:
        session.rollback()
        print(f'Error, operation not completed. See error message below '
              f'for details.\n{err.orig.args}')
        sys.exit()


def new_bill(date: date_obj, descr: str, value: float,
             user_name: str, category_name: str) -> Bill:
    """Define a new bill by category_name, rather than category_id"""
    category = session.query(Category).filter_by(
        user_name=user_name, name=category_name).one()
    return Bill(date=date, descr=descr, value=value,  # type:ignore
                user_name=user_name, category_id=category.id)
