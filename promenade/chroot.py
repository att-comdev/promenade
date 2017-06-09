from promenade import logging
import os
import subprocess

__all__ = ['genesis']


LOG = logging.getLogger(__name__)


def genesis(target):
    LOG.info('Running genesis script with chroot "%s"', target)
