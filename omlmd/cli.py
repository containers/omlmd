# Using this to scope CLI targets
import click
from omlmd.helpers import Helper

@click.group()
def cli():
    pass

@click.command()
@click.argument('target', required=True)
@click.option('-o', '--output', default='.', show_default=True)
@click.option('--media-types', '-m', multiple=True, default=[])
def pull(target, output, media_types):
    """Pulls an OCI Artifact containing ML model and metadata, filtering if necessary."""
    Helper().pull(target, output, media_types)

@click.group()
def get():
    pass

@click.command()
@click.argument('target', required=True)
def config(target):
    """Outputs configuration of the given OCI Artifact for ML model and metadata."""
    click.echo(Helper().get_config(target))

@click.command()
@click.argument('targets', required=True, nargs=-1)
def crawl(targets):
    """Crawls configuration for the given list of OCI Artifact for ML model and metadata."""
    click.echo(Helper().crawl(targets))

cli.add_command(pull)
cli.add_command(get)
get.add_command(config)
cli.add_command(crawl)
