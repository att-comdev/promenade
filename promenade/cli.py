from . import builder, config, exceptions, generator, logging
from promenade_client import client
import click
import os
import sys

__all__ = []

LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
def promenade(*, verbose):
    if _debug():
        verbose = True
    logging.setup(verbose=verbose)


@promenade.command('build-all', help='Construct all scripts')
@click.option(
    '-o',
    '--output-dir',
    default='.',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    required=True,
    help='Location to write complete cluster configuration.')
@click.option('--validators', is_flag=True, help='Generate validation scripts')
@click.argument('config_files', nargs=-1, type=click.File('rb'))
def build_all(*, config_files, output_dir, validators):
    debug = _debug()
    try:
        c = config.Configuration.from_streams(
            debug=debug, streams=config_files)
        b = builder.Builder(c, validators=validators)
        b.build_all(output_dir=output_dir)
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('generate-certs', help='Generate a certs for a site')
@click.option(
    '-o',
    '--output-dir',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    required=True,
    help='Location to write *-certificates.yaml')
@click.argument('config_files', nargs=-1, type=click.File('rb'))
def genereate_certs(*, config_files, output_dir):
    debug = _debug()
    try:
        c = config.Configuration.from_streams(
            debug=debug, streams=config_files, substitute=True, validate=False)
        g = generator.Generator(c)
        g.generate(output_dir)
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('check-health', help='Check health of Promenade API')
def check_health():
    debug = _debug()
    try:
        client.get_health()
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('join-scripts', help='Generate join scripts')
@click.option('--hostname', required=True, help='Name of the node')
@click.option('--ip', required=True, help='IP address of the node')
@click.option(
    '--design-ref',
    required=True,
    help='Endpoint containing configuration documents')
@click.option(
    '-dl',
    '--dynamic-labels',
    required=True,
    help='Used to set configuration options in generated script')
@click.option(
    '-sl',
    '--static-labels',
    required=True,
    help='Used to set configuration options in generated script')
def join_scripts(*, hostname, ip, design_ref, dynamic_labels, static_labels):
    debug = _debug()
    try:
        client.get_join_scripts(
            hostname=hostname,
            ip=ip,
            design_ref=design_ref,
            dynamic_labels=dynamic_labels,
            static_labels=static_labels)
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


def _debug():
    return os.environ.get('PROMENADE_DEBUG', '').lower() in {'1', 'True'}
