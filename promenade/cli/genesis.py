from promenade import logging
import click
import promenade.assets
import promenade.chroot
import promenade.pki
import promenade.templaters

__all__ = []


LOG = logging.getLogger(__name__)


@click.command()
@click.option('-a', '--asset-dir', default='/assets',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Source path for binaries to deploy.')
@click.option('-c', '--config-dir', default='/etc/promenade',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Location of cluster configuration data.')
@click.option('-t', '--target-dir', default='/target',
              type=click.Path(exists=True, file_okay=False,
                              dir_okay=True, resolve_path=True),
              help='Location where templated files will be placed.')
@click.option('-v', '--verbose', is_flag=True)
def entry_point(*, asset_dir, config_dir, target_dir, verbose):
    logging.setup(verbose=verbose)

    # Install binary/static data
    promenade.assets.rsync(src=asset_dir, dest=target_dir)

    # Install templated configuration
    templater = promenade.templaters.Genesis.from_config_dir(config_dir)
    templater.render_to_target(target_dir=target_dir)

    promenade.pki.generate_keys(config_dir=config_dir, target_dir=target_dir)

    # Perform final initialization on the host.
    promenade.chroot.bootstrap(target_dir)

    # wait for the api
    # do helm thing
