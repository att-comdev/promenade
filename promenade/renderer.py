from . import logging
import jinja2
import os
import pkg_resources
import hashlib

__all__ = ['Renderer']


LOG = logging.getLogger(__name__)


class Renderer:
    def __init__(self, *, config, target_dir):
        self.config = config
        self.target_dir = target_dir

    def render(self):
        for template_dir in self.config['Node']['templates']:
            self.render_template_dir(template_dir)

    def render_template_dir(self, template_dir):
        source_root = pkg_resources.resource_filename(
                'promenade', os.path.join('templates', template_dir))
        LOG.debug('Searching for templates in: "%s"', source_root)
        for root, _dirnames, filenames in os.walk(source_root,
                                                  followlinks=True):
            for source_filename in filenames:
                source_path = os.path.join(root, source_filename)
                self.render_template_file(path=source_path,
                                          root=source_root)
                self.generate_sha_hashes(path=source_path,
                                          root=source_root)

    def render_template_file(self, *, path, root):
        base_path = os.path.relpath(path, root)
        target_path = os.path.join(self.target_dir, base_path)

        _ensure_path(target_path)

        LOG.debug('Templating "%s" into "%s"', path, target_path)

        env = jinja2.Environment(undefined=jinja2.StrictUndefined)

        with open(path) as f:
            template = env.from_string(f.read())
        rendered_data = template.render(config=self.config)

        with open(target_path, 'w') as f:
            f.write(rendered_data)

        LOG.info('Installed "%s"', os.path.join('/', base_path))

#Generate SHA256 Hases of all the files for host validation
    def generate_sha_hashes(self, *, path, root):
        base_path = os.path.relpath(path, root)
        target_path = os.path.join(self.target_dir, base_path)
        log_path = "var/log/promenade/"
        target_log_path = os.path.join(self.target_dir, log_path)
        log_file = os.path.join(target_log_path, "promenade_file_hash.log")
        if not os.path.exists(target_log_path):
            LOG.info('Creating "%s"', target_log_path)
            os.mkdir(target_log_path)
        else:
            LOG.info('Skipping creation of "%s" because it already exists', target_log_path)
#Generate Hashes and Write to file
        hash_sums = {}
        hash = hashlib.sha256(open(path,'rb').read()).hexdigest()
        hash_sums[base_path] = hash
        LOG.info('File Hash:  "%s" into "%s"', hash_sums, target_path)
        #TODO: Test without changing directory
        os.chdir(target_log_path)
        file_out = open(log_file, "a")
        for key,value in hash_sums.items():
            output = key + ": " + value
            file_out.write(output + "\n")
        file_out.close()


def _ensure_path(path):
    base = os.path.dirname(path)
    os.makedirs(base, mode=0o775, exist_ok=True)
