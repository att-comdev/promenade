from promenade import logging
import abc
import jinja2
import os
import pkg_resources
import yaml

__all__ = ['Genesis']


LOG = logging.getLogger(__name__)


class BaseTemplater(metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def CONFIG_FILE(self):
        pass

    @abc.abstractproperty
    def TEMPLATE_PATHS(self):
        pass

    @classmethod
    def from_config_dir(cls, config_dir_path):
        path = os.path.join(config_dir_path, cls.CONFIG_FILE)
        LOG.debug('Loading genesis configuration from "%s"', path)
        data = yaml.load(open(path))
        LOG.debug('Loaded genesis configruation from "%s"', path)
        return cls(data)

    def __init__(self, data):
        self.data = data

    def render_to_target(self, *, target_dir):
        for template_dir in self.TEMPLATE_PATHS:
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



class Genesis(BaseTemplater):
    CONFIG_FILE = 'genesis.yaml'
    TEMPLATE_PATHS = ('common', 'genesis')


def _ensure_path(path):
    base = os.path.dirname(path)
    os.makedirs(base, mode=0o775, exist_ok=True)
