from promenade import builder, config, exceptions, generator, logging
from promenade.promenade_cli import client_helper
from promenade.promenade_client import client, session
import click
import os
import sys
from urllib.parse import urlparse

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
            debug=debug,
            substitute=True,
            allow_missing_substitutions=False,
            streams=config_files)
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
            debug=debug,
            streams=config_files,
            substitute=True,
            allow_missing_substitutions=True,
            validate=False)
        g = generator.Generator(c)
        g.generate(output_dir)
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('check-health', help='Check health of Promenade API')
@click.option('--token', required=True, help="User token")
@click.pass_context
def check_health(ctx, token):
    debug = _debug()
    try:
        prom_client = get_client(token, ctx)
        client_helper.CheckHealth(prom_client).invoke()
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('validatedesign', help='Check health of Promenade API')
@click.option('--token', required=True, help="User token")
@click.option(
    '--href',
    required=True,
    help='Endpoint containing documents to be validated')
@click.pass_context
def validate_design(ctx, token, href):
    debug = _debug()
    try:
        prom_client = get_client(token, ctx)
        client_helper.Validate(prom_client).invoke(href=href)
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('join-scripts', help='Generate join scripts')
@click.option('--token', required=True, help="User token")
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
    required=False,
    help='Used to set configuration options in generated script')
@click.pass_context
def join_scripts(*, ctx, token, hostname, ip, design_ref, dynamic_labels,
                 static_labels):
    debug = _debug()
    try:
        prom_client = get_client(token, ctx)
        client_helper.JoinScripts(prom_client).invoke(
            hostname=hostname,
            ip=ip,
            design_ref=design_ref,
            dynamic_labels=dynamic_labels,
            static_labels=static_labels)
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


def get_client(token, ctx):
    ks_sess = session.KeystoneClient.get_ks_session(token=token)
    url = session.KeystoneClient.get_endpoint(
        'physicalprovisioner', ks_sess=ks_sess)

    url_parse_result = urlparse(url)

    def auth_gen():
        return list(ks_sess.get_auth_headers().items())

    ctx.obj['CLIENT'] = client.PromenadeClient(
        session.PromenadeSession(
            scheme=url_parse_result.scheme,
            host=url_parse_result.hostname,
            port=url_parse_result.port,
            auth_gen=auth_gen))
    return ctx.obj['CLIENT']


def _debug():
    return os.environ.get('PROMENADE_DEBUG', '').lower() in {'1', 'True'}
