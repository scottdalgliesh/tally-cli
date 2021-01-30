import click

from . import categ as _categ
from . import parse as _parse
from . import users
from .review import TransData


@click.group()
def cli():
    """Parse, categorize and summarize expense data from RBC credit card statements."""
    pass


@cli.command()
@click.option('-a', '--add', help='Add a new user.', type=str)
@click.option('-u', '--update', help='Update an existing user.',
              nargs=2, type=str)
@click.option('-d', '--delete', help='Delete a user.',
              type=click.STRING)
@click.option('-s', '--set_active', help='Set the active user.',
              type=click.STRING)
@ click.option('--confirm', is_flag=True, help='Confirm delete action.')
def user(add: str, update: str, delete: str, set_active: str, confirm: bool):
    """Manage users & set active user. Issue without options to list users."""
    # validate only a single option is used
    active_options = [option for option in [add, update, delete, set_active]
                      if option not in [None, ()]]
    if len(active_options) > 1:
        msg = 'Invalid entry. Only a single option can be used at once.'

    # if no options entered, list users
    elif len(active_options) == 0:
        user_names = users.get_users()
        if len(user_names) == 0:
            msg = 'No users exist yet. See option "-a" to create a new user.'
        else:
            title = 'List of Users:'
            msg = '\n'.join([title, '-'*len(title), *user_names])

        # add '*' to active user, or note if no active user exists
        if users.active_user_exists():
            active_user = users.get_active_user_name()
            index = msg.find(active_user)
            msg = msg[:index] + '*' + msg[index:]
        else:
            msg = msg + ('\n\n*No active user set.\nSee option '
                         '"-s" to set the active user.')

    # option-directed function calls
    elif add is not None:
        msg = users.add_user(add)
    elif update != ():
        msg = users.update_user(*update)
    elif delete is not None:
        if confirm:
            msg = users.delete_user(delete)
        else:
            msg = (f'Are you sure you want to delete user "{delete}"?\n'
                   'Issue command with "--confirm" to complete operation.')
    elif set_active is not None:
        msg = users.set_active_user(set_active)
    else:
        msg = 'Internal error. No actions taken.'
    print(msg, '\n', sep='')


@cli.command()
@click.option('-a', '--add', help='Add a new category.', type=str)
@click.option('-u', '--update', help='Update an existing category.',
              nargs=2, type=str)
@click.option('-d', '--delete', help='Delete a category.',
              type=click.STRING)
@click.option('--confirm', is_flag=True, help='Confirm delete action.')
def categ(add: str, update: str, delete: str, confirm: bool):
    """Manage categories. Issue without options to list active user categories."""
    # validate only a single option is used
    active_options = [option for option in [add, update, delete]
                      if option not in [None, ()]]
    if len(active_options) > 1:
        msg = 'Invalid entry. Only a single option can be used at once.'

    # validate that active user is set
    elif not users.active_user_exists():
        msg = 'Active user is not set. See command "user -s"'

    # if no options entered, list users
    elif len(active_options) == 0:
        categ_names = _categ.get_categs()
        if len(categ_names) == 0:
            msg = 'No categories exist yet. See option "-a" to create a new category.'
        else:
            title = 'List of Categories:'
            msg = '\n'.join([title, '-'*len(title), *categ_names])

    # option-directed function calls
    elif add is not None:
        msg = _categ.add_categ(add)
    elif update != ():
        msg = _categ.update_categ(*update)
    elif delete is not None:
        if confirm:
            msg = _categ.delete_categ(delete)
        else:
            msg = (f'Are you sure you want to delete categpru "{delete}"?\n'
                   'Issue command with "--confirm" to complete operation.')
    else:
        msg = 'Internal error. No actions taken.'
    print(msg, '\n', sep='')


@cli.command()
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False))
@click.option('--no_confirm', is_flag=True,
              help='Do not require active user confirmation.')
def parse(filepath: str, no_confirm: bool):
    '''Parse & categorize a pdf statement.'''
    trans_dict = _parse.parse_statement(filepath)
    msg = _categ.categorize(trans_dict, no_confirm)
    print(msg)


@cli.command()
@click.option('-f', '--filter_edges', is_flag=True,
              help='Filter out first and last month\'s data (which may be incomplete).')
@click.option('-c', '--category', help='List transactions for specified category.',
              type=click.STRING)
def review(filter_edges: bool, category: str):
    """Review transaction data for the active user."""
    # validate active user exists
    if not users.active_user_exists():
        print('Active user is not set. See command "user -s"', '\n')
        return

    # get active user data
    active_user = users.get_active_user_name()
    trans_data = TransData(active_user)

    # filter first and last month's data if applicable
    if filter_edges:
        try:
            trans_data.filter_first_and_last_month()
        except ValueError as v_err:
            print(f'{v_err} Try re-issueing without the "--filter_edges" option.\n')
            return

    # generate review output
    if category:
        trans_data.filter_by_category(category)
        msg = f'Transaction list for category "{category}":\n{trans_data.data}'
    else:
        msg = f'Monthly spending summary:\n{trans_data.summarize_all()}'
    print(msg, '\n', sep='')
