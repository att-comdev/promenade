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
        with open(os.path.join(output_dir, 'genesis.sh'), 'w') as f:
            f.write(script)

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

        with open(os.path.join(output_dir, _join_name(node_name)), 'w') as f:
            f.write(script)


def _join_name(node_name):
    return 'join-%s.sh' % node_name
