from promenade import logging
import os
import shutil
import subprocess
import tempfile

__all__ = ['generate_keys']


LOG = logging.getLogger(__name__)


CA_ONLY_MAP = {
    'cluster-ca': [
        'kubelet',
    ],
}


FULL_DISTRIBUTION_MAP = {
    'apiserver': [
        'apiserver',
    ],
    'apiserver-key': [
        'apiserver',
    ],
    'cluster-ca': [
        'apiserver',
        'controller-manager',
        'kubelet',
        'proxy',
        'scheduler',
    ],
    'cluster-ca-key': [
        'controller-manager',
    ],
    'sa': [
        'apiserver',
    ],
    'sa-key': [
        'controller-manager',
    ],
}


def generate_keys(*, initial_pki, target_dir):
    if os.path.exists(os.path.join(target_dir, 'etc/kubernetes/cfssl')):
        with tempfile.TemporaryDirectory() as tmp:
            _write_initial_pki(tmp, initial_pki)
            _make_sa_keypair(tmp)

            _generate_certs(tmp, target_dir)

            _distribute_files(tmp, target_dir, FULL_DISTRIBUTION_MAP)


def _write_initial_pki(tmp, initial_pki):
    for filename, data in initial_pki.items():
        path = os.path.join(tmp, filename + '.pem')
        with open(path, 'w') as f:
            LOG.debug('Writing data for "%s" to path "%s"', filename, path)
            f.write(data)


def _make_sa_keypair(output_dir):
        private_key = os.path.join(output_dir, 'sa-key.pem')
        public_key = os.path.join(output_dir, 'sa.pem')
        subprocess.run(['/usr/bin/openssl', 'genrsa',
                        '-out', private_key], check=True)
        subprocess.run(['/usr/bin/openssl', 'rsa', '-pubout',
                        '-in', private_key,
                        '-out', public_key], check=True)


def _generate_certs(dest, target):
    ca_config_path = os.path.join(target, 'etc/kubernetes/cfssl/ca-config.json')
    ca_path = os.path.join(dest, 'cluster-ca.pem')
    ca_key_path = os.path.join(dest, 'cluster-ca-key.pem')
    search_dir = os.path.join(target, 'etc/kubernetes/cfssl/csr-configs')
    for filename in os.listdir(search_dir):
        name, _ext = os.path.splitext(filename)
        path = os.path.join(search_dir, filename)
        cfssl_result = subprocess.check_output([
            'cfssl', 'gencert', '-ca', ca_path, '-ca-key', ca_key_path,
            '-config', ca_config_path, '-profile', 'kubernetes', path])
        subprocess.run(['cfssljson', '-bare', name], cwd=dest,
                       input=cfssl_result, check=True)


def _distribute_files(src, dest, distribution_map):
    for filename, destinations in distribution_map.items():
        src_path = os.path.join(src, filename + '.pem')
        for destination in destinations:
            dest_dir = os.path.join(dest, 'etc/kubernetes/%s/pki' % destination)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy(src_path, dest_dir)
