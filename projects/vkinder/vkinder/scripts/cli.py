import os.path

import click

from vkinder import app
from vkinder import menu
from vkinder.globals import dbpath, tokenpath


@click.option('--export', '-e', is_flag=True,
              help="Export next matches to a JSON file rather than printing to the console")
@click.option('--output-amount', '-o', default=10, show_default=True,
              help="Amount of matches returned by 'next' menu option")
@click.group()
@click.pass_context
def cli(ctx, output_amount, export):
    """
    VKInder: Python coursework by Roman Vlasenko
    """
    ctx.ensure_object(dict)
    ctx.obj['output_amount'] = output_amount
    ctx.obj['export'] = export


@cli.command()
@click.option('--same-sex', '-s', is_flag=True,
              help='Search for matches with the same sex as the user')
@click.option('--ignore-age', '-iage', is_flag=True,
              help='Ignore age when searching for matches')
@click.option('--ignore-city', '-icity', is_flag=True,
              help='Ignore city when searching for matches')
@click.pass_context
def run(ctx, ignore_city, ignore_age, same_sex):
    """Start application and run menu"""
    ctx.obj['ignore_city'] = ignore_city
    ctx.obj['ignore_age'] = ignore_age
    ctx.obj['same_sex'] = same_sex
    vkinder = app.startup(ctx.obj)
    menu.run(vkinder)


@cli.command()
def cleardb():
    """Delete database file"""
    if os.path.exists(dbpath):
        os.remove(dbpath)


@cli.command()
def cleartoken():
    """Delete saved token"""
    if os.path.exists(tokenpath):
        os.remove(tokenpath)


if __name__ == '__main__':
    cli()
