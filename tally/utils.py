import sys

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

def safe_commit(session: Session) -> None:
    """If required, catch commit exceptions, rollback transaction, then exit."""
    try:
        session.commit()
    except IntegrityError as err:
        session.rollback()
        print(f'Error, operation not completed. See error message below '
              f'for details.\n{err.orig.args}')
        sys.exit()
