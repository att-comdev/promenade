from . import assets, chroot, logging, pki, templaters
import click

__all__ = []


LOG = logging.getLogger(__name__)


@click.command()
@click.option('-a', '--asset-dir', default='/assets',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Source path for binaries to deploy.')
@click.option('-c', '--config', type=click.Path(exists=True, file_okay=True,
                                                dir_okay=False, resolve_path=True),
              help='Location of cluster configuration data.')
@click.option('--hostname', help='Current hostname.')
@click.option('-t', '--target-dir', default='/target',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Location where templated files will be placed.')
@click.option('-v', '--verbose', is_flag=True)
def entry_point(*, asset_dir, config, hostname, target_dir, verbose):
    logging.setup(verbose=verbose)

    # Install binary/static data
    assets.rsync(src=asset_dir, dest=target_dir)

    # Install templated configuration
    templater = templaters.Templater.from_config(hostname, config)
    templater.render_to_target(target_dir=target_dir)

    pki.generate_keys(target_dir=target_dir)

    # Perform final initialization on the host.
    chroot.bootstrap(target_dir)

    # wait for the api
    # do helm thing
