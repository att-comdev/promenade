from . import kube, logging

__all__ = ['add_member']


LOG = logging.getLogger(__name__)


def add_member(exec_pod, hostname, port):
    result = kube.kc('exec', '-n', 'kube-system', '-t', exec_pod, '--', 'sh', '-c',
                     'ETCDCTL_API=3 etcdctl member add %s --peer-urls http://%s:%d'
                     % (hostname, hostname, port))
    if result.returncode != 0:
        LOG.error('Failed to add etcd member. STDOUT: %r', result.stdout)
        LOG.error('Failed to add etcd member. STDERR: %r', result.stderr)
        result.check_returncode()
