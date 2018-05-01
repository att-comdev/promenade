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

from . import agent, builder, config, exceptions, generator, logging
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
@click.option(
    '--leave-kubectl',
    is_flag=True,
    help='Leave behind kubectl on joined nodes')
@click.argument('config_files', nargs=-1, type=click.File('rb'))
def build_all(*, config_files, leave_kubectl, output_dir, validators):
    debug = _debug()
    try:
        c = config.Configuration.from_streams(
            debug=debug,
            substitute=True,
            allow_missing_substitutions=False,
            leave_kubectl=leave_kubectl,
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


@promenade.command('agent', help='Run in-cluster agent')
@click.option(
    '--hostname',
    required=True,
)
def agent_cmd(*, hostname):
    debug = _debug()

    try:
        a = agent.runner.AgentRunner.with_defaults(hostname=hostname)
        a.run()
    except exceptions.PromenadeException as e:
        e.display(debug=debug)
        sys.exit(e.EXIT_CODE)


def _debug():
    return os.environ.get('PROMENADE_DEBUG', '').lower() in {'1', 'True'}
