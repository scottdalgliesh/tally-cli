from typing import List

from pick import pick

from .models import Bill, Category, get_session
from .parse import TransDict
from .users import get_active_user_name
from .utils import safe_commit


def categorize(trans_dict: TransDict, no_confirm: bool) -> str:
    '''Interactively categorize transactions.'''
    # get active user and category list
    session = get_session()
    active_user = get_active_user_name(session)
    categ_list = get_categs()

    # verify active user is correct prior to proceeding
    if not no_confirm:
        confirm_user = input(
            f'Please verify the active user is correct: "{active_user}" ([y]/n)')
        if not confirm_user.lower() in ['y', '']:
            return 'Process aborted during active user confirmation.'

    # interactively categorize each transaction
    new_bill_count = 0
    while trans_dict['Date']:
        trans = (
            f"Active User:{active_user}\n"
            f"Date:{trans_dict['Date'][0]}\n"
            f"Value:{trans_dict['Value'][0]}\n"
            f"Description: {trans_dict['Description'][0]}"
        )
        categ, _ = pick(categ_list, trans)
        new_bill = Bill(
            date=trans_dict['Date'].pop(0),
            descr=trans_dict['Description'].pop(0),
            value=trans_dict['Value'].pop(0),
            user_name = active_user,
            category_name=categ
        )
        session.add(new_bill)
        new_bill_count +=1
    safe_commit(session)
    return f'{new_bill_count} transactions added successfully.'


def get_categs() -> List[str]:
    '''Get all categories.'''
    session = get_session()
    categs = session.query(Category).all()
    if len(categs) == 0:
        return []
    else:
        return [categ.name for categ in categs]


def add_categ(categ_name: str) -> str:
    '''Add a new category.'''
    session = get_session()
    new_category = Category(name=categ_name)
    session.add(new_category)
    safe_commit(session)
    return f'Category {categ_name} added successfully.'


def update_categ(old_categ_name: str, new_categ_name: str) -> str:
    '''Modify an existing category's name.'''
    session = get_session()
    session.autoflush = False
    categ = session.query(Category).filter_by(name=old_categ_name).first()
    if categ is None:
        msg = f'Category "{old_categ_name}" does not exist. Please verify spelling.'
    else:
        categ.name = new_categ_name
        safe_commit(session)
        msg = f'User "{old_categ_name}" successfully updated to "{new_categ_name}".'
    return msg


def delete_categ(categ_name: str) -> str:
    """Delete an existing category."""
    session = get_session()
    session.autoflush = False
    categ = session.query(Category).filter_by(name=categ_name).first()
    if categ is None:
        msg = f'Category "{categ_name}" does not exist. Please verify spelling.'
    else:
        session.delete(categ)
        safe_commit(session)
        msg = f'Category "{categ_name}" successfully deleted.'
    return msg
