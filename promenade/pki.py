from promenade import logging
import os
import shutil
import subprocess
import tempfile

__all__ = ['generate_keys']


LOG = logging.getLogger(__name__)


def generate_keys(target):
    with tempfile.TemporaryDirectory() as tmp:
        private_key = os.path.join(tmp, 'sa.key')
        public_key = os.path.join(tmp, 'sa.pub')
        key_target_dir = os.path.join(target, 'etc/kubernetes/controller-manager/pki')
        pub_target_dir = os.path.join(target, 'etc/kubernetes/apiserver/pki')
        key_target = os.path.join(key_target_dir, 'sa.key')
        pub_target = os.path.join(pub_target_dir, 'sa.pub')

        subprocess.run(['/usr/bin/openssl', 'genrsa',
                        '-out', private_key], check=True)
        subprocess.run(['/usr/bin/openssl', 'rsa', '-pubout',
                        '-in', private_key,
                        '-out', public_key], check=True)

        os.makedirs(key_target_dir, exist_ok=True)
        os.makedirs(pub_target_dir, exist_ok=True)
        shutil.move(private_key, key_target)
        shutil.move(public_key, pub_target)
