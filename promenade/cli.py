from . import builder, config, exceptions, generator, logging
import click
import sys

__all__ = []


LOG = logging.getLogger(__name__)


@click.group()
@click.option('-v', '--verbose', is_flag=True)
def promenade(*, verbose):
    logging.setup(verbose=verbose)


@promenade.command('build-all', help='Construct all scripts')
@click.option('-o', '--output-dir', default='.',
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              resolve_path=True),
              required=True,
              help='Location to write complete cluster configuration.')
@click.argument('config_files', nargs=-1, type=click.File('rb'))
def build_all(*, config_files, output_dir):
    try:
        c = config.Configuration.from_streams(streams=config_files)
        b = builder.Builder(c)
        b.build_all(output_dir=output_dir)
    except exceptions.PromenadeException as e:
        e.display()
        sys.exit(1)


@promenade.command('generate-certs', help='Generate a certs for a site')
@click.option('-o', '--output-dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              resolve_path=True),
              required=True,
              help='Location to write *-certificates.yaml')
@click.argument('config_files', nargs=-1, type=click.File('rb'))
@click.option('--calico-etcd-service-ip', default='10.96.232.136',
              help='Service IP for calico etcd')
def genereate_certs(*, calico_etcd_service_ip,config_files, output_dir):
    try:
        c = config.Configuration.from_streams(substitute=False, streams=config_files)
        g = generator.Generator(c,
                calico_etcd_service_ip=calico_etcd_service_ip)
        g.generate(output_dir)
    except exceptions.PromenadeException as e:
        e.display()
        sys.exit(1)
