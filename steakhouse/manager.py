import click
from steakhouse.models import create_tables


@click.group()
def cli():
    pass

@cli.command()
def createdb():
    create_tables()
