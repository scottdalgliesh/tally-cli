import click

from . import users


@click.group()
def cli():
    """Parse, categorize and summarize expense data from RBC credit card statements."""
    pass


@cli.command()
@click.option('-a', '--add', help='Add a new user.', type=str)
@click.option('-u', '--update', help='Update an existing user.',
              nargs=2, type=str)
@click.option('-d', '--delete', help='Delete a user.',
              type=click.Choice(users.get_users()))
@click.option('-s', '--set_active', help='Set the active user.',
              type=click.Choice(users.get_users()))
@click.option('--confirm', is_flag=True, help='Confirm delete action.')
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
        session = users.get_session()
        if users.active_user_exists(session):
            active_user = users.get_active_user_name(session)
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


cli.add_command(user)
