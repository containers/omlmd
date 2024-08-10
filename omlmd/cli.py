# Using this to scope CLI targets
import click
from omlmd.helpers import Helper
from omlmd.provider import OMLMDRegistry
from omlmd.model_metadata import deserialize_mdfile


plain_http = click.option('--plain-http', help="allow insecure connections to registry without SSL check", is_flag=True, default=False, show_default=True)


def get_OMLMDRegistry(plain_http: bool) -> OMLMDRegistry:
    return OMLMDRegistry(insecure=plain_http)


@click.group()
def cli():
    pass

@click.command()
@plain_http
@click.argument('target', required=True)
@click.option('-o', '--output', default='.', show_default=True)
@click.option('--media-types', '-m', multiple=True, default=[])
def pull(plain_http, target, output, media_types):
    """Pulls an OCI Artifact containing ML model and metadata, filtering if necessary."""
    Helper(get_OMLMDRegistry(plain_http)).pull(target, output, media_types)

@click.group()
def get():
    pass

@click.command()
@plain_http
@click.argument('target', required=True)
def config(plain_http, target):
    """Outputs configuration of the given OCI Artifact for ML model and metadata."""
    click.echo(Helper(get_OMLMDRegistry(plain_http)).get_config(target))

@click.command()
@plain_http
@click.argument('targets', required=True, nargs=-1)
def crawl(plain_http, targets):
    """Crawls configuration for the given list of OCI Artifact for ML model and metadata."""
    click.echo(Helper(get_OMLMDRegistry(plain_http)).crawl(targets))
    
@click.command()
@plain_http
@click.argument('target', required=True)
@click.argument('path', required=True, type=click.Path())
@click.option('-m', '--metadata', required=True, type=click.Path())
def push(plain_http, target, path, metadata):
    """Pushes an OCI Artifact containing ML model and metadata, supplying metadata from file as necessary"""
    import logging
    logging.basicConfig(level=logging.DEBUG)
    md = deserialize_mdfile(metadata)
    click.echo(Helper(get_OMLMDRegistry(plain_http)).push(target, path, **md))

cli.add_command(pull)
cli.add_command(get)
get.add_command(config)
cli.add_command(crawl)
cli.add_command(push)
