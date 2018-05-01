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

from promenade import exceptions, logging
from boltons.iterutils import remap
import abc

LOG = logging.getLogger(__name__)


class IEventSource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def stream_events(self):
        pass


class KubernetesEventSource(IEventSource):
    GROUP = 'promenade.airshipit.org'
    VERSION = 'v1'
    PLURAL = 'node-configurations'

    def __init__(self, *, hostname, kube_wrapper):
        self.hostname = hostname
        self.kube_wrapper = kube_wrapper

    def stream_events(self):
        self.kube_wrapper.wait_for_crds(
            [self.GROUP + '/' + self.VERSION + ':' + self.PLURAL])

        LOG.info('Monitoring events')
        for event in self.kube_wrapper.stream_custom_objects(
                self.GROUP, self.VERSION, self.PLURAL):
            loggable_event = _clean_event(event)
            LOG.debug('Got event: %s', loggable_event)

            _validate_event(event)
            if self._passes_filter(loggable_event):
                yield loggable_event['raw_object']

    def _passes_filter(self, loggable_event):
        if self._is_local(loggable_event):
            if loggable_event['type'] in {'ADDED', 'MODIFIED'}:
                LOG.debug('Got %s event for node %s.', loggable_event['type'],
                          self.hostname)
                return True
            elif loggable_event['type'] == 'DELETED':
                LOG.warn('Got delete event for node %s: %s', self.hostname,
                         loggable_event)
                return False
        else:
            return False

    def _is_local(self, loggable_event):
        event_hostname = loggable_event['raw_object'].get('metadata',
                                                          {}).get('name')
        if event_hostname:
            return event_hostname == self.hostname
        else:
            LOG.warn('Got event without hostname: %s', loggable_event)
            return False


def _clean_event(event):
    return {
        'type':
        event.get('type', 'UNKNOWN_TYPE').upper(),
        'raw_object':
        remap(
            event.get('raw_object', {}),
            visit=lambda _p, _k, v: v is not None and v != ''),
    }


EXPECTED_TYPES = {
    'ADDED',
    'DELETED',
    'MODIFIED',
}


def _validate_event(event):
    type_ = event.get('type', '').upper()
    if type_ == 'ERROR':
        LOG.error('Got an error event from the Kubernetes API: %s', event)
        raise exceptions.KubernetesErrorEvent()
    elif type_ not in EXPECTED_TYPES:
        LOG.error('Got unexpected event from Kubernets API: %s', event)
        raise exceptions.KubernetesUnexpectedEvent()
