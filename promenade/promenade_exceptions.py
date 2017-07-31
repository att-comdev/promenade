from . import logging


LOG = logging.getLogger(__name__)


class PromenadeBaseException(Exception):
    '''
    Base exception that all Promenade exceptions inherit
    '''

    def __init__(self, exception, message):
        self.message = message or self.message
        self._exception = exception
 
        super(PromenadeBaseException, self).__init__(self.message)


class GeneratorException(PromenadeBaseException):
    '''
    A top-level exception for errors occurring in the generator
    '''
 
    def  __init__(self, output_dir):
        self._message = 'An error occurred generating to output directory \
        {}'.format(outout_dir)

        super(GeneratorException, self).__init__(self.message) 


class OperatorException(PromenadeBaseException):
    '''
    A top-level exception for errors occuring in the Operator
    '''

    def __init__(self, message):
        super(OperatorException, self).__init__(message)

class RendererException(PromenadeBaseException):
    '''
    A top-level exeption for errors occurring in the Template
    Renderer
    '''

    message = 'An error occurred while rendering the template.'


class ValidationException(PromenadeBaseException):
    '''
    A top-level exception for validation errors
    '''

    def __init__(self):
        self._message = 'An unknown validation error occurred.'
        super(ValidationException, self).__init__(self._message)


class AssetSyncException(OperatorException):
    '''
    Error that occurs when there is an error syncing assets from the asset
    directory. 
    '''

    def __init__(self, asset_dir, target_dir):
        self._message = 'Error syncing assets from {} to target directory {}.'.format(
                        asset_dir, target_dir)

        super(AssetSyncException, self).__init__(self._message)


class BootstrapException(OperatorException):
    '''
    Error that occurs when there is an error running the genesis script during
    the bootstrapping process.
    '''

    def __init__(self, target_dir):
        self._message = 'Failed to run genesis script {}.'.format(target_dir)

        super(BootstrapException, self).__init__(self._message) 


class ClusterNameMismatchException(ValidationException):
    '''
    Exception that occurs when the Cluster name in the Cluster config 
    does not match the value of the Cluster name in the Network config.
    '''

    def __init__(self, cluster_name, network_name):
        self._message = 'Cluster name {} in Cluster config does not match \
                        cluster name {} in Network config.'.format(
                        cluster_name, network_name)

        super(ClusterNameMistmatchException, self).__init__(self._message) 


class MalformedCAConfigException(PKIException):
    '''
    Exception occurs when a malformed ca config is encountered.
    '''

    def __init__(self, ca_config):
        self._message = 'CA config {} is malformed'.format(ca_config)

        super(MalformedCAConfigException, self).__init__(self._message)


class MissingDocumentException(ValidationException):
    ''' 
    Exception occurs when one of the required documents required for the 
    generator is missing 
    '''

    def __init__(self, doc_type):
        self._message = 'Generator requires one {} document to \
                        function.'.format(doc_type)

        super(MissingDocumentException, doc_type).__init__(self._message)


class RenderTemplateDirException(RendererException):
    '''
    Exception that occurs when there is an error rendering the template
    directory.
    '''

    def __init__(self, template_dir):
        self._message = 'There was an error rendering the template directory \
                        {}'.format(template_dir)

        super(RenderTemplateDirException, self).__init__(self._message)


class TemplateLoadException(RendererException):
    '''
    Exception that occurs when there is an error loading the provided template
    '''

    def __init__(self, template):
        self._message = 'Unable to load template {}'.format(template)

        super(TemplateLoadException, self).__init__(self._message)


class TemplateSaveException(RendererException):
    '''
    Exception that occurs when there is an error saving a template to the 
    provided location
    '''

    def __init__(self, template):
        self._mesage = 'Unable to save template to {}'.format(template)

        super(TemplateSaveException, self).__init__(self._message)
