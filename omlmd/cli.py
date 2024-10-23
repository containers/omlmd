"""Command line interface for OMLMD."""

from __future__ import annotations

import logging
from pathlib import Path

import click
import cloup

from .helpers import Helper
from .model_metadata import deserialize_mdfile

logger = logging.getLogger(__name__)


plain_http = click.option(
    "--plain-http",
    help="Allow insecure connections to registry without SSL check",
    is_flag=True,
    default=False,
    show_default=True,
)


@cloup.group()
def cli():
    logging.basicConfig(level=logging.INFO)


@cli.command()
@plain_http
@click.argument("target", required=True)
@click.option(
    "-o",
    "--output",
    default=Path.cwd(),
    show_default=True,
    type=click.Path(path_type=Path, resolve_path=True),
)
@click.option("--media-types", "-m", multiple=True, default=[])
def pull(plain_http: bool, target: str, output: Path, media_types: tuple[str]):
    """Pulls an OCI Artifact containing ML model and metadata, filtering if necessary."""
    Helper.from_plain(plain_http).pull(target, output, media_types)


@cli.group()
def get():
    pass


@get.command()
@plain_http
@click.argument("target", required=True)
def config(plain_http: bool, target: str):
    """Outputs configuration of the given OCI Artifact for ML model and metadata."""
    click.echo(Helper.from_plain(plain_http).get_config(target))


@cli.command()
@plain_http
@click.argument("targets", required=True, nargs=-1)
def crawl(plain_http: bool, targets: tuple[str]):
    """Crawls configuration for the given list of OCI Artifact for ML model and metadata."""
    click.echo(Helper.from_plain(plain_http).crawl(targets))


@cli.command()
@plain_http
@click.argument("target", required=True)
@click.argument(
    "path",
    required=True,
    type=click.Path(path_type=Path, exists=True, resolve_path=True),
)
@cloup.option_group(
    "Metadata options",
    cloup.option(
        "-m",
        "--metadata",
        type=click.Path(path_type=Path, exists=True, resolve_path=True),
        help="Metadata file in JSON or YAML format",
    ),
    cloup.option("--empty-metadata", help="Push with empty metadata", is_flag=True),
    constraint=cloup.constraints.require_one,
)
def push(
    plain_http: bool,
    target: str,
    path: Path,
    metadata: Path | None,
    empty_metadata: bool,
):
    """Pushes an OCI Artifact containing ML model and metadata, supplying metadata from file as necessary"""

    if empty_metadata:
        logger.warning(f"Pushing to {target} with empty metadata.")
    md = deserialize_mdfile(metadata) if metadata else {}
    click.echo(Helper.from_plain(plain_http).push(target, path, **md))
