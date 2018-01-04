from . import exceptions, logging, validation
from deckhand.engine import layering
import copy
import jinja2
import jsonpath_ng
import requests
import yaml

__all__ = ['Configuration']

LOG = logging.getLogger(__name__)


class Configuration:
    def __init__(self, *, documents, debug=False, substitute=True):
        if substitute:
            documents = _render(documents)
        self.debug = debug
        self.documents = documents

    @classmethod
    def from_streams(cls, *, streams, **kwargs):
        documents = []
        for stream in streams:
            stream_name = getattr(stream, 'name')
            if stream_name is not None:
                LOG.info('Loading documents from %s', stream_name)
            stream_documents = list(yaml.safe_load_all(stream))
            validation.check_schemas(stream_documents)
            if stream_name is not None:
                LOG.info('Successfully validated documents from %s',
                         stream_name)
            documents.extend(stream_documents)

        rendered_documents = _render(documents)
        return cls(documents=rendered_documents, **kwargs)

    @classmethod
    def from_design_ref(cls, design_ref):
        response = requests.get(design_ref)
        response.raise_for_status()

        documents = list(yaml.safe_load_all(response.text))
        validation.check_schemas(documents)

        return cls(documents=documents)

    def __getitem__(self, path):
        value = self.get_path(path)
        if value:
            return value
        else:
            return jinja2.StrictUndefined('No match found for path %s' % path)

    def get_first(self, *paths):
        result = self._get_first(*paths)
        if result:
            return result
        else:
            return jinja2.StrictUndefined(
                'Nothing found matching paths: %s' % ','.join(paths))

    def get(self, *, kind=None, name=None, schema=None):
        result = _get(self.documents, kind=kind, schema=schema, name=name)

        if result:
            return result['data']
        else:
            return jinja2.StrictUndefined(
                'No document found matching kind=%s schema=%s name=%s' %
                (kind, schema, name))

    def iterate(self, *, kind=None, schema=None, labels=None):
        if kind is not None:
            if schema is not None:
                raise AssertionError(
                    'Logic error: specified both kind and schema')
            schema = 'promenade/%s/v1' % kind

        for document in self.documents:
            if _matches_filter(document, schema=schema, labels=labels):
                yield document

    def extract_genesis_config(self):
        LOG.debug('Extracting genesis config.')
        documents = []
        for document in self.documents:
            if document['schema'] != 'promenade/KubernetesNode/v1':
                documents.append(document)
            else:
                LOG.debug('Excluding schema=%s metadata.name=%s',
                          document['schema'], _mg(document, 'name'))
        return Configuration(
            debug=self.debug, documents=documents, substitute=False)

    def extract_node_config(self, name):
        LOG.debug('Extracting node config for %s.', name)
        documents = []
        for document in self.documents:
            schema = document['schema']
            if schema == 'promenade/Genesis/v1':
                LOG.debug('Excluding schema=%s metadata.name=%s', schema,
                          _mg(document, 'name'))
                continue
            elif schema == 'promenade/KubernetesNode/v1' and _mg(
                    document, 'name') != name:
                LOG.debug('Excluding schema=%s metadata.name=%s', schema,
                          _mg(document, 'name'))
                continue
            else:
                documents.append(document)
        return Configuration(
            debug=self.debug, documents=documents, substitute=False)

    @property
    def kubelet_name(self):
        for document in self.iterate(kind='Genesis'):
            return 'genesis'

        for document in self.iterate(kind='KubernetesNode'):
            return document['data']['hostname']

        return jinja2.StrictUndefined(
            'No Genesis or KubernetesNode found while getting kubelet name')

    def _get_first(self, *paths):
        for path in paths:
            value = self.get_path(path)
            if value:
                return value

    def get_path(self, path, default=None):
        kind, jsonpath = path.split(':')
        document = _get(self.documents, kind=kind)
        if document:
            data = _extract(document['data'], jsonpath)
            if data:
                return data
        return default

    def append(self, item):
        validation.check_schema(item)
        self.documents.append(item)


def _matches_filter(document, *, schema, labels):
    matches = True
    if schema is not None and not document.get('schema',
                                               '').startswith(schema):
        matches = False

    if labels is not None:
        document_labels = _mg(document, 'labels', [])
        for key, value in labels.items():
            if key not in document_labels:
                matches = False
            else:
                if document_labels[key] != value:
                    matches = False

    return matches


def _get(documents, kind=None, schema=None, name=None):
    if kind is not None:
        if schema is not None:
            msg = "Only kind or schema may be specified, not both"
            raise exceptions.ValidationException(msg)
        schema = 'promenade/%s/v1' % kind

    for document in documents:
        if (schema == document.get('schema')
                and (name is None or name == _mg(document, 'name'))):
            return document

def _render(all_documents):
    layering_policy = None

    input_documents = []
    for document in all_documents:
        if document.get('schema') == 'deckhand/LayeringPolicy/v1':
            layering_policy = document
        else:
            input_documents.append(document)

    if layering_policy is None:
        raise exceptions.ValidationException('No layering policy specified')

    dh_engine = layering.DocumentLayering(layering_policy, all_documents)
    rendered_documents = dh_engine.render()
    rendered_documents.append(layering_policy)

    for document in rendered_documents:
        if (document.get('schema') == 'armada/Chart/v1'
            and _mg(document, 'name') == 'kubernetes-proxy'):
            LOG.warn('KP: %s', document)
    return rendered_documents


def _extract(document, jsonpath):
    p = jsonpath_ng.parse(jsonpath)
    matches = p.find(document)
    if matches:
        return matches[0].value


def _mg(document, field, default=None):
    return document.get('metadata', {}).get(field, default)
