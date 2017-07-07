# Copyright 2017 The Promenade Authors.
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

from . import generator, logging, operator
import click

__all__ = []


LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
def promenade(*, verbose):
    logging.setup(verbose=verbose)


@promenade.command(help='Initialize a new cluster on one node')
@click.option('-a', '--asset-dir', default='/assets',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Source path for binaries to deploy.')
@click.option('-c', '--config-path', type=click.File(),
              help='Location of cluster configuration data.')
@click.option('--hostname', help='Current hostname.')
@click.option('-t', '--target-dir', default='/target',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Location where templated files will be placed.')
def genesis(*, asset_dir, config_path, hostname, target_dir):

    op = operator.Operator.from_config(config_path=config_path,
                                       hostname=hostname,
                                       target_dir=target_dir)

    op.genesis(asset_dir=asset_dir)


@promenade.command(help='Join an existing cluster')
@click.option('-a', '--asset-dir', default='/assets',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Source path for binaries to deploy.')
@click.option('-c', '--config-path', type=click.File(),
              help='Location of cluster configuration data.')
@click.option('--hostname', help='Current hostname.')
@click.option('-t', '--target-dir', default='/target',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Location where templated files will be placed.')
def join(*, asset_dir, config_path, hostname, target_dir):

    op = operator.Operator.from_config(config_path=config_path,
                                       hostname=hostname,
                                       target_dir=target_dir)

    op.join(asset_dir=asset_dir)


@promenade.command(help='Generate certs and keys')
@click.option('-c', '--config-path', type=click.File(),
              required=True,
              help='Location of cluster configuration data.')
@click.option('-o', '--output-dir', default='.',
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              resolve_path=True),
              required=True,
              help='Location to write complete cluster configuration.')
def generate(*, config_path, output_dir):
    g = generator.Generator.from_config(config_path=config_path)
    g.generate_all(output_dir)
