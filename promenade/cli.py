from . import logging, operator
import click

__all__ = []


LOG = logging.getLogger(__name__)


@click.command()
@click.option('-a', '--asset-dir', default='/assets',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Source path for binaries to deploy.')
@click.option('-c', '--config-path',
              type=click.Path(exists=True, file_okay=True,
                              dir_okay=False, resolve_path=True),
              help='Location of cluster configuration data.')
@click.option('--hostname', help='Current hostname.')
@click.option('-t', '--target-dir', default='/target',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Location where templated files will be placed.')
@click.option('-v', '--verbose', is_flag=True)
def entry_point(*, asset_dir, config_path, hostname, target_dir, verbose):
    logging.setup(verbose=verbose)

    op = operator.Operator.from_config(config_path=config_path,
                                       hostname=hostname,
                                       target_dir=target_dir)

    op.setup(asset_dir=asset_dir)

#    # Install templated configuration
#    templater = templaters.Templater.from_config(hostname, config)
#    templater.render_to_target(target_dir=target_dir)
#
#    pki.generate_keys(target_dir=target_dir)
#
#    # Perform final initialization on the host.
#    chroot.bootstrap(target_dir)
#
#    # (If genesis)
##    etcd.expand_members()
#
#    # wait for the api
#    # do helm thing
