from promenade import logging
import os
import shutil
import subprocess
import tempfile

__all__ = ['generate_keys']


LOG = logging.getLogger(__name__)


DISTRIBUTION_MAP = {
    'sa': [
        'apiserver',
    ],
    'sa-key': [
        'controller-manager',
    ],
}


def generate_keys(target):
    with tempfile.TemporaryDirectory() as tmp:
        _make_sa_keypair(tmp)

        _distribute_files(tmp, target)


def _make_sa_keypair(output_dir):
        private_key = os.path.join(output_dir, 'sa-key.pem')
        public_key = os.path.join(output_dir, 'sa.pem')
        subprocess.run(['/usr/bin/openssl', 'genrsa',
                        '-out', private_key], check=True)
        subprocess.run(['/usr/bin/openssl', 'rsa', '-pubout',
                        '-in', private_key,
                        '-out', public_key], check=True)


def _distribute_files(src, dest):
    for filename, destinations in DISTRIBUTION_MAP.items():
        src_path = os.path.join(src, filename + '.pem')
        for destination in destinations:
            dest_dir = os.path.join(dest, 'etc/kubernetes/%s/pki' % destination)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy(src_path, dest_dir)
