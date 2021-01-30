from typing import List

from pick import pick

from .models import Category, session
from .parse import TransDict
from .users import active_user_exists, get_active_user, get_active_user_name
from .utils import new_bill, safe_commit


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
    safe_commit()
    return f'{new_bill_count} transactions added successfully.'


def get_categs() -> List[str]:
    '''Get all categories.'''
    if not active_user_exists():
        return []
    categs = get_active_user().categories
    return [categ.name for categ in categs]  # type: ignore


def add_categ(categ_name: str) -> str:
    '''Add a new category.'''
    active_user_name = get_active_user_name()
    new_category = Category(name=categ_name, user_name=active_user_name)
    session.add(new_category)
    safe_commit()
    return f'Category {categ_name} added successfully.'


def update_categ(old_categ_name: str, new_categ_name: str) -> str:
    '''Modify an existing category's name.'''
    session.autoflush = False
    active_user_name = get_active_user_name()
    categ = session.query(Category).filter_by(name=old_categ_name,
                                              user_name=active_user_name).first()
    if categ is None:
        msg = f'Category "{old_categ_name}" does not exist. Please verify spelling.'
    else:
        categ.name = new_categ_name
        safe_commit()
        msg = f'User "{old_categ_name}" successfully updated to "{new_categ_name}".'
    return msg


def delete_categ(categ_name: str) -> str:
    """Delete an existing category."""
    session.autoflush = False
    active_user_name = get_active_user_name()
    categ = session.query(Category).filter_by(name=categ_name,
                                              user_name=active_user_name).first()
    if categ is None:
        msg = f'Category "{categ_name}" does not exist. Please verify spelling.'
    else:
        session.delete(categ)
        safe_commit()
        msg = f'Category "{categ_name}" successfully deleted.'
    return msg
