# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from promenade import builder, config, exceptions, generator, logging
from promenade.promenade_cli import client_helper
from promenade.promenade_client import client, session
import click
import os
import sys
from urllib.parse import urlparse
import json

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


@promenade.command('generate-certs', help='Generate certs for a site')
@click.option(
    '-o',
    '--output-dir',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    required=True,
    help='Location to write *-certificates.yaml')
@click.argument('config_files', nargs=-1, type=click.File('rb'))
def generate_certs(*, config_files, output_dir):
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


@promenade.command('check-health', help='Checks health of Promenade API')
@click.option(
    '--os_project_domain_name',
    envvar='OS_PROJECT_DOMAIN_NAME',
    required=False)
@click.option(
    '--os_user_domain_name', envvar='OS_USER_DOMAIN_NAME', required=False)
@click.option('--os_project_name', envvar='OS_PROJECT_NAME', required=False)
@click.option('--os_username', envvar='OS_USERNAME', required=False)
@click.option('--os_password', envvar='OS_PASSWORD', required=False)
@click.option('--os_auth_url', envvar='OS_AUTH_URL', required=False)
@click.option(
    '--token',
    help='The Keystone token to be used',
    default=lambda: os.environ.get('OS_TOKEN', ''))
@click.option(
    '--url',
    '-u',
    help='Promenade API URL',
    default=lambda: os.environ.get('PROM_URL', ''))
@click.pass_context
def check_health(ctx, os_project_domain_name, os_user_domain_name,
                 os_project_name, os_username, os_password, os_auth_url, token,
                 url):
    debug = _debug()
    try:
        if token:
            prom_client = get_client(ctx, url=url, token=token)
        else:
            keystone_env = {
                'project_domain_name': os_project_domain_name,
                'user_domain_name': os_user_domain_name,
                'project_name': os_project_name,
                'username': os_username,
                'password': os_password,
                'auth_url': os_auth_url,
            }
            prom_client = get_client(ctx, url=url, keystone_env=keystone_env)
        click.echo(client_helper.CheckHealth(prom_client).invoke())
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('validatedesign', help='Validates node design docs')
@click.option(
    '--os_project_domain_name',
    envvar='OS_PROJECT_DOMAIN_NAME',
    required=False)
@click.option(
    '--os_user_domain_name', envvar='OS_USER_DOMAIN_NAME', required=False)
@click.option('--os_project_name', envvar='OS_PROJECT_NAME', required=False)
@click.option('--os_username', envvar='OS_USERNAME', required=False)
@click.option('--os_password', envvar='OS_PASSWORD', required=False)
@click.option('--os_auth_url', envvar='OS_AUTH_URL', required=False)
@click.option(
    '--token',
    help='The Keystone token to be used',
    default=lambda: os.environ.get('OS_TOKEN', ''))
@click.option(
    '--url',
    '-u',
    help='Promenade API URL',
    default=lambda: os.environ.get('PROM_URL', ''))
@click.option(
    '--href',
    required=True,
    help='Endpoint containing documents to be validated')
@click.pass_context
def validate_design(ctx, os_project_domain_name, os_user_domain_name,
                    os_project_name, os_username, os_password, os_auth_url,
                    token, href, url):
    debug = _debug()
    try:
        if token:
            prom_client = get_client(ctx, url=url, token=token)
        else:
            keystone_env = {
                'project_domain_name': os_project_domain_name,
                'user_domain_name': os_user_domain_name,
                'project_name': os_project_name,
                'username': os_username,
                'password': os_password,
                'auth_url': os_auth_url,
            }
            prom_client = get_client(ctx, url=url, keystone_env=keystone_env)

        click.echo(
            json.dumps(client_helper.Validate(prom_client, href).invoke()))
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


@promenade.command('join-scripts', help='Generate join scripts')
@click.option(
    '--os_project_domain_name',
    envvar='OS_PROJECT_DOMAIN_NAME',
    required=False)
@click.option(
    '--os_user_domain_name', envvar='OS_USER_DOMAIN_NAME', required=False)
@click.option('--os_project_name', envvar='OS_PROJECT_NAME', required=False)
@click.option('--os_username', envvar='OS_USERNAME', required=False)
@click.option('--os_password', envvar='OS_PASSWORD', required=False)
@click.option('--os_auth_url', envvar='OS_AUTH_URL', required=False)
@click.option(
    '--token',
    help='The Keystone token to be used',
    default=lambda: os.environ.get('OS_TOKEN', ''))
@click.option(
    '--url',
    '-u',
    help='Promenade API url',
    default=lambda: os.environ.get('PROM_URL', ''))
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
def join_scripts(ctx, os_project_domain_name, os_user_domain_name,
                 os_project_name, os_username, os_password, os_auth_url, token,
                 url, hostname, ip, design_ref, dynamic_labels, static_labels):
    debug = _debug()
    try:
        if token:
            prom_client = get_client(ctx, url=url, token=token)
        else:
            keystone_env = {
                'project_domain_name': os_project_domain_name,
                'user_domain_name': os_user_domain_name,
                'project_name': os_project_name,
                'username': os_username,
                'password': os_password,
                'auth_url': os_auth_url,
            }
            prom_client = get_client(ctx, url=url, keystone_env=keystone_env)
        click.echo(
            json.dumps(
                client_helper.JoinScripts(prom_client, hostname, ip,
                                          design_ref, dynamic_labels,
                                          static_labels).invoke()))
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


def get_client(ctx, url=None, token=None, keystone_env=None):
    if not ctx.obj:
        ctx.obj = {}
    if not token:
        ks_sess = session.KeystoneClient.get_ks_session(**keystone_env)
    else:
        ks_sess = session.KeystoneClient.get_ks_session(token=token)
    session.KeystoneClient.get_token(ks_sess=ks_sess)

    if not url:
        url = session.KeystoneClient.get_endpoint(
            'kubernetesprovisioner', ks_sess=ks_sess)

    url_parse_result = urlparse(url)

    ctx.obj['CLIENT'] = client.PromenadeClient(
        session.PromenadeSession(
            scheme=url_parse_result.scheme,
            host=url_parse_result.hostname,
            port=url_parse_result.port))
    return ctx.obj['CLIENT']


def _debug():
    return os.environ.get('PROMENADE_DEBUG', '').lower() in {'1', 'True'}
