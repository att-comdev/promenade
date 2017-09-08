from . import logging, renderer
import os

__all__ = ['Builder']

LOG = logging.getLogger(__name__)


class Builder:
    def __init__(self, config):
        self.config = config

    def build_all(self, *, output_dir):
        self.build_genesis(output_dir=output_dir)
        for node_document in self.config.iterate(
                schema='promenade/KubernetesNode/v1'):
            self.build_node(node_document, output_dir=output_dir)

    def build_genesis(self, *, output_dir):
        LOG.info('Building genesis script')
        sub_config = self.config.extract_genesis_config()
        tarball = renderer.build_tarball_from_roles(
            config=sub_config, roles=['common', 'genesis'])

        script = renderer.render_template(
            sub_config,
            template='scripts/genesis.sh',
            context={'tarball': tarball})

        _write_script(output_dir, 'genesis.sh', script)

    def build_node(self, node_document, *, output_dir):
        node_name = node_document['metadata']['name']
        LOG.info('Building script for node %s', node_name)
        sub_config = self.config.extract_node_config(node_name)
        tarball = renderer.build_tarball_from_roles(
            config=sub_config, roles=['common', 'join'])

        script = renderer.render_template(
            sub_config,
            template='scripts/join.sh',
            context={'tarball': tarball})

        _write_script(output_dir, _join_name(node_name), script)


def _join_name(node_name):
    return 'join-%s.sh' % node_name


def _write_script(output_dir, name, script):
    path = os.path.join(output_dir, name)
    with open(path, 'w') as f:
        os.fchmod(f.fileno(), 0o555)
        f.write(script)
