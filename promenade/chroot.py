from promenade import logging
import subprocess

__all__ = ['bootstrap']


LOG = logging.getLogger(__name__)


def bootstrap(target):
    LOG.debug('Running genesis script with chroot "%s"', target)
    subprocess.run(['/target/usr/sbin/chroot', '/target',
                    '/bin/bash', '/usr/local/bin/bootstrap'],
                   check=True)
