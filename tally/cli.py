from typing import Tuple

import click

from . import categ as _categ
from . import parse as _parse
from . import users
from .config import DB_URL
from .models import init_db
from .review import TransData
from .utils import handle_db_session, require_active_user


@click.group()
def cli():
    """Parse, categorize and summarize expense data from RBC credit card statements."""
    if not DB_URL.exists():
        print('First time setup: initializing database...', end='')
        init_db()
        print('done')


@cli.group()
def user():
    """Manage users & set the active user."""
    pass


@user.command(name='list')
def list_users():
    """List all users. The active user is denoted by an asterisk."""
    user_names = users.get_users()
    if len(user_names) == 0:
        print('No users exist yet. See option "user add" to create a new user.')
        return None
    title = 'List of Users:'
    msg = '\n'.join([title, '-'*len(title), *user_names])
    if users.active_user_exists():
        active_user = users.get_active_user_name()
        index = msg.find(active_user)
        msg = msg[:index] + '*' + msg[index:]
    else:
        msg = msg + ('\n\n*No active user set.\nSee command '
                     '"user active" to set the active user.')
    print(msg)


@user.command(name='add')
@click.argument('user_names', nargs=-1)
@click.option('-s', '--set_active', is_flag=True, help='Set new user as active.')
@handle_db_session
def add_user(user_names: Tuple[str], set_active: bool):
    """Add one or more users."""
    for user_name in user_names:
        msg = users.add_user(user_name)
        print(msg)
    if set_active:
        users.set_active_user(user_names[0])


@user.command('update')
@click.argument('old_user_name')
@click.argument('new_user_name')
@handle_db_session
def update_user(old_user_name: str, new_user_name: str):
    """Update a user's name."""
    msg = users.update_user(old_user_name, new_user_name)
    print(msg)


@user.command('delete')
@click.argument('user_names', nargs=-1)
@click.confirmation_option(
    prompt='Are you sure you want to delete the specified user(s)?')
@handle_db_session
def delete_user(user_names: Tuple[str]):
    """Delete one or more users."""
    for user_name in user_names:
        msg = users.delete_user(user_name)
        print(msg)


@user.command()
@click.argument('user_name')
@handle_db_session
def active(user_name: str):
    """Set the active user."""
    msg = users.set_active_user(user_name)
    print(msg)


@cli.group()
def categ():
    """Manage categories for the active user."""
    pass


@categ.command(name='list')
@require_active_user
@handle_db_session
def list_categs():
    """List all categories for the active user."""
    categ_names = _categ.get_categs()
    if len(categ_names) == 0:
        msg = ('No categories exist yet. See command "categ add" to create '
               'a new category.')
    else:
        title = 'List of Categories:'
        msg = '\n'.join([title, '-'*len(title)]) + '\n'
        for categ_name in categ_names:
            msg += categ_name
            if _categ.is_hidden(categ_name):
                msg += ' (hidden)'
            msg += '\n'
    print(msg)


@categ.command(name='add')
@click.argument('categ_names', nargs=-1)
@click.option('-h', '--hidden', is_flag=True,
              help='Hide category in summary outputs.')
@require_active_user
@handle_db_session
def add_categ(categ_names: Tuple[str], hidden: bool = False):
    """Add one or more categories."""
    for categ_name in categ_names:
        msg = _categ.add_categ(categ_name, hidden)
        print(msg)


@categ.command('update')
@click.argument('old_categ_name')
@click.argument('new_categ_name')
@require_active_user
@handle_db_session
def update_categ(old_categ_name: str, new_categ_name: str):
    """Update a category's name."""
    msg = _categ.update_categ(old_categ_name, new_categ_name)
    print(msg)


@categ.command(name='show')
@click.argument('categ_names', nargs=-1)
@require_active_user
@handle_db_session
def show_categ(categ_names: Tuple[str]):
    """Enable display of one or more categories in summary outputs."""
    for categ_name in categ_names:
        msg = _categ.set_categ_display(categ_name, False)
        print(msg)


@categ.command(name='hide')
@click.argument('categ_names', nargs=-1)
@require_active_user
@handle_db_session
def hide_categ(categ_names: Tuple[str]):
    """Disable display of one or more categories in summary outputs."""
    for categ_name in categ_names:
        msg = _categ.set_categ_display(categ_name, True)
        print(msg)


@categ.command('delete')
@click.argument('categ_names', nargs=-1)
@click.confirmation_option(
    prompt='Are you sure you want to delete the specified category(ies)?')
@require_active_user
@handle_db_session
def delete_categ(categ_names: Tuple[str]):
    """Delete one or more categories."""
    for categ_name in categ_names:
        msg = _categ.delete_categ(categ_name)
        print(msg)


@cli.command()
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False))
@click.option('--no_confirm', is_flag=True,
              help='Do not require active user confirmation.')
@require_active_user
@handle_db_session
def parse(filepath: str, no_confirm: bool):
    '''Parse & categorize a pdf statement.'''
    trans_dict = _parse.parse_statement(filepath)
    msg = _categ.categorize(trans_dict, no_confirm)
    print(msg)


@cli.command()
@click.option('-f', '--filter_edges', is_flag=True,
              help='Filter out first and last month\'s data (which may be incomplete).')
@click.option('-s', '--show_hidden', is_flag=True,
              help='Show hidden categories in output.')
@click.option('-c', '--category', help='List transactions for specified category.',
              type=click.STRING)
@require_active_user
def review(filter_edges: bool, category: str, show_hidden: bool):
    """Review transaction data for the active user."""
    # get active user data
    active_user = users.get_active_user_name()
    trans_data = TransData(active_user, show_hidden=show_hidden)

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
