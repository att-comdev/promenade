from promenade import logging
import jinja2
import operator
import os
import pkg_resources
import yaml

__all__ = ['Templater']


LOG = logging.getLogger(__name__)


class Templater:
    @classmethod
    def from_config(cls, hostname, path):
        LOG.debug('Loading genesis configuration from "%s"', path)
        cluster_data = yaml.load(open(path))
        LOG.debug('Loaded genesis configruation from "%s"', path)
        return cls(hostname, cluster_data)

    def __init__(self, hostname, cluster_data):
        self.data = {
            'cluster': cluster_data['nodes'],
            'current_node': _extract_current_node_data(cluster_data['nodes'],
                                                       hostname),
            'genesis': _extract_genesis_data(cluster_data['nodes']),
            'masters': _extract_master_data(cluster_data['nodes']),
            'network': cluster_data['network'],
        }

    @property
    def template_paths(self):
        return ['common'] + self.data['current_node']['roles']

    def render_to_target(self, *, target_dir):
        for template_dir in self.template_paths:
            self.render_template_dir(template_dir=template_dir,
                                     target_dir=target_dir)

    def render_template_dir(self, *, template_dir, target_dir):
        source_root = pkg_resources.resource_filename(
                'promenade', os.path.join('templates', template_dir))
        LOG.debug('Searching for templates in: "%s"', source_root)
        for root, _dirnames, filenames in os.walk(source_root,
                                                  followlinks=True):
            for source_filename in filenames:
                source_path = os.path.join(root, source_filename)
                self.render_template_file(path=source_path,
                                          root=source_root,
                                          target_dir=target_dir)

    def render_template_file(self, *, path, root, target_dir):
        base_path = os.path.relpath(path, root)
        target_path = os.path.join(target_dir, base_path)

        _ensure_path(target_path)

        LOG.debug('Templating "%s" into "%s"', path, target_path)

        env = jinja2.Environment(undefined=jinja2.StrictUndefined)

        with open(path) as f:
            template = env.from_string(f.read())
        rendered_data = template.render(**self.data)

        with open(target_path, 'w') as f:
            f.write(rendered_data)

        LOG.info('Installed "%s"', os.path.join('/', base_path))


def _extract_current_node_data(nodes, hostname):
    base = nodes[hostname]
    return {
        'hostname': hostname,
        'labels': _extract_node_labels(base),
        **base,
    }


ROLE_LABELS = {
    'common': [
    ],
    'genesis': [
        'promenade=genesis',
    ],
    'master': [
        'node-role.kubernetes.io/master=',
    ],
    'worker': [
    ],
}


def _extract_node_labels(data):
    labels = set(map(lambda k: ROLE_LABELS[k], ['common'] + data['roles']))
    labels.update(data.get('additional_labels', []))
    return sorted(labels)


def _extract_genesis_data(nodes):
    for hostname, node in nodes.items():
        if 'genesis' in node['roles']:
            return {
                'hostname': hostname,
                'ip': node['ip'],
            }


def _extract_master_data(nodes):
    # XXX Testing this + dnsmasq registration
    return sorted(({'hostname': hostname, 'ip': node['ip']}
                   for hostname, node in nodes.items()
                   if 'master' in node['roles']),
                  key=operator.itemgetter('hostname'))


def _ensure_path(path):
    base = os.path.dirname(path)
    os.makedirs(base, mode=0o775, exist_ok=True)
