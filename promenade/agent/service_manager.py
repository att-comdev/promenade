# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
from promenade import exceptions, logging
from pystemd import systemd1

LOG = logging.getLogger(__name__)


class IServiceManager(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_status(self, service_name):
        pass

    @abc.abstractmethod
    def set_up(self, service_name):
        pass

    @abc.abstractmethod
    def set_down(self, service_name):
        pass


class SystemdServiceManager(IServiceManager):
    def get_status(self, service_name):
        LOG.debug('Getting status for %s', service_name)
        unit = _load_unit(service_name, raise_errors=False)
        return _extract_properties(unit)

    def set_up(self, service_name):
        LOG.debug('Setting service %s up', service_name)
        unit = _load_unit(service_name, raise_errors=True)
        unit.Unit.Start(b'replace')
        LOG.info('Service %s set to up', service_name)

    def set_down(self, service_name):
        LOG.debug('Setting service %s down', service_name)
        unit = _load_unit(service_name, raise_errors=True)
        unit.Unit.Stop(b'replace')
        LOG.info('Service %s set to down', service_name)


def _load_unit(service_name, *, raise_errors):
    unit = systemd1.Unit(service_name + '.service')
    unit.load()

    if raise_errors:
        if unit.Unit.LoadState != b'loaded':
            raise exceptions.SystemdMissingUnit('Missing unit',
                                                '%s.service' % service_name)

    return unit


def _extract_properties(unit):
    result = {
        'messages': [],
    }
    result['state'] = unit.Unit.ActiveState.decode('utf-8')
    if unit.Unit.LoadState != b'loaded':
        error_type, error_message = unit.Unit.LoadError
        result['messages'].append('%s: %s' % (error_type.decode('utf-8'),
                                              error_message.decode('utf-8')))

    return result
