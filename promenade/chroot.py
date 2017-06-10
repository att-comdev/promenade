from promenade import logging
import pkg_resources
import os
import subprocess

__all__ = ['genesis']


LOG = logging.getLogger(__name__)


def genesis(target):
    LOG.debug('Running genesis script with chroot "%s"', target)
    subprocess.run(['/bin/bash', '/usr/local/bin/bootstrap-genesis'],
                   check=True, preexec_fn=lambda: os.chroot(target))
