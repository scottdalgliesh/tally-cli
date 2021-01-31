from typing import List

from pick import pick

from .models import Category, session
from .parse import TransDict
from .users import get_active_user, get_active_user_name
from .utils import new_bill


def categorize(trans_dict: TransDict, no_confirm: bool) -> str:
    '''Interactively categorize transactions.'''
    # get active user and category list
    active_user = get_active_user_name()
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
        bill = new_bill(
            date=trans_dict['Date'].pop(0),
            descr=trans_dict['Description'].pop(0),
            value=trans_dict['Value'].pop(0),
            user_name=active_user,
            category_name=categ
        )
        session.add(bill)
        new_bill_count += 1
    session.commit()
    return f'{new_bill_count} transactions added successfully.'


def get_categs() -> List[str]:
    '''Get all categories for the active user.'''
    categs = get_active_user().categories
    return [categ.name for categ in categs]  # type: ignore


def add_categ(categ_name: str) -> str:
    '''Add a new category for the active user.'''
    new_category = Category(name=categ_name, user_name=get_active_user_name())
    session.add(new_category)
    session.commit()
    return f'Category {categ_name} added successfully.'


def update_categ(old_categ_name: str, new_categ_name: str) -> str:
    '''Modify an existing category's name for the active user.'''
    categ = session.query(Category).filter_by(
        name=old_categ_name, user_name=get_active_user_name()).one()
    categ.name = new_categ_name
    session.commit()
    return (f'Category "{old_categ_name}" successfully updated '
            f'to "{new_categ_name}".')


def delete_categ(categ_name: str) -> str:
    """Delete an existing category for the active user."""
    categ = session.query(Category).filter_by(
        name=categ_name, user_name=get_active_user_name()).one()
    session.delete(categ)
    session.commit()
    return f'Category "{categ_name}" successfully deleted.'
