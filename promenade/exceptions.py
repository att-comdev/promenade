import logging

LOG = logging.getLogger(__name__)


class PromenadeException(Exception):
    def __init__(self, message):
        self.message = message

    def display(self):
        LOG.error(self.message)

class ValidationException(PromenadeException):
    pass
